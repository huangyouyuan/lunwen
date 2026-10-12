"""Table-first descriptive comparisons using saved full-reference-patch counts.

No training, inference, distance generation, figure export or manuscript edit.
Run from any directory: python -B scripts/analyze_spatial_error_conditions.py
All outputs belong to results/{processed,summary}/spatial_error_conditions/.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from sec33_metrics import CLASSES, CM_COLS, RUN, SITES, SITE_LABELS, five_stats

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results/processed/sec33_reference_patch_types"
PROC = ROOT / "results/processed/spatial_error_conditions"
SUM = ROOT / "results/summary/spatial_error_conditions"
AREA = ["<10", "10-<50", "50-<100", "100-<200", "200-<500", ">=500"]
SHAPE = ["1-<1.5", "1.5-<2", "2-<3", ">=3"]
ENN = ["60-<90", "90-<120", "120-<180", ">=180"]
DIST = ["0<d<=1", "1<d<=6", "d>6"]
BANDS = ["0<d<=1", "1<d<=2", "2<d<=3", "3<d<=4", "4<d<=5", "5<d<=6", "d>6"]
GROUPKEY = ["target", "crop", "scheme", "group"]
CHECKS, INPUTS = [], {}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def record(path):
    INPUTS[path.relative_to(ROOT).as_posix()] = sha(path)


def read(path):
    record(path)
    return pd.read_csv(path, float_precision="round_trip")


def check(name, condition, detail=""):
    ok = bool(condition)
    CHECKS.append(dict(check=name, status="Verified" if ok else "Not verified", detail=str(detail)))
    if not ok:
        raise ValueError(f"{name}: {detail}")


def save(frame, name, processed=False):
    d = PROC if processed else SUM
    d.mkdir(parents=True, exist_ok=True)
    frame.to_csv(d / (name + ".csv"), index=False, float_format="%.17g", lineterminator="\n")


def ratio(n, d):
    n, d = np.broadcast_arrays(np.asarray(n, float), np.asarray(d, float))
    return np.divide(n, d, out=np.full(n.shape, np.nan), where=d != 0)


def compare(a, b, keys, fields, name, integer=False):
    a, b = a.set_index(keys).sort_index(), b.set_index(keys).sort_index()
    check(name + " identities", a.index.is_unique and b.index.is_unique and a.index.equals(b.index))
    check(name + " values", np.array_equal(a[fields].values, b[fields].values) if integer else
          np.allclose(a[fields], b[fields], rtol=0, atol=1e-12, equal_nan=True))


def specs():
    """Disjoint partitions within each scheme; indices address the fine cube."""
    any_ = slice(None)
    out = [("all", "all", (any_, any_, any_, any_))]
    for scheme, labels, axis in [("area", AREA, 0), ("shape", SHAPE, 1), ("enn", ENN, 2)]:
        for i, label in enumerate(labels):
            idx = [any_] * 4
            idx[axis] = slice(i, i + 1)
            out.append((scheme, label, tuple(idx)))
    for a, s in itertools.product(range(6), range(4)):
        idx = (slice(a, a + 1), slice(s, s + 1), any_, any_)
        out.append(("area_shape", f"{AREA[a]}|{SHAPE[s]}", idx))
        for e in range(4):
            out.append(("area_shape_enn", f"{AREA[a]}|{SHAPE[s]}|{ENN[e]}",
                        idx[:2] + (slice(e, e + 1), any_)))
        for d, bs in enumerate((slice(0, 1), slice(1, 6), slice(6, 7))):
            out.append(("area_shape_distance", f"{AREA[a]}|{SHAPE[s]}|{DIST[d]}", idx[:3] + (bs,)))
    for b, label in enumerate(BANDS):
        out.append(("distance", label, (any_, any_, any_, slice(b, b + 1))))
    return out


SPECS = specs()


def make_cube(code, counts):
    cube = np.zeros((96, 7, 3), np.int64)
    np.add.at(cube, code, counts)
    return cube.reshape(6, 4, 4, 7, 3)


def grouped(cube):
    return np.stack([cube[idx].sum(axis=(0, 1, 2, 3)) for _, _, idx in SPECS])


def group_support(f, band_pixels):
    rows = []
    for scheme, group, idx in SPECS:
        mask = np.ones(len(f), bool)
        for column, sel in zip(["a", "s", "e"], idx[:3]):
            if sel.start is not None:
                mask &= f[column].eq(sel.start).values
        n = band_pixels[:, idx[3]].sum(axis=1)
        supported = mask & (n > 0)
        pixels = int(n[mask].sum())
        rows.append(dict(scheme=scheme, group=group, patch_count=int(supported.sum()),
                         reference_pixels=pixels, area_ha=pixels * .09,
                         area_share=float(pixels / f.reference_pixels.sum()),
                         singleton_patch_count=int((supported & f.reference_pixels.eq(1)).sum()),
                         outer_edge_patch_count=int((supported & f.touches_outer_edge).sum()),
                         outer_edge_pixels=int(n[supported & f.touches_outer_edge].sum())))
    return pd.DataFrame(rows)


def contrast_arrays(f, nband, counts, name):
    """Return two arms x strata integer n, FN, patch support. No error-based selection."""
    tc = 0 if f.crop.iloc[0] == "corn" else 2
    errband = counts.sum(axis=2) - counts[:, :, tc]
    if name.startswith("area_"):
        arm, strata = (f.a >= 2).to_numpy(), f.s.to_numpy()
    elif name.startswith("shape_"):
        arm, strata = (f.s >= 2).to_numpy(), f.a.to_numpy()
    else:
        arm, strata = (f.e >= 1).to_numpy(), (f.a * 4 + f.s).to_numpy()
    k = 4 if name.startswith("area_") else 6 if name.startswith("shape_") else 24
    use_dist = name.endswith("distance")
    bs = [slice(0, 1), slice(1, 6), slice(6, 7)] if use_dist else [slice(0, 7)]
    out = np.zeros((2, k * len(bs), 3), np.int64)
    for d, sl in enumerate(bs):
        nn, ee = nband[:, sl].sum(axis=1), errband[:, sl].sum(axis=1)
        at = arm.astype(int) * k * len(bs) + strata * len(bs) + d
        for j, val in enumerate([nn, ee, (nn > 0).astype(int)]):
            np.add.at(out[:, :, j].reshape(-1), at, val)
    return out


def contrast_stats(arr, patch_min, pixels_min):
    n, fn, patches = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    eligible = ((n >= pixels_min) & (patches >= patch_min)).all(axis=0)
    q = n / n.sum(axis=1)[:, None]
    weight = np.minimum(q[0], q[1]) * eligible
    weightsum = weight.sum()
    weights = weight / weightsum if weightsum else weight
    rates = ratio(fn, n)
    low = float(np.sum(weights[eligible] * rates[0, eligible])) if weightsum else np.nan
    high = float(np.sum(weights[eligible] * rates[1, eligible])) if weightsum else np.nan
    return dict(common_strata=int(eligible.sum()), total_strata=n.shape[1], overlap_mass=weightsum,
                low_pixels=int(n[0].sum()), high_pixels=int(n[1].sum()),
                low_coverage=float(n[0, eligible].sum() / n[0].sum()),
                high_coverage=float(n[1, eligible].sum() / n[1].sum()),
                low_excluded_pixels=int(n[0, ~eligible].sum()), high_excluded_pixels=int(n[1, ~eligible].sum()),
                low_raw_rate=float(fn[0].sum()/n[0].sum()), high_raw_rate=float(fn[1].sum()/n[1].sum()),
                low_standard_rate=low, high_standard_rate=high, contrast=high-low)


CONTRASTS = ["area_control_shape", "area_control_shape_distance", "shape_control_area", "shape_control_area_distance",
             "enn_control_area_shape", "enn_control_area_shape_distance"]


def summarize(frame, keys, values):
    rows = []
    for key, g in frame.groupby(keys, sort=True, dropna=False):
        check_fold = len(g) == 5 and set(g.fold) == {1, 2, 3, 4, 5}
        if not check_fold:
            raise ValueError(f"Incomplete five predictions: {key}")
        row = dict(zip(keys, key)) | {"n_predictions": 5}
        for col in values:
            row.update(five_stats(g[col], col))
        rows.append(row)
    return pd.DataFrame(rows)


def whole_tables(cm, metrics, directions):
    """Reuse audited whole-site metrics/directions; add transparent reading columns."""
    m = metrics.copy()
    m["fn_loss"] = m.fn / m.f1_denominator
    m["fp_loss"] = m.fp / m.f1_denominator
    w = m[m.kind.eq("within")][["model", "target", "crop", "fn", "fp", "fn_loss", "fp_loss"]]
    m = m.merge(w.rename(columns={c: "baseline_"+c for c in ["fn", "fp", "fn_loss", "fp_loss"]}),
                on=["model", "target", "crop"], validate="many_to_one")
    for col in ["fn", "fp", "fn_loss", "fp_loss"]:
        m["delta_"+col] = m[col] - m["baseline_"+col]
    m["site"] = m.target.map(SITE_LABELS)
    m["source_site"] = m.source.map(SITE_LABELS)
    check("F1 loss components close for all three classes", np.allclose(m.delta_fn_loss + m.delta_fp_loss, m.delta_f1, atol=1e-14))
    save(m, "whole_crop_per_prediction", True)
    save(m[m.kind.eq("within")], "within_whole_crop")
    vals = ["f1", "delta_f1", "precision", "recall", "delta_precision", "delta_recall", "fn", "fp",
            "delta_fn", "delta_fp", "delta_fn_loss", "delta_fp_loss"]
    summary = summarize(m[m.kind.eq("cross")], ["model", "source", "target", "crop"], vals)
    save(summary, "cross_whole_crop")
    d = directions.copy()
    d["site"] = d.target.map(SITE_LABELS)
    d["source_site"] = d.source.map(SITE_LABELS)
    d["count_rank"] = d.groupby(RUN).errors.rank(method="min", ascending=False).astype(int)
    d["delta_count_rank"] = d.groupby(RUN).delta_errors.rank(method="min", ascending=False).astype(int)
    d["site_error_share"] = d.errors / d.groupby(RUN).errors.transform("sum")
    d["net_error_share"] = ratio(d.delta_errors, d.groupby(RUN).delta_errors.transform("sum"))
    save(d, "six_directions_per_prediction", True)
    save(d[d.kind.eq("within")], "within_six_directions")
    ds = summarize(d[d.kind.eq("cross")], ["model", "source", "target", "true_class", "predicted_class", "direction"],
                   ["errors", "rate", "delta_errors", "delta_rate", "site_error_share", "net_error_share"])
    ds["delta_count_rank"] = ds.groupby(["model", "source", "target"]).delta_errors_mean.rank(method="min", ascending=False).astype(int)
    save(ds, "cross_six_directions")
    return m, summary


def location_tables(band_rows):
    """Reuse the already-verified seven-band directional counts, including true other."""
    d=pd.DataFrame(band_rows)
    d["location"]=np.where(d.band.eq(BANDS[0]),DIST[0],np.where(d.band.eq(BANDS[6]),DIST[2],DIST[1]))
    keys=RUN+["true_class","predicted_class","location"]
    d=d.groupby(keys,as_index=False)[["pixels","errors"]].sum()
    bk=["model","target","true_class","predicted_class","location"]
    base=d[d.kind.eq("within")][bk+["errors"]].rename(columns={"errors":"within_errors"})
    d=d.merge(base,on=bk,validate="many_to_one")
    d["delta_errors"]=d.errors-d.within_errors
    d["rate"]=ratio(d.errors,d.pixels)
    d["within_rate"]=ratio(d.within_errors,d.pixels)
    d["delta_rate"]=d.rate-d.within_rate
    k=RUN+["true_class","predicted_class"]
    n=d.groupby(k).pixels.transform("sum")
    d["reference_share"]=d.pixels/n
    d["direction_contribution"]=d.errors/n
    d["net_direction_contribution"]=d.delta_errors/n
    save(d,"direction_location_per_prediction",True)
    save(d[d.kind.eq("within")],"within_direction_location")
    s=summarize(d[d.kind.eq("cross")],["model","source","target","true_class","predicted_class","location"],
                ["errors","delta_errors","rate","delta_rate","net_direction_contribution"])
    save(s,"cross_direction_location")


def reading_tables(groups, contrasts, within_whole, cross_whole):
    """Small, purpose-specific tables for report review; no new input statistics."""
    rows=[]
    subsets={"area_lt10":("area",["<10"]),"area_lt50":("area",AREA[:2]),
             "area_ge50":("area",AREA[2:]),"enn_ge90":("enn",ENN[1:]),
             "nearest":("distance",BANDS[:1]),"interior_gt1":("distance",BANDS[1:]),
             "far_gt6":("distance",BANDS[6:])}
    for name,(scheme,labels) in subsets.items():
        g=groups[groups.scheme.eq(scheme)&groups.group.isin(labels)]
        a=g.groupby(RUN+["crop"],as_index=False)[["reference_pixels","area_share","fn","within_fn","delta_fn"]].sum()
        b=groups[groups.scheme.eq("all")][RUN+["crop","fn","within_fn","reference_pixels"]].rename(columns={"fn":"whole_fn","within_fn":"whole_within_fn","reference_pixels":"whole_pixels"})
        a=a.merge(b,on=RUN+["crop"],validate="one_to_one")
        a["subset"]=name
        a["omission_rate"]=ratio(a.fn,a.reference_pixels)
        a["within_omission_rate"]=ratio(a.within_fn,a.reference_pixels)
        a["delta_omission_rate"]=a.omission_rate-a.within_omission_rate
        a["error_share"]=ratio(a.fn,a.whole_fn)
        a["net_contribution"]=a.delta_fn/a.whole_pixels
        rows.append(a)
    r=pd.concat(rows,ignore_index=True)
    save(r[r.kind.eq("within")],"reading_within_spatial_subsets")
    s=summarize(r[r.kind.eq("cross")],["model","source","target","crop","subset"],
                ["fn","delta_fn","omission_rate","delta_omission_rate","net_contribution"])
    whole=cross_whole[["model","source","target","crop","delta_fn_mean"]].rename(columns={"delta_fn_mean":"whole_delta_fn_mean"})
    s=s.merge(whole,on=["model","source","target","crop"],validate="many_to_one")
    s["ratio_of_mean_net_counts"]=ratio(s.delta_fn_mean,s.whole_delta_fn_mean)
    s["total_net_sign"]=np.sign(s.whole_delta_fn_mean).astype(int)
    save(s,"reading_cross_spatial_subsets")
    vals=["f1_mean","delta_f1_mean","delta_fn_mean","delta_fp_mean","delta_fn_loss_mean","delta_fp_loss_mean"]
    target=cross_whole[cross_whole.crop.ne("other")].groupby(["model","target","crop"],as_index=False)[vals].mean()
    target["n_sources"]=3
    save(target,"reading_target_cross_means")
    c=contrasts[contrasts.kind.eq("cross")]
    ss=summarize(c,["model","source","target","crop","contrast_name","rule"],["contrast","delta_contrast"])
    agg=[]
    for key,g in ss.groupby(["contrast_name","rule","crop"]):
        w=contrasts[(contrasts.kind=="within")&(contrasts.contrast_name==key[0])&(contrasts.rule==key[1])&(contrasts.crop==key[2])]
        agg.append(dict(zip(["contrast_name","rule","crop"],key))|dict(within_n=len(w),within_positive=int(w.contrast.gt(0).sum()),
            within_min=w.contrast.min(),within_max=w.contrast.max(),cross_n=len(g),
            cross_delta_positive_mean=int(g.delta_contrast_mean.gt(0).sum()),
            cross_delta_all5positive=int(g.delta_contrast_positive.eq(5).sum()),
            cross_delta_all5negative=int(g.delta_contrast_negative.eq(5).sum()),
            cross_delta_min=g.delta_contrast_mean.min(),cross_delta_max=g.delta_contrast_mean.max()))
    save(pd.DataFrame(agg),"reading_condition_consistency")


def site_standardization(groups, support):
    """Four-site common reference cells, equal-site average composition weights."""
    rows, weights_out, decomposition = [], [], []
    for scheme in ["area_shape", "area_shape_distance", "area_shape_enn"]:
        for crop in ["corn", "soybean"]:
            ss = support[(support.scheme == scheme) & (support.crop == crop)]
            ns = ss.pivot(index="group", columns="target", values="reference_pixels").reindex(columns=SITES)
            ps = ss.pivot(index="group", columns="target", values="patch_count").reindex(columns=SITES)
            for rule, pm, nm in [("primary", 10, 1000), ("all_supported", 1, 1)]:
                valid = ((ns >= nm) & (ps >= pm)).all(axis=1)
                selected = ns.loc[valid]
                q = selected / selected.sum(axis=0)
                weights = q.mean(axis=1)
                check(f"site common weights {scheme} {crop} {rule}", len(weights) > 0 and abs(weights.sum()-1) < 1e-12)
                for cell in ns.index:
                    for target in SITES:
                        weights_out.append(dict(scheme=scheme, crop=crop, rule=rule, group=cell, target=target,
                            reference_pixels=int(ns.loc[cell, target]), patch_count=int(ps.loc[cell, target]),
                            eligible=bool(valid.loc[cell]), common_weight=float(weights.get(cell, 0)),
                            site_retained_weight=float(q.loc[cell,target]) if valid.loc[cell] else 0))
                gg = groups[(groups.scheme == scheme) & (groups.crop == crop)]
                rates_by_run = {}
                for key, g in gg.groupby(RUN):
                    g = g.set_index("group")
                    target = key[3]
                    rates = g.loc[weights.index, "omission_rate"]
                    total = ns[target].sum()
                    retained = selected[target].sum()
                    row = dict(zip(RUN, key)) | dict(scheme=scheme, crop=crop, rule=rule,
                        common_cells=int(valid.sum()), total_cells=len(valid),
                        coverage=retained/total, excluded_pixels=int(total-retained),
                        raw_rate=float(g.fn.sum()/total),
                        retained_native_rate=float((q[target] * rates).sum()),
                        standardized_rate=float((weights * rates).sum()))
                    rows.append(row)
                    if key[0] == "within":
                        rates_by_run[(key[1], target)] = rates
                for model in ["convgru", "unet3d", "utae"]:
                    for t1, t2 in itertools.combinations(SITES, 2):
                        r1, r2 = rates_by_run[(model,t1)], rates_by_run[(model,t2)]
                        q1, q2 = q[t1], q[t2]
                        exposure = ((q2-q1)*(r1+r2)/2).sum()
                        condition_rate = ((r2-r1)*(q1+q2)/2).sum()
                        gap = (q2*r2).sum() - (q1*r1).sum()
                        check(f"two-part identity {scheme} {crop} {rule} {model} {t1} {t2}", abs(gap-exposure-condition_rate)<1e-12)
                        decomposition.append(dict(scheme=scheme,crop=crop,rule=rule,model=model,
                            site1=SITE_LABELS[t1],site2=SITE_LABELS[t2],
                            coverage1=selected[t1].sum()/ns[t1].sum(),coverage2=selected[t2].sum()/ns[t2].sum(),
                            retained_native_gap=gap, composition_component=exposure, condition_rate_component=condition_rate,
                            standardized_gap=float((weights*(r2-r1)).sum())))
    out = pd.DataFrame(rows)
    baseline = out[out.kind.eq("within")][["model","target","crop","scheme","rule","standardized_rate"]].rename(columns={"standardized_rate":"within_standardized_rate"})
    out = out.merge(baseline,on=["model","target","crop","scheme","rule"],validate="many_to_one")
    out["delta_standardized_rate"] = out.standardized_rate-out.within_standardized_rate
    save(out,"site_common_weight_per_prediction",True)
    save(out[out.kind.eq("within")],"within_site_common_weights")
    save(summarize(out[out.kind.eq("cross")],["model","source","target","crop","scheme","rule"],
                   ["standardized_rate","delta_standardized_rate"]),"cross_site_common_weights")
    save(pd.DataFrame(weights_out),"site_common_support_weights")
    save(pd.DataFrame(decomposition),"within_site_gap_decomposition")


def main():
    features = read(INPUT / "reference_patch_features.csv")
    index = read(INPUT / "prediction_count_index.csv")
    cm = read(ROOT / "results/processed/sec33_crop_spatial_context/whole_cm.csv")
    old = ROOT / "results/processed/sec33_directional_confusion_closeout"
    metrics = read(old / "crop_metrics_per_prediction.csv")
    directions = read(old / "directional_per_prediction.csv")
    band_old = read(ROOT / "results/processed/sec33_directional_confusion/distance_direction_per_prediction.csv")
    formal_w = read(ROOT / "results/summary/f1_raw_scale/within_site_crop_f1.csv")
    formal_c = read(ROOT / "results/summary/f1_raw_scale/cross_site_crop_f1_per_fold.csv")
    formal_diff = read(ROOT / "results/summary/f1_raw_scale/crop_f1_difference_36paths.csv")
    foundation = read(ROOT / "results/summary/sec13_sec31_foundations/within_site_crop_metrics.csv")
    # Background is not copied to patches; retain source hashes and a compact eight-group table.
    background = read(ROOT / "results/summary/sec13_sec31_foundations/class_background_full_scope.csv")
    composition = read(ROOT / "results/summary/sec13_sec31_foundations/reference_composition.csv")
    landscape = read(ROOT / "results/summary/sec13_sec31_foundations/landscape_background_full_scope.csv")
    check("unique target PID", not features.duplicated(["target","PID"]).any())
    check("site mapping", features.site.eq(features.target.map(SITE_LABELS)).all())
    check("features valid and complete", features.feature_status.eq("valid").all() and
          np.isfinite(features[["AREA","SHAPE","ENN"]]).all().all())
    check("AREA ha equals 0.09 * pixels", np.allclose(features.AREA, features.reference_pixels*.09,atol=1e-9,rtol=0))
    check("display bins cover all", features.AREA.gt(0).all() and features.SHAPE.ge(1).all() and features.ENN.ge(60).all())
    expected = {(k,m,s,t,f) for m in ["convgru","unet3d","utae"] for t in SITES
                for k,s,f in [("within",t,0)]+[("cross",s,f) for s in SITES if s!=t for f in range(1,6)]}
    check("192 prediction identities", len(index)==192 and set(map(tuple,index[RUN].values))==expected and not index.duplicated(RUN).any())
    check("same run identities as whole CM", set(map(tuple,cm[RUN].values))==expected and not cm.duplicated(RUN).any())
    for crop in ["corn","soybean"]:
        for kind, formal, keys in [("within",formal_w,["model","target"]),("cross",formal_c,["model","source","target","fold"])]:
            a=metrics[(metrics.kind==kind)&(metrics.crop==crop)][keys+["f1"]]
            compare(a,formal.rename(columns={crop+"_f1":"f1"}),keys,["f1"],f"formal {kind} {crop}")
    compare(metrics[metrics.kind.eq("within") & metrics.crop.ne("other")], foundation,
            ["model","target","crop"],["pixels","tp","fn","fp"],"foundation within counts",True)
    for _,r in cm.iterrows():
        mat=r[CM_COLS].to_numpy(np.int64).reshape(3,3)
        mm=metrics
        dd=directions
        for k in RUN:
            mm=mm[mm[k].eq(r[k])]
            dd=dd[dd[k].eq(r[k])]
        check("CM to saved metrics "+str(tuple(r[RUN])),len(mm)==3 and all(
            int(mm[mm.crop.eq(c)].iloc[0].tp)==mat[i,i] and
            int(mm[mm.crop.eq(c)].iloc[0].fn)==mat[i].sum()-mat[i,i] and
            int(mm[mm.crop.eq(c)].iloc[0].fp)==mat[:,i].sum()-mat[i,i] for i,c in enumerate(CLASSES)))
        check("CM to saved directions "+str(tuple(r[RUN])),len(dd)==6 and all(
            int(dd[(dd.true_class==CLASSES[i])&(dd.predicted_class==CLASSES[j])].iloc[0].errors)==mat[i,j]
            for i,j in itertools.permutations(range(3),2)))
    features["a"] = np.searchsorted([10,50,100,200,500],features.AREA,side="right")
    features["s"] = np.searchsorted([1.5,2,3],features.SHAPE,side="right")
    features["e"] = np.searchsorted([90,120,180],features.ENN,side="right")
    group_frames, supports, contrasts, restored, band_rows = [], [], [], [], []
    ref_by_target, condition_support = {}, []
    cm_lookup = cm.set_index(RUN)
    for target in SITES:
        ff = features[features.target.eq(target)].sort_values("PID").copy()
        pid = ff.PID.to_numpy(int)
        for j, run in enumerate(index[index.target.eq(target)].itertuples(index=False)):
            path=INPUT/run.file
            actual=sha(path)
            INPUTS[path.relative_to(ROOT).as_posix()]=actual
            check("count hash "+run.file, actual==run.sha256)
            with np.load(path) as z:
                ids=z["PID"].astype(int)
                lookup=pd.Index(ids).get_indexer(pid)
                check("explicit PID join "+run.file, len(set(ids))==len(ids) and (lookup>=0).all() and len(ids)==len(ff)+1 and 0 in ids)
                raw=z["patch_band_prediction_counts"]
                check("integer nonnegative and empty PID0 "+run.file,
                      np.issubdtype(raw.dtype,np.integer) and (raw>=0).all() and raw[ids==0].sum()==0)
                counts=raw[lookup].astype(np.int64)
            nband=counts.sum(axis=2)
            check("reference pixel support "+run.file,np.array_equal(nband.sum(axis=1),ff.reference_pixels))
            if target not in ref_by_target:
                ref_by_target[target]=nband
                check("saved boundary and far interior "+target,
                      np.array_equal(nband[:,0],ff.boundary_pixels) and np.array_equal(nband[:,6],ff.far_interior_pixels))
            check("invariant reference distance support "+run.file,np.array_equal(nband,ref_by_target[target]))
            runkey={k:getattr(run,k) for k in RUN}
            mat=np.stack([counts[ff.crop.eq(c)].sum(axis=(0,1)) for c in CLASSES])
            saved=cm_lookup.loc[tuple(runkey.values()),CM_COLS].to_numpy(np.int64).reshape(3,3)
            check("whole CM restored "+run.file,np.array_equal(mat,saved))
            restored.append(runkey | dict(zip(CM_COLS,mat.ravel())))
            for tc, crop in enumerate(CLASSES):
                mask=ff.crop.eq(crop).to_numpy()
                cb=counts[mask].sum(axis=0)
                for b in range(7):
                    for pc in range(3):
                        if pc!=tc:
                            band_rows.append(runkey|dict(band=BANDS[b],true_class=crop,predicted_class=CLASSES[pc],
                                                         pixels=int(cb[b].sum()),errors=int(cb[b,pc])))
                if crop=="other":
                    continue
                f=ff[mask]
                cc=counts[mask]
                nn=nband[mask]
                code=(f.a*16+f.s*4+f.e).to_numpy(int)
                cube=make_cube(code,cc)
                vals=grouped(cube)
                if j==0:
                    support=group_support(f,nn)
                    support["target"],support["crop"],support["site"]=target,crop,SITE_LABELS[target]
                    check("group supports match cube "+target+crop,np.array_equal(vals.sum(axis=1),support.reference_pixels))
                    supports.append(support)
                frame=pd.DataFrame({"scheme":[s[0] for s in SPECS],"group":[s[1] for s in SPECS],
                                    "to_corn":vals[:,0],"to_other":vals[:,1],"to_soybean":vals[:,2]})
                for k,v in runkey.items(): frame[k]=v
                frame["crop"]=crop
                frame["fn"]=vals.sum(axis=1)-vals[:,tc]
                frame["to_other_crop"]=vals[:,2 if tc==0 else 0]
                group_frames.append(frame)
                for name in CONTRASTS:
                    arr=contrast_arrays(f,nn,cc,name)
                    for rule,pm,nm in [("primary",10,1000),("all_supported",1,1)]:
                        stats=contrast_stats(arr,pm,nm)
                        contrasts.append(runkey|dict(crop=crop,contrast_name=name,rule=rule)|stats)
                        if j==0:
                            eligible=((arr[:,:,0]>=nm)&(arr[:,:,2]>=pm)).all(axis=0)
                            q=arr[:,:,0]/arr[:,:,0].sum(axis=1)[:,None]
                            ww=np.minimum(q[0],q[1])*eligible
                            if ww.sum(): ww=ww/ww.sum()
                            for cell in range(arr.shape[1]):
                                condition_support.append(dict(target=target,crop=crop,contrast_name=name,rule=rule,stratum=cell,
                                    low_pixels=int(arr[0,cell,0]),high_pixels=int(arr[1,cell,0]),
                                    low_patch_count=int(arr[0,cell,2]),high_patch_count=int(arr[1,cell,2]),
                                    eligible=bool(eligible[cell]),common_weight=float(ww[cell])))
        print(f"Finished {SITE_LABELS[target]}: 48 saved predictions",flush=True)
    compare(pd.DataFrame(band_rows),band_old,RUN+["band","true_class","predicted_class"],["pixels","errors"],"all six directions seven bands",True)
    support=pd.concat(supports,ignore_index=True)
    save(support,"reference_group_support")
    for key,g in support.groupby(["target","crop","scheme"]):
        check("area shares close "+str(key),abs(g.area_share.sum()-1)<1e-12)
        if "distance" not in key[2]:
            check("patch counts close "+str(key),g.patch_count.sum()==len(features[(features.target==key[0])&(features.crop==key[1])]))
    groups=pd.concat(group_frames,ignore_index=True).merge(support,on=GROUPKEY,validate="many_to_one")
    basekeys=["model"]+GROUPKEY
    fields=["fn","to_other","to_other_crop"]
    baseline=groups[groups.kind.eq("within")][basekeys+fields].rename(columns={c:"within_"+c for c in fields})
    groups=groups.merge(baseline,on=basekeys,validate="many_to_one")
    whole=groups[groups.scheme.eq("all")][RUN+["crop","fn","within_fn","reference_pixels"]].rename(columns={
        "fn":"whole_fn","within_fn":"whole_within_fn","reference_pixels":"whole_crop_pixels"})
    groups=groups.merge(whole,on=RUN+["crop"],validate="many_to_one")
    for col,label in [("fn","omission"),("to_other","to_other"),("to_other_crop","to_other_crop")]:
        groups[label+"_rate"]=ratio(groups[col],groups.reference_pixels)
        groups["within_"+label+"_rate"]=ratio(groups["within_"+col],groups.reference_pixels)
        groups["delta_"+label+"_rate"]=groups[label+"_rate"]-groups["within_"+label+"_rate"]
    groups["delta_fn"]=groups.fn-groups.within_fn
    groups["omission_contribution"]=groups.fn/groups.whole_crop_pixels
    groups["within_omission_contribution"]=groups.within_fn/groups.whole_crop_pixels
    groups["net_omission_contribution"]=groups.delta_fn/groups.whole_crop_pixels
    groups["error_share"]=ratio(groups.fn,groups.whole_fn)
    groups["net_error_share"]=ratio(groups.delta_fn,groups.whole_fn-groups.whole_within_fn)
    groups["rate_status"]=np.where(groups.reference_pixels.gt(0),"defined","no_reference_support")
    groups["net_share_status"]=np.where((groups.whole_fn-groups.whole_within_fn).ne(0),"defined_signed_net","zero_net_denominator")
    check("outgoing directions sum FN",np.array_equal(groups.fn,groups.to_other+groups.to_other_crop))
    for col in ["fn","within_fn","delta_fn"]:
        sums=groups.groupby(RUN+["crop","scheme"])[col].sum().unstack("scheme")
        check("all partitions restore "+col, sums.eq(sums["all"],axis=0).all().all())
    save(groups,"group_metrics_per_prediction",True)
    save(groups[groups.kind.eq("within")],"within_group_metrics")
    vals=["fn","delta_fn","omission_rate","to_other_rate","to_other_crop_rate","delta_omission_rate",
          "delta_to_other_rate","delta_to_other_crop_rate","omission_contribution","net_omission_contribution","error_share","net_error_share"]
    gs=summarize(groups[groups.kind.eq("cross")],["model","source"]+GROUPKEY,vals)
    gs=gs.merge(support,on=GROUPKEY,validate="many_to_one")
    save(gs,"cross_group_metrics")
    co=pd.DataFrame(contrasts)
    ck=["model","target","crop","contrast_name","rule"]
    cb=co[co.kind.eq("within")][ck+["contrast"]].rename(columns={"contrast":"within_contrast"})
    co=co.merge(cb,on=ck,validate="many_to_one")
    co["delta_contrast"]=co.contrast-co.within_contrast
    save(co,"conditional_contrasts_per_prediction",True)
    save(co[co.kind.eq("within")],"within_conditional_contrasts")
    cs=summarize(co[co.kind.eq("cross")],["model","source","target","crop","contrast_name","rule"],
                 ["contrast","delta_contrast","low_standard_rate","high_standard_rate"])
    coverage=co[["target","crop","contrast_name","rule","low_coverage","high_coverage","common_strata","total_strata","overlap_mass"]].drop_duplicates()
    cs=cs.merge(coverage,on=["target","crop","contrast_name","rule"],validate="many_to_one")
    save(cs,"cross_conditional_contrasts")
    save(pd.DataFrame(condition_support),"conditional_support_weights")
    whole_m,whole_s=whole_tables(cm,metrics,directions)
    for crop in ["corn","soybean"]:
        sub=whole_s[whole_s.crop.eq(crop)].rename(columns={"delta_f1_mean":crop+"_f1_difference"})
        compare(sub,formal_diff,["model","source","target"],[crop+"_f1_difference"],"formal delta F1 "+crop)
    site_standardization(groups,support)
    location_tables(band_rows)
    reading_tables(groups,co,whole_m,whole_s)
    # Compact background; no patch-level replication of site-level indices.
    bg=composition.merge(background,on=["target","site","crop","pixels"],validate="one_to_one",suffixes=("","_background"))
    save(bg,"site_class_background")
    save(landscape,"site_landscape_background")
    save(pd.DataFrame(CHECKS),"verification_checks")
    config=dict(data_status="derived_exploratory",area_ha=AREA,shape=SHAPE,enn_m=ENN,
                contrast_arms={"area":"high AREA>=50 ha; low AREA<50 ha", "shape":"high SHAPE>=2; low SHAPE<2",
                               "enn":"high ENN>=90 m; low ENN<90 m"},
                primary_support={"patches_per_arm_or_site_per_cell":10,"pixels_per_arm_or_site_per_cell":1000},
                sensitivity_support={"patches":1,"pixels":1},
                contrast_weights="minimum of the two arm-specific full-population pixel shares, normalize over eligible strata",
                site_weights="mean of four site-specific pixel shares normalized within retained cells, equal site weight",
                distance_strata=DIST, no_p_values=True, source_count=192,
                scripts=["scripts/analyze_spatial_error_conditions.py"])
    (SUM/"analysis_config.json").write_text(json.dumps(config,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    generated=list(PROC.glob("*.csv"))+list(SUM.glob("*.csv"))+[SUM/"analysis_config.json"]
    manifest=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
                  inputs=INPUTS,script_sha256=sha(Path(__file__)),outputs={p.relative_to(ROOT).as_posix():sha(p) for p in generated},
                  verification="Verified",scope="saved count identities/hashes, integer CM and band closure, formal F1, grouping and arithmetic; not distance/FRAGSTATS regeneration")
    (SUM/"manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"Saved {len(groups)} group-prediction rows; {len(CHECKS)} checks.",flush=True)


if __name__ == "__main__":
    main()

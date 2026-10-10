#!/usr/bin/env python3
"""Limited closeout: saved integer counts -> exclusive contact groups and metrics.

No historical producer is run, no distances or masks are regenerated, and all
writes are confined to the independent closeout directories.
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

try:
    import explore_sec33_directional_confusion as base
except ModuleNotFoundError:
    from scripts import explore_sec33_directional_confusion as base

ROOT = Path(__file__).resolve().parents[1]
OLD_PROC = ROOT / "results/processed/sec33_directional_confusion"
OLD_SUM = ROOT / "results/summary/sec33_directional_confusion"
PROC = ROOT / "results/processed/sec33_directional_confusion_closeout"
SUM = ROOT / "results/summary/sec33_directional_confusion_closeout"
FIG = ROOT / "figures/exploratory/sec33_directional_confusion_closeout"
RUN, CM_COLS, CLASSES, SITES, MODELS = base.RUN, base.CM_COLS, base.CLASSES, base.SITES, base.MODELS
SITE_LABELS = base.SITE_LABELS
CLASS_LABELS = dict(corn="玉米", other="其他类", soybean="大豆")
MODEL_LABELS = dict(convgru="ConvGRU", unet3d="3D U-Net", utae="U-TAE")
NEAREST = "0<d<=1"
PAIR_BITS = {"corn_other": (1, "corn", "other"), "corn_soybean": (2, "corn", "soybean"),
             "other_soybean": (4, "other", "soybean")}
CONTACTS = {"corn": (("soybean", 2), ("other", 1)),
            "soybean": (("corn", 2), ("other", 4)),
            "other": (("corn", 1), ("soybean", 4))}
GROUPS = ("contact_1_only", "contact_2_only", "mixed", "nearest_no_direct")
CHECKS, INPUTS = [], {}

def require(condition, message):
    if not bool(condition):
        raise ValueError(message)

def check(name, condition, detail=""):
    ok = bool(condition)
    CHECKS.append(dict(check=name, status="Verified" if ok else "Not verified", detail=str(detail)))
    require(ok, f"{name}: {detail}")

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def metadata(path, role="input"):
    p = Path(path).resolve()
    return dict(path=p.as_posix(), sha256=sha256(p), bytes=p.stat().st_size, role=role)

def read(path):
    INPUTS[str(path)] = metadata(path)
    return pd.read_csv(path, float_precision="round_trip")

def save(frame, name, processed=False):
    directory = PROC if processed else SUM
    directory.mkdir(parents=True, exist_ok=True)
    frame.to_csv(directory / (name + ".csv"), index=False, float_format="%.17g", lineterminator="\n")

def ratio(n, d):
    return n / d if d else np.nan

def group_for(true_class, bitmask):
    require(true_class in CONTACTS and int(bitmask) == bitmask and 0 <= bitmask <= 7, "invalid contact identity")
    b1, b2 = CONTACTS[true_class][0][1], CONTACTS[true_class][1][1]
    yes1, yes2 = bool(bitmask & b1), bool(bitmask & b2)
    return "mixed" if yes1 and yes2 else "contact_1_only" if yes1 else "contact_2_only" if yes2 else "nearest_no_direct"

def group_label(tc, group):
    if group == "mixed":
        return "同时接触两种异类（混合边界）"
    if group == "nearest_no_direct":
        return "最近带无四邻域异类直接接触"
    return "仅直接接触" + CLASS_LABELS[CONTACTS[tc][0 if group == "contact_1_only" else 1][0]]

def five_stats(values, prefix):
    result = base.five_stats(values, prefix)
    result[prefix + "_n_na"] = int((~np.isfinite(np.asarray(values, float))).sum())
    result[prefix + "_status"] = "defined" if len(values) == 5 and np.isfinite(values).all() else "incomplete_or_undefined"
    return result

def require_five(x):
    require(len(x) == 5 and set(x.fold) == {1, 2, 3, 4, 5}, "five unique prediction identities required")

def compare(a, b, keys, fields, name, integer=False):
    require(not a.duplicated(keys).any() and not b.duplicated(keys).any(), name + " duplicate keys")
    a, b = a.set_index(keys).sort_index(), b.set_index(keys).sort_index()
    check(name + " identities", a.index.equals(b.index), f"{len(a)} vs {len(b)}")
    aa, bb = a[fields].to_numpy(), b[fields].to_numpy()
    check(name + " values", np.array_equal(aa, bb) if integer else np.allclose(aa, bb, atol=1e-12, rtol=0, equal_nan=True),
          f"{len(a)} rows x {len(fields)} fields")

def load_inputs():
    return {
        "whole_cm": read(ROOT / "results/processed/sec33_crop_spatial_context/whole_cm.csv"),
        "bits": read(OLD_PROC / "boundary_bitmask_band_cm.csv"),
        "old_direction": read(OLD_PROC / "directional_per_prediction.csv"),
        "old_metrics": read(OLD_PROC / "crop_metrics_per_prediction.csv"),
        "old_metric_summary": read(OLD_SUM / "crop_metrics_summary.csv"),
        "direction_summary": read(OLD_SUM / "directional_summary.csv"),
        "distance": read(OLD_PROC / "distance_direction_per_prediction.csv"),
        "distance_summary": read(OLD_SUM / "distance_direction_summary.csv"),
        "overlap": read(OLD_PROC / "boundary_type_direction_per_prediction.csv"),
        "k4": read(OLD_PROC / "k4_c3_c4_type_error_per_prediction.csv"),
        "k4_features": read(OLD_SUM / "k4_c3_c4_feature_support.csv"),
        "f1_within": read(ROOT / "results/summary/f1_raw_scale/within_site_crop_f1.csv"),
        "f1_fold": read(ROOT / "results/summary/f1_raw_scale/cross_site_crop_f1_per_fold.csv"),
        "f1_summary": read(ROOT / "results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv"),
    }

def verify_inputs(t):
    expected = {("within", m, s, s, 0) for m in MODELS for s in SITES}
    expected |= {("cross", m, s, z, k) for m in MODELS for s in SITES for z in SITES if s != z for k in range(1, 6)}
    cm = t["whole_cm"]
    check("12 independent within + 180 cross identities", len(cm) == 192 and set(map(tuple, cm[RUN].to_numpy())) == expected)
    check("unique whole run keys", not cm.duplicated(RUN).any())
    b = t["bits"]
    check("bitmask identity coverage", len(b) == 192 * 7 * 8 and not b.duplicated(RUN + ["band", "bitmask"]).any()
          and set(map(tuple, b[RUN].drop_duplicates().to_numpy())) == expected)
    for _, x in b.groupby(RUN):
        require(set(zip(x.band, x.bitmask)) == set(itertools.product(base.BANDS, range(8))), "missing band/bitmask")
    check("all seven bands and eight bitmasks for every run", True)
    for name, d in [("whole", cm), ("bitmask", b)]:
        a = d[CM_COLS].to_numpy()
        check(name + " nonnegative integer CM", np.isfinite(a).all() and (a >= 0).all() and (a == np.floor(a)).all())
    compare(b.groupby(RUN, as_index=False)[CM_COLS].sum(), cm, RUN, CM_COLS, "seven bands restore whole CM", True)
    for tc in range(3):
        cols = [f"cm_{tc}_{pc}" for pc in range(3)]
        supports = b[RUN + ["band", "bitmask"]].copy()
        supports["n"] = b[cols].sum(axis=1)
        check("same target reference support class " + str(tc),
              supports.groupby(["target", "band", "bitmask"]).n.nunique().eq(1).all())
        relevant = CONTACTS[CLASSES[tc]][0][1] | CONTACTS[CLASSES[tc]][1][1]
        invalid = b.bitmask.astype(int).map(lambda v: bool(v & (7 ^ relevant)))
        check("no unrelated contact bit on true class " + str(tc), b.loc[invalid, cols].to_numpy().sum() == 0)
    check("no direct contacts outside nearest band",
          b.loc[~b.band.eq(NEAREST) & b.bitmask.ne(0), CM_COLS].to_numpy().sum() == 0)
    rows = []
    for r in b.groupby(RUN + ["band"], as_index=False)[CM_COLS].sum().itertuples(index=False):
        m = np.array([getattr(r, c) for c in CM_COLS], np.int64).reshape(3, 3)
        for tc, pc in itertools.permutations(range(3), 2):
            rows.append(dict(zip(RUN + ["band"], [getattr(r, c) for c in RUN + ["band"]])) |
                        dict(true_class=CLASSES[tc], predicted_class=CLASSES[pc], errors=int(m[tc, pc]),
                             pixels=int(m[tc].sum())))
    compare(pd.DataFrame(rows), t["distance"], RUN + ["band", "true_class", "predicted_class"],
            ["errors", "pixels"], "saved distance count linkage", True)

def compute_whole(t):
    cm = t["whole_cm"]
    metrics, directions = [], []
    baseline = {(r.model, r.target): base.matrix(r) for _, r in cm[cm.kind.eq("within")].iterrows()}
    for _, r in cm.iterrows():
        m, w = base.matrix(r), baseline[(r.model, r.target)]
        run = {k: r[k] for k in RUN}
        for tc, crop in enumerate(CLASSES):
            f, p, rec, leak, tp, fn, fp = base.f1_from_matrix(m, tc)
            wf, wp, wr, wl, *_ = base.f1_from_matrix(w, tc)
            denom = 2 * tp + fp + fn
            metrics.append(run | dict(crop=crop, pixels=tp+fn, predicted_pixels=tp+fp, tp=tp, fn=fn, fp=fp,
                f1=f, precision=p, recall=rec, leakage=leak, f1_denominator=denom,
                f1_status="defined" if denom else "undefined_zero_denominator",
                precision_status="defined" if tp+fp else "no_predicted_support",
                recall_status="defined" if tp+fn else "no_true_support",
                within_f1=wf, within_precision=wp, within_recall=wr,
                delta_f1=wf-f, delta_precision=p-wp, delta_recall=rec-wr))
            for pc in range(3):
                if pc == tc:
                    continue
                directions.append(run | dict(true_class=crop, predicted_class=CLASSES[pc],
                    direction=crop+"_to_"+CLASSES[pc], pixels=int(m[tc].sum()), errors=int(m[tc, pc]),
                    within_errors=int(w[tc, pc]), within_rate=ratio(w[tc, pc], w[tc].sum()),
                    rate=ratio(m[tc, pc], m[tc].sum()),
                    delta_rate=ratio(m[tc, pc], m[tc].sum())-ratio(w[tc, pc], w[tc].sum()),
                    delta_errors=int(m[tc, pc]-w[tc, pc]),
                    rate_status="defined" if m[tc].sum() else "no_true_support"))
    metrics, directions = pd.DataFrame(metrics), pd.DataFrame(directions)
    compare(metrics, t["old_metrics"], RUN+["crop"], ["f1", "precision", "recall", "tp", "fn", "fp"], "F1 fix leaves current actual metrics unchanged")
    compare(directions, t["old_direction"], RUN+["true_class", "predicted_class"],
            ["pixels", "errors", "within_errors", "rate", "delta_rate", "delta_errors"], "whole six directions unchanged")
    for crop in CLASSES:
        c = metrics[metrics.crop.eq(crop)]
        d = directions[directions.true_class.eq(crop)].groupby(RUN, as_index=False).errors.sum().rename(columns={"errors":"fn"})
        p = directions[directions.predicted_class.eq(crop)].groupby(RUN, as_index=False).errors.sum().rename(columns={"errors":"fp"})
        compare(c, d, RUN, ["fn"], "FN directed count closure " + crop, True)
        compare(c, p, RUN, ["fp"], "FP directed count closure " + crop, True)
        for kind, auth, keys in [("within", t["f1_within"], ["model","target"]),
                                 ("cross", t["f1_fold"], ["model","source","target","fold"])]:
            compare(c[c.kind.eq(kind)], auth.rename(columns={crop+"_f1":"f1"}), keys, ["f1"], "current F1 " + kind + "/" + crop)
    save(metrics, "crop_metrics_per_prediction", True)
    save(directions, "directional_per_prediction", True)
    rows = []
    for key, x in metrics[metrics.kind.eq("cross")].groupby(["model","source","target","crop"]):
        require_five(x)
        row = dict(zip(["model","source","target","crop"], key))
        for field in ["f1","precision","recall"]:
            row["within_"+field] = float(x["within_"+field].iloc[0])
            row.update(five_stats(x[field], "cross_"+field))
            row.update(five_stats(x["delta_"+field], "delta_"+field))
            row["delta_"+field] = row["delta_"+field+"_mean"]
        rows.append(row)
    paths = pd.DataFrame(rows)
    compare(paths, t["old_metric_summary"], ["model","source","target","crop"],
            ["within_f1","cross_f1_mean","cross_f1_std","delta_f1","delta_precision","delta_recall"], "path metrics unchanged")
    for crop in ("corn","soybean"):
        compare(paths[paths.crop.eq(crop)], t["f1_summary"].rename(columns={crop+"_f1_mean":"cross_f1_mean",crop+"_f1_std":"cross_f1_std"}),
                ["model","source","target"], ["cross_f1_mean","cross_f1_std"], "five F1 mean/std authoritative "+crop)
    valid = np.isfinite(paths.delta_recall) & np.isfinite(paths.delta_precision)
    paths["larger_drop"] = np.where(~valid, "not_calculable", np.where(-paths.delta_recall > -paths.delta_precision, "recall", np.where(-paths.delta_recall < -paths.delta_precision, "precision", "equal")))
    save(paths, "crop_metrics_summary_path_level", True)
    return metrics, paths, directions

def summarize_directions(d, existing):
    keys = ["model", "source", "target", "true_class", "predicted_class"]
    rows = []
    for key, x in d[d.kind.eq("cross")].groupby(keys):
        require_five(x)
        require(x.pixels.nunique() == 1 and x.within_errors.nunique() == 1, "whole directional support/baseline identity")
        row = dict(zip(keys, key)) | dict(site=SITE_LABELS[key[2]], direction=x.direction.iloc[0],
            within_pixels=int(x.pixels.iloc[0]), within_errors=int(x.within_errors.iloc[0]),
            within_rate=float(x.within_rate.iloc[0]), within_delta_rate=0.0, rate_status=x.rate_status.iloc[0],
            n_predictions=5, prediction_ids="1;2;3;4;5")
        for field, dest in [("rate", "cross_rate"), ("delta_rate", "delta_rate"),
                            ("errors", "cross_errors"), ("delta_errors", "delta_errors")]:
            row.update(five_stats(x[field], dest))
        row.update(delta_rate=row["delta_rate_mean"], delta_errors=row["delta_errors_mean"],
                   delta_rate_pp=row["delta_rate_mean"] * 100)
        rows.append(row)
    out = pd.DataFrame(rows)
    numeric = [c for c in existing.select_dtypes(include="number") if c in out and c not in keys]
    compare(out, existing, keys, numeric, "whole directional five-prediction summary unchanged")
    left, right = out.set_index(keys).sort_index(), existing.set_index(keys).sort_index()
    fields = [c for c in existing if c.endswith("_direction")]
    check("whole directional summary sign classifications unchanged", left[fields].equals(right[fields]))
    save(out, "directional_summary")
    return out

def exclusive_counts(bits):
    near = bits[bits.band.eq(NEAREST)]
    rows = []
    mapping = []
    for tc in CLASSES:
        for bit in range(8):
            g = group_for(tc, bit)
            mapping.append(dict(true_class=tc, bitmask=bit, exclusive_boundary_group=g,
                                group_label=group_label(tc,g), contact_1=CONTACTS[tc][0][0],contact_2=CONTACTS[tc][1][0],
                                admissible_bitmask=not bool(bit & (7 ^ (CONTACTS[tc][0][1] | CONTACTS[tc][1][1])))))
    for key, x in near.groupby(RUN, sort=True):
        for tc, name in enumerate(CLASSES):
            for g in GROUPS:
                use = x[x.bitmask.map(lambda bit: group_for(name,int(bit))).eq(g)]
                pred = use[[f"cm_{tc}_{j}" for j in range(3)]].sum().to_numpy(np.int64)
                rows.append(dict(zip(RUN, key)) | dict(band=NEAREST, true_class=name, exclusive_boundary_group=g,
                    group_label=group_label(name,g), reference_pixels=int(pred.sum()),
                    pred_corn=int(pred[0]), pred_other=int(pred[1]), pred_soybean=int(pred[2])))
    return pd.DataFrame(rows), pd.DataFrame(mapping)

def summarize_boundary(d):
    rows = []
    keys = ["model","source","target","band","true_class","predicted_class","exclusive_boundary_group"]
    for key, x in d[d.kind.eq("cross")].groupby(keys):
        require_five(x)
        check("exclusive reference and baseline identity "+"/".join(map(str,key)),
              x.reference_pixels.nunique()==1 and x.within_errors.nunique()==1 and x.within_reference_pixels.eq(x.reference_pixels).all())
        row = dict(zip(keys,key))
        for field in ["group_label","reference_pixels","nearest_reference_pixels","share_of_nearest_class","share_of_full_class","within_errors","within_rate","rate_status"]:
            row[field] = x[field].iloc[0]
        row["within_reference_pixels"] = int(x.reference_pixels.iloc[0])
        row["n_predictions"] = len(x)
        row["prediction_ids"] = "1;2;3;4;5"
        for src, dest in [("errors","cross_errors"),("rate","cross_rate"),("delta_errors","delta_errors"),("delta_rate","delta_rate")]:
            row.update(five_stats(x[src], dest))
        row["delta_rate_pp"] = row["delta_rate_mean"]*100
        rows.append(row)
    return pd.DataFrame(rows)

def build_exclusive(t):
    b = t["bits"]
    grouped, mapping = exclusive_counts(b)
    save(mapping, "boundary_group_mapping")
    save(grouped, "exclusive_boundary_row_counts", True)
    # Small auditable bitmask cell table, nearest band only. Diagonal is a count,
    # never a directed error; no contact labels are propagated into the interior.
    near = b[b.band.eq(NEAREST)].melt(RUN+["band","bitmask"], CM_COLS, "cm_cell","count")
    near["true_class"] = near.cm_cell.str[3].astype(int).map(dict(enumerate(CLASSES)))
    near["predicted_class"] = near.cm_cell.str[5].astype(int).map(dict(enumerate(CLASSES)))
    near["exclusive_boundary_group"] = [group_for(c,int(bit)) for c,bit in zip(near.true_class,near.bitmask)]
    save(near, "exclusive_boundary_per_prediction", True)
    for tc, name in enumerate(CLASSES):
        got = grouped[grouped.true_class.eq(name)].groupby(RUN,as_index=False)[["pred_"+c for c in CLASSES]].sum()
        expected = b[b.band.eq(NEAREST)].groupby(RUN,as_index=False)[[f"cm_{tc}_{j}" for j in range(3)]].sum()
        expected = expected.rename(columns={f"cm_{tc}_{j}":"pred_"+c for j,c in enumerate(CLASSES)})
        compare(got,expected,RUN,["pred_"+c for c in CLASSES],"four mutually exclusive rows restore nearest CM "+name,True)
    check("one class-specific group per bitmask", not mapping.duplicated(["true_class","bitmask"]).any() and len(mapping)==24)
    check("shared exclusive reference support", grouped.groupby(["target","true_class","exclusive_boundary_group"]).reference_pixels.nunique().eq(1).all())

    # Recombine the two relevant exclusive groups for every historical overlap
    # view. For the unrelated pair the required row must be all zero.
    overlap = t["overlap"][t["overlap"].band.eq(NEAREST)]
    restored = []
    for name, (bit,c1,c2) in PAIR_BITS.items():
        for tc in CLASSES:
            groups = [g for g in GROUPS if any(group_for(tc,k)==g and k&bit for k in range(8))] if tc in (c1,c2) else []
            if tc in (c1,c2):
                which = 0 if CONTACTS[tc][0][1]==bit else 1
                groups = [GROUPS[which],"mixed"]
            z = grouped[grouped.true_class.eq(tc) & grouped.exclusive_boundary_group.isin(groups)].groupby(RUN)[["reference_pixels"]+["pred_"+c for c in CLASSES]].sum()
            for run in t["whole_cm"][RUN].itertuples(index=False,name=None):
                vals = z.loc[run] if run in z.index else pd.Series(0,index=["reference_pixels"]+["pred_"+c for c in CLASSES])
                for pc in CLASSES:
                    if pc != tc:
                        restored.append(dict(zip(RUN,run))|dict(boundary_type=name,band=NEAREST,true_class=tc,predicted_class=pc,
                           pixels=int(vals.reference_pixels),errors=int(vals["pred_"+pc]),rate=ratio(vals["pred_"+pc], vals.reference_pixels)))
    restored = pd.DataFrame(restored)
    compare(restored, overlap, RUN+["boundary_type","band","true_class","predicted_class"],["pixels","errors","rate"],"historical overlap recovered from exclusive groups")
    save(restored,"overlap_reconstruction_per_prediction",True)
    baseline = grouped[grouped.kind.eq("within")].set_index(["model","target","true_class","exclusive_boundary_group"])
    full = {}
    for _, r in t["whole_cm"][t["whole_cm"].kind.eq("within")].iterrows():
        for tc,c in enumerate(CLASSES):
            full[(r.target,c)] = int(base.matrix(r)[tc].sum())
    totals = grouped.groupby(RUN+["true_class"]).reference_pixels.sum()
    rows=[]
    for r in grouped.itertuples(index=False):
        w=baseline.loc[(r.model,r.target,r.true_class,r.exclusive_boundary_group)]
        for pc in CLASSES:
            if pc==r.true_class: continue
            n,e,we=int(r.reference_pixels),int(getattr(r,"pred_"+pc)),int(w["pred_"+pc])
            rt,wr=ratio(e,n),ratio(we,int(w.reference_pixels))
            near_n=int(totals.loc[tuple(getattr(r,k) for k in RUN)+(r.true_class,)])
            rows.append({k:getattr(r,k) for k in RUN+["band","true_class","exclusive_boundary_group","group_label"]}|
                dict(predicted_class=pc,direction=r.true_class+"_to_"+pc,reference_pixels=n,
                     nearest_reference_pixels=near_n,share_of_nearest_class=ratio(n,near_n),
                     share_of_full_class=ratio(n,full[(r.target,r.true_class)]),
                     errors=e,rate=rt,within_reference_pixels=int(w.reference_pixels),within_errors=we,within_rate=wr,
                     delta_errors=e-we,delta_rate=rt-wr,delta_rate_pp=(rt-wr)*100,
                     rate_status="defined" if n else "no_true_support"))
    d=pd.DataFrame(rows)
    save(d,"exclusive_boundary_grouped_per_prediction",True)
    leak_keys=RUN+["band","true_class","exclusive_boundary_group"]
    leakage=d.groupby(leak_keys,as_index=False).agg(reference_pixels=("reference_pixels","first"),
        errors=("errors","sum"),within_errors=("within_errors","sum"),
        rate=("rate",lambda a:a.sum(min_count=2)),within_rate=("within_rate",lambda a:a.sum(min_count=2)),
        delta_rate=("delta_rate",lambda a:a.sum(min_count=2)))
    expected=grouped[leak_keys+["reference_pixels"]].copy()
    expected["errors"]=[sum(getattr(r,"pred_"+c) for c in CLASSES if c!=r.true_class) for r in grouped.itertuples()]
    compare(leakage,expected,leak_keys,["reference_pixels","errors"],"exclusive two directed errors restore leakage count",True)
    check("exclusive directed rates restore leakage rate",np.allclose(leakage.rate,
          np.divide(leakage.errors,leakage.reference_pixels,where=leakage.reference_pixels.ne(0),out=np.full(len(leakage),np.nan)),
          atol=1e-12,rtol=0,equal_nan=True))
    save(leakage,"exclusive_boundary_leakage_per_prediction",True)
    summary=summarize_boundary(d)
    save(summary,"exclusive_boundary_summary")
    check("exclusive complete six-direction coverage",len(d)==192*6*4 and len(summary)==36*6*4)
    support=grouped[grouped.kind.eq("within") & grouped.model.eq(MODELS[0])][["target","true_class","exclusive_boundary_group","group_label","reference_pixels"]].copy()
    support["nearest_reference_pixels"]=support.groupby(["target","true_class"]).reference_pixels.transform("sum")
    support["share_of_nearest_class"]=support.reference_pixels/support.nearest_reference_pixels
    save(support,"exclusive_boundary_reference_support")
    case=summary[summary.source.eq("iw2_2023")&summary.target.eq("il_2023")&summary.true_class.eq("soybean")&summary.predicted_class.eq("corn")]
    save(case,"case_B_to_D_exclusive_boundary")
    # The supplied review numbers are diagnostic anchors; statistics themselves
    # are always obtained from the input counts.
    anchor=support[support.target.eq("il_2023")&support.true_class.eq("soybean")].set_index("exclusive_boundary_group")
    check("review D soybean support anchors",
          anchor.reference_pixels.to_dict()==dict(contact_1_only=201905,contact_2_only=239867,mixed=30405,nearest_no_direct=82865))
    return d,summary

def composition_six(whole, direction):
    ref={}
    for _, r in whole[whole.kind.eq("within")].iterrows():
        s=base.matrix(r).sum(axis=1)
        if r.target in ref: require(np.array_equal(s,ref[r.target]),"composition reference mismatch")
        ref[r.target]=s
    rows=[]
    for source,target in itertools.permutations(SITES,2):
        row=dict(source=source,target=target,source_site=SITE_LABELS[source],target_site=SITE_LABELS[target])
        for i,c in enumerate(CLASSES):
            for label,site in [("source",source),("target",target)]:
                row[label+"_"+c+"_pixels"]=int(ref[site][i])
                row[label+"_"+c+"_share"]=float(ref[site][i]/ref[site].sum())
            row["target_minus_source_"+c+"_share"]=row["target_"+c+"_share"]-row["source_"+c+"_share"]
        rows.append(row)
    comp=pd.DataFrame(rows)
    save(comp,"source_target_composition")
    keys=["model","source","target","true_class","predicted_class"]
    require(not direction.duplicated(keys).any(),"direction duplicated")
    out=direction.merge(comp,on=["source","target"],how="left",validate="many_to_one",indicator=True)
    check("six-way composition unique complete 216", len(out)==216 and not out.duplicated(keys).any() and out._merge.eq("both").all()
          and all(len(z)==6 for _,z in out.groupby(["model","source","target"])))
    out=out.drop(columns="_merge")
    compare(out,direction,keys,["within_errors","within_rate","cross_rate_mean","delta_rate","delta_errors"],"six composition one-to-one directional join")
    save(out,"source_composition_direction_contrast")
    # Descriptive source-order comparison within a fixed target and model.
    # It tests no causal hypothesis and computes no pooled-path correlation.
    ranks=[]
    for key,x in out.groupby(["model","target","true_class","predicted_class"]):
        tc,pc=key[2:]
        source_order=x.sort_values("source_"+pc+"_share")
        vals=source_order.delta_rate.to_numpy()
        relation="same_order" if (np.diff(vals)>0).all() else "opposite_order" if (np.diff(vals)<0).all() else "no_monotonic_order"
        ranks.append(dict(zip(["model","target","true_class","predicted_class"],key))|
            dict(direction=tc+"_to_"+pc,composition_axis="source_"+pc+"_share",
                 source_order_by_predicted_class_share=";".join(source_order.source.map(SITE_LABELS)),
                 delta_order_ascending=";".join(x.sort_values("delta_rate").source.map(SITE_LABELS)),
                 relation=relation,n_sources=len(x)))
    ranks=pd.DataFrame(ranks)
    save(ranks,"composition_source_order_diagnostic")
    return out,ranks

def model_summary(paths):
    rows=[]
    for (model,crop),x in paths.groupby(["model","crop"]):
        require(len(x)==12 and not x.duplicated(["source","target"]).any(),"12 distinct directed paths")
        row=dict(model=model,crop=crop,n_paths=12,n_independent_within_baselines=4,weight="equal over 12 directed paths")
        for field in ["within_f1","cross_f1_mean","delta_f1","within_precision","cross_precision_mean","delta_precision","within_recall","cross_recall_mean","delta_recall"]:
            a=x[field].to_numpy()
            row[field+"_mean"]=float(a.mean()) if np.isfinite(a).all() else np.nan
        for field in ["f1","precision","recall"]:
            row["delta_"+field+"_pp"]=row["delta_"+field+"_mean"]*100
            v=x["delta_"+field].to_numpy()
            row["delta_"+field+"_median"]=float(np.median(v))
            row["delta_"+field+"_min"]=float(v.min())
            row["delta_"+field+"_max"]=float(v.max())
            row["delta_"+field+"_leave_one_path_out_min"]=float(((v.sum()-v)/11).min())
            row["delta_"+field+"_leave_one_path_out_max"]=float(((v.sum()-v)/11).max())
        row["recall_larger_drop_paths"]=int(x.larger_drop.eq("recall").sum())
        row["precision_larger_drop_paths"]=int(x.larger_drop.eq("precision").sum())
        row["equal_drop_paths"]=int(x.larger_drop.eq("equal").sum())
        row["not_calculable_drop_paths"]=int(x.larger_drop.eq("not_calculable").sum())
        gap=x.delta_precision-x.delta_recall # positive: recall drop is larger
        row["mean_recall_minus_precision_drop"]=float(gap.mean())
        row["leave_one_path_out_gap_min"]=float(((gap.sum()-gap)/11).min())
        row["leave_one_path_out_gap_max"]=float(((gap.sum()-gap)/11).max())
        rows.append(row)
    out=pd.DataFrame(rows)
    save(out,"model_crop_metrics_summary")
    save(paths[paths.crop.isin(["corn","soybean"])],"model_crop_path_diagnostics")
    # Overall and each model omitted: descriptive sensitivity only.
    overall=[]
    for crop,x in paths[paths.crop.isin(["corn","soybean"])].groupby("crop"):
        for excluded in ["none"]+list(MODELS):
            z=x if excluded=="none" else x[x.model.ne(excluded)]
            overall.append(dict(crop=crop,excluded_model=excluded,n_paths=len(z),
                delta_precision_mean=z.delta_precision.mean(),delta_recall_mean=z.delta_recall.mean(),delta_f1_mean=z.delta_f1.mean()))
    save(pd.DataFrame(overall),"pooled_model_influence")
    return out

def case_tables(t, boundary, metrics, paths, directions):
    filt=lambda x: x.target.eq("il_2023")&x.true_class.eq("soybean")&x.predicted_class.eq("corn")
    near=boundary[filt(boundary)]
    save(near,"case_D_exclusive_all_sources")
    d=t["distance_summary"][filt(t["distance_summary"])].copy()
    save(d,"case_D_distance_all_sources")
    k=t["k4"]
    k=k[k.target.eq("il_2023")&k.crop.eq("soybean")&k.kind.eq("cross")&k.region.eq("interior")]
    rows=[]
    for key,x in k.groupby(["model","source","target","crop","spatial_type","region"]):
        require_five(x)
        row=dict(zip(["model","source","target","crop","spatial_type","region"],key))
        row.update(pixels=int(x.pixels.iloc[0]),n_patches=int(x.n_patches.iloc[0]))
        for field in ["delta_other_crop_rate","delta_other_rate","delta_leakage"]:
            row.update(five_stats(x[field],field))
        rows.append(row)
    save(pd.DataFrame(rows),"case_D_C3_C4_interior_all_sources")
    b=paths[paths.model.eq("convgru")&paths.source.eq("iw2_2023")&paths.target.eq("il_2023")]
    save(b,"case_B_D_ConvGRU_crop_metrics")
    e=directions[directions.model.eq("convgru")&directions.source.eq("iw2_2023")&directions.target.eq("il_2023")&
                 directions.true_class.eq("soybean")&directions.predicted_class.eq("corn")]
    check("B-D soybean FN corn FP common direction",len(e)==5)
    save(e,"case_B_D_soybean_to_corn_per_prediction",True)

def seal():
    old=SUM/"analysis_manifest.json"
    manifest=json.loads(old.read_text(encoding="utf-8")) if old.exists() else {}
    if INPUTS: manifest["inputs"]=list(INPUTS.values())
    scripts=[Path(__file__), ROOT/"scripts/explore_sec33_directional_confusion.py",
             ROOT/"scripts/plot_sec33_directional_confusion_closeout.py",
             ROOT/"scripts/test/test_sec33_directional_confusion_closeout.py",
             ROOT/"scripts/test/test_sec33_directional_confusion.py",
             ROOT/"scripts/test/test_f1_raw_scale.py",ROOT/"scripts/test/test_f1_presentation.py"]
    checks=pd.read_csv(SUM/"exclusive_boundary_checks.csv")
    manifest["calculation_checks"]=checks.status.value_counts().to_dict()
    manifest["identity_scope"]=dict(independent_within_model_targets=12,cross_predictions=180,
        directed_model_paths=36,whole_direction_summaries=216,exclusive_boundary_direction_summaries=864)
    manifest.update(created_at_utc=datetime.now(timezone.utc).isoformat(),status="Verified",
        data_status="derived / exploratory",distance_generation_status="Partially verified",distance_transform_rerun=False,
        historical_arrays_reused=True,baseline_head=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
        scripts=[metadata(p,"script") for p in scripts],
        artifacts=[metadata(p,"artifact") for directory in (PROC,SUM,FIG) for p in sorted(directory.glob("*"))
                   if p.is_file() and p.name!="analysis_manifest.json"])
    old.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def main():
    t=load_inputs()
    verify_inputs(t)
    metrics,paths,directions=compute_whole(t)
    direction_summary=summarize_directions(directions,t["direction_summary"])
    _,boundary=build_exclusive(t)
    composition_six(t["whole_cm"],direction_summary)
    model_summary(paths)
    case_tables(t,boundary,metrics,paths,directions)
    save(pd.DataFrame(CHECKS),"exclusive_boundary_checks")
    # Report and dictionary are curated alongside the computed tables rather
    # than generated from hardcoded scientific conclusions.
    seal()
    print(f"Closeout computed: {len(CHECKS)} checks; nearest-boundary, six directions, model strata.")

if __name__=="__main__":
    main()

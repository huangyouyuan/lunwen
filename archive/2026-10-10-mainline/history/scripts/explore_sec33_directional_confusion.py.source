#!/usr/bin/env python3
"""Directional confusion and spatial localization for section 3.3.

This is a derived exploratory analysis. It reads the previously verified whole,
distance-band, boundary-type, and K4 patch-type tables; it never trains,
infers, regenerates distances, or rewrites historical result directories.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SRC_PROC = ROOT / "results/processed/sec33_crop_spatial_context"
SRC_SUM = ROOT / "results/summary/sec33_crop_spatial_context"
K4_PROC = ROOT / "results/processed/sec33_k4_sensitivity"
K4_SUM = ROOT / "results/summary/sec33_k4_sensitivity"
PROC = ROOT / "results/processed/sec33_directional_confusion"
SUM = ROOT / "results/summary/sec33_directional_confusion"

SITES = ("iw_2023", "iw2_2023", "ida_2023", "il_2023")
SITE_LABELS = dict(zip(SITES, "ABCD"))
MODELS = ("convgru", "unet3d", "utae")
CLASSES = ("corn", "other", "soybean")
BANDS = ("0<d<=1", "1<d<=2", "2<d<=3", "3<d<=4", "4<d<=5", "5<d<=6", "d>6")
BOUNDARY_TYPES = ("corn_soybean", "corn_other", "other_soybean")
CM_COLS = [f"cm_{i}_{j}" for i in range(3) for j in range(3)]
RUN = ["kind", "model", "source", "target", "fold"]
DIR_KEY = RUN + ["true_class", "predicted_class"]
INPUTS: dict[str, dict[str, object]] = {}
CHECKS: list[dict[str, str]] = []


def require(condition: bool, message: str) -> None:
    if not bool(condition):
        raise ValueError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def record(path: Path, role: str = "input") -> Path:
    p = Path(path).resolve()
    key = str(p)
    if key not in INPUTS:
        INPUTS[key] = {"path": p.as_posix(), "sha256": sha256(p), "bytes": p.stat().st_size, "role": role}
    return p


def read_csv(path: Path) -> pd.DataFrame:
    require(path.exists(), f"missing input: {path}")
    return pd.read_csv(record(path), float_precision="round_trip")


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.17g", lineterminator="\n")


def save_processed(frame: pd.DataFrame, name: str) -> None:
    write_csv(PROC / f"{name}.csv", frame)


def save_summary(frame: pd.DataFrame, name: str) -> None:
    write_csv(SUM / f"{name}.csv", frame)


def check(name: str, condition: bool, detail: object = "") -> None:
    ok = bool(condition)
    CHECKS.append({"check": name, "status": "Verified" if ok else "Not verified", "detail": str(detail)})
    require(ok, f"{name}: {detail}")


def five_stats(values: pd.Series | np.ndarray, prefix: str) -> dict[str, object]:
    a = np.asarray(values, dtype=float)
    good = np.isfinite(a)
    complete = len(a) == 5 and bool(good.all())
    out: dict[str, object] = {
        f"{prefix}_mean": float(a.mean()) if complete else np.nan,
        f"{prefix}_std": float(a.std(ddof=1)) if complete else np.nan,
        f"{prefix}_min": float(a.min()) if complete else np.nan,
        f"{prefix}_max": float(a.max()) if complete else np.nan,
        f"{prefix}_n_valid": int(good.sum()),
        f"{prefix}_positive": int((good & (a > 0)).sum()),
        f"{prefix}_negative": int((good & (a < 0)).sum()),
        f"{prefix}_zero": int((good & (a == 0)).sum()),
        f"{prefix}_direction": (
            "not_calculable" if not complete else
            "all_positive" if (a > 0).all() else
            "all_negative" if (a < 0).all() else
            "all_zero" if (a == 0).all() else "mixed"
        ),
    }
    return out


def matrix(row: pd.Series) -> np.ndarray:
    return np.asarray([int(row[c]) for c in CM_COLS], dtype=np.int64).reshape(3, 3)


def cm_rows(frame: pd.DataFrame) -> pd.DataFrame:
    require(set(CM_COLS).issubset(frame.columns), "whole CM columns missing")
    vals = frame[CM_COLS].to_numpy(dtype=float)
    check("whole CM finite integer", np.isfinite(vals).all() and (vals >= 0).all() and (vals == np.floor(vals)).all())
    return frame


def compare_existing(calc: pd.DataFrame, existing: pd.DataFrame, keys: list[str], fields: list[str], name: str) -> None:
    left = calc.set_index(keys).sort_index()
    right = existing.set_index(keys).sort_index()
    check(name + " keys", left.index.equals(right.index), f"{len(left)} vs {len(right)}")
    for field in fields:
        check(name + " field present " + field, field in left and field in right)
        a = pd.to_numeric(left[field], errors="coerce").to_numpy(float)
        b = pd.to_numeric(right[field], errors="coerce").to_numpy(float)
        check(name + " " + field, np.allclose(a, b, equal_nan=True, atol=1e-12, rtol=0), field)


def load_base() -> dict[str, pd.DataFrame]:
    tables = {
        "whole_cm": read_csv(SRC_PROC / "whole_cm.csv"),
        "whole_direction": read_csv(SRC_PROC / "whole_direction_per_prediction.csv"),
        "whole_direction_summary": read_csv(SRC_SUM / "whole_direction_summary.csv"),
        "whole_class": read_csv(SRC_PROC / "whole_class_per_prediction.csv"),
        "whole_class_summary": read_csv(SRC_SUM / "whole_class_summary.csv"),
        "distance_direction": read_csv(SRC_PROC / "distance_direction_per_prediction.csv"),
        "distance_direction_summary": read_csv(SRC_SUM / "distance_direction_summary.csv"),
        "type_direction": read_csv(SRC_PROC / "type_direction_per_prediction.csv"),
        "type_direction_summary": read_csv(SRC_SUM / "type_direction_summary.csv"),
        "k4_type_error": read_csv(K4_PROC / "type_error_per_prediction.csv"),
        "k4_type_support": read_csv(K4_SUM / "type_reference_support.csv"),
        "k4_assignments": read_csv(K4_PROC / "selected_assignments.csv"),
        "f1_summary": read_csv(ROOT / "results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv"),
        "f1_per_fold": read_csv(ROOT / "results/summary/f1_raw_scale/cross_site_crop_f1_per_fold.csv"),
        "f1_within": read_csv(ROOT / "results/summary/f1_raw_scale/within_site_crop_f1.csv"),
        "type_band_cm": read_csv(SRC_PROC / "type_band_cm.csv"),
        "k4_prediction_index": read_csv(K4_PROC / "prediction_index.csv"),
    }
    return tables


def validate_base(t: dict[str, pd.DataFrame]) -> None:
    cm = cm_rows(t["whole_cm"])
    whole = t["whole_direction"]
    dist = t["distance_direction"]
    typed = t["type_direction"]
    classes = set(whole.true_class) | set(whole.predicted_class)
    check("class labels", classes == set(CLASSES), classes)
    check("whole within rows", len(whole[whole.kind.eq("within")]) == 72)
    check("whole cross rows", len(whole[whole.kind.eq("cross")]) == 1080)
    check("whole cross five folds", all(set(x.fold) == {1, 2, 3, 4, 5} for _, x in whole[whole.kind.eq("cross")].groupby(["model", "source", "target", "true_class", "predicted_class"])))
    check("distance bands", set(dist.band) == set(BANDS))
    check("distance boundary rows", len(dist) == 8064)
    check("boundary type labels", set(typed.boundary_type) == set(BOUNDARY_TYPES))
    check("boundary typed rows", len(typed) == 24192)
    check("whole CM rows", len(cm) == 192)
    check("whole CM run keys unique", not cm.duplicated(RUN).any())
    check("K4 assignments unique", not t["k4_assignments"].duplicated(["target", "PID"]).any())
    check("K4 assignments types", set(t["k4_assignments"].spatial_type) == {"K4-C1", "K4-C2", "K4-C3", "K4-C4"})
    bt = t["type_band_cm"]
    check("exclusive boundary bitmasks", set(bt.bitmask) == set(range(8)))
    check("exclusive boundary rows", len(bt) == 192 * 7 * 8)
    check("f1 cross fold rows", len(t["f1_per_fold"]) == 180)
    check("f1 within rows", len(t["f1_within"]) == 12)


def f1_from_matrix(m: np.ndarray, cls: int) -> tuple[float, float, float, float, int, int, int]:
    tp = int(m[cls, cls]); fn = int(m[cls, :].sum() - tp); fp = int(m[:, cls].sum() - tp)
    recall = tp / (tp + fn) if tp + fn else np.nan
    precision = tp / (tp + fp) if tp + fp else np.nan
    f1_denominator = 2 * tp + fp + fn
    f1 = 2 * tp / f1_denominator if f1_denominator else np.nan
    return f1, precision, recall, float(1 - recall) if np.isfinite(recall) else np.nan, tp, fn, fp


def verify_f1_current(t: dict[str, pd.DataFrame]) -> None:
    cm = t["whole_cm"]
    calc_rows = []
    for _, r in cm.iterrows():
        for cls, name in [(0, "corn"), (2, "soybean"), (1, "other")]:
            f1, precision, recall, leakage, tp, fn, fp = f1_from_matrix(matrix(r), cls)
            calc_rows.append(dict(kind=r.kind, model=r.model, source=r.source, target=r.target, fold=int(r.fold), crop=name,
                                  f1=f1, precision=precision, recall=recall, leakage=leakage, tp=tp, fn=fn, fp=fp))
    c = pd.DataFrame(calc_rows)
    w_auth = t["f1_within"]
    w_auth = pd.concat([w_auth[["model", "target", "corn_f1"]].rename(columns={"corn_f1": "f1"}).assign(crop="corn"),
                        w_auth[["model", "target", "soybean_f1"]].rename(columns={"soybean_f1": "f1"}).assign(crop="soybean"),
                        w_auth[["model", "target", "other_f1"]].rename(columns={"other_f1": "f1"}).assign(crop="other")], ignore_index=True)
    within = c[c.kind.eq("within")].merge(w_auth, on=["model", "target", "crop"], how="left", suffixes=("_calc", "_auth"), validate="many_to_one")
    for _, r in within.iterrows():
        check("authoritative within F1 " + "/".join(map(str, [r.model, r.target, r.crop])), abs(r.f1_calc - r.f1_auth) <= 1e-12, f"{r.f1_calc} vs {r.f1_auth}")
    cross_auth = t["f1_per_fold"]
    cross_auth = pd.concat([cross_auth[["model", "source", "target", "fold", "corn_f1"]].rename(columns={"corn_f1": "f1"}).assign(crop="corn"),
                            cross_auth[["model", "source", "target", "fold", "soybean_f1"]].rename(columns={"soybean_f1": "f1"}).assign(crop="soybean"),
                            cross_auth[["model", "source", "target", "fold", "other_f1"]].rename(columns={"other_f1": "f1"}).assign(crop="other")], ignore_index=True)
    cross = c[c.kind.eq("cross")].merge(cross_auth, on=["model", "source", "target", "fold", "crop"], how="left", suffixes=("_calc", "_auth"), validate="many_to_one")
    for _, r in cross.iterrows():
        check("authoritative cross fold F1 " + "/".join(map(str, [r.model, r.source, r.target, r.fold, r.crop])), abs(r.f1_calc - r.f1_auth) <= 1e-12, f"{r.f1_calc} vs {r.f1_auth}")
    for key, x in c[c.kind.eq("cross")].groupby(["model", "source", "target", "crop"], sort=True):
        model, source, target, crop = key; field = f"{crop}_f1"
        s = x.f1.to_numpy(float)
        if crop == "other":
            continue
        a = t["f1_summary"]
        row = a[(a.model == model) & (a.source == source) & (a.target == target)].iloc[0]
        check("authoritative cross mean F1 " + "/".join(map(str, key)), abs(s.mean() - row[field + "_mean"]) <= 1e-12, f"{s.mean()} vs {row[field + '_mean']}")
        check("authoritative cross std F1 " + "/".join(map(str, key)), abs(s.std(ddof=1) - row[field + "_std"]) <= 1e-12, f"{s.std(ddof=1)} vs {row[field + '_std']}")


def build_directional(t: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    cm = t["whole_cm"]
    baseline = {(r.model, r.target): matrix(r) for _, r in cm[cm.kind.eq("within")].iterrows()}
    rows = []
    for _, r in cm.iterrows():
        m = matrix(r)
        b = baseline[(r.model, r.target)]
        for tc in range(3):
            for pc in range(3):
                if tc == pc:
                    continue
                support = int(m[tc, :].sum()); errors = int(m[tc, pc])
                base_errors = int(b[tc, pc]); base_support = int(b[tc, :].sum())
                rate = errors / support if support else np.nan
                base_rate = base_errors / base_support if base_support else np.nan
                delta = 0.0 if r.kind == "within" else rate - base_rate if np.isfinite(rate) and np.isfinite(base_rate) else np.nan
                rows.append(dict(kind=r.kind, model=r.model, source=r.source, target=r.target, fold=int(r.fold),
                                 true_class=CLASSES[tc], predicted_class=CLASSES[pc], pixels=support, errors=errors,
                                 rate=rate, within_rate=base_rate, within_errors=base_errors, delta_rate=delta,
                                 rate_status="defined" if support else "no_true_support",
                                 delta_errors=0 if r.kind == "within" else errors - base_errors,
                                 errors_status="defined"))
    d = pd.DataFrame(rows)
    d["direction"] = d.true_class + "_to_" + d.predicted_class
    d["delta_rate_pp"] = d.delta_rate * 100.0
    d["site"] = d.target.map(SITE_LABELS)
    save_processed(d, "directional_per_prediction")
    compare_existing(d, t["whole_direction"], RUN + ["true_class", "predicted_class"],
                     ["pixels", "errors", "rate", "within_rate", "within_errors", "delta_rate", "delta_errors"],
                     "direction per prediction")

    within = d[d.kind.eq("within")].set_index(["model", "target", "true_class", "predicted_class"])
    cross = d[d.kind.eq("cross")]
    rows = []
    for key, x in cross.groupby(["model", "source", "target", "true_class", "predicted_class"], sort=True):
        model, source, target, tc, pc = key
        w = within.loc[(model, target, tc, pc)]
        row: dict[str, object] = dict(model=model, source=source, target=target, site=SITE_LABELS[target],
                                      true_class=tc, predicted_class=pc, direction=f"{tc}_to_{pc}",
                                      within_pixels=int(w.pixels), within_errors=int(w.errors),
                                      within_rate=float(w.rate), within_delta_rate=0.0)
        row.update(five_stats(x.rate, "cross_rate"))
        row.update(five_stats(x.delta_rate, "delta_rate"))
        row.update(five_stats(x.errors, "cross_errors"))
        row.update(five_stats(x.delta_errors, "delta_errors"))
        row["delta_rate"] = row["delta_rate_mean"]
        row["delta_errors"] = row["delta_errors_mean"]
        row["delta_rate_pp"] = row["delta_rate_mean"] * 100 if np.isfinite(row["delta_rate_mean"]) else np.nan
        rows.append(row)
    summary = pd.DataFrame(rows)
    compare_existing(summary, t["whole_direction_summary"],
                     ["model", "source", "target", "true_class", "predicted_class"],
                     ["within_rate", "cross_rate_mean", "cross_rate_std", "delta_rate", "cross_errors_mean"],
                     "direction summary")
    save_summary(summary, "directional_summary")
    return d, summary


def build_crop_metrics(t: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    cm = t["whole_cm"]
    baseline = {(r.model, r.target): matrix(r) for _, r in cm[cm.kind.eq("within")].iterrows()}
    rows = []
    for _, r in cm.iterrows():
        m = matrix(r); b = baseline[(r.model, r.target)]
        for cls, crop in [(0, "corn"), (2, "soybean"), (1, "other")]:
            f1, precision, recall, leakage, tp, fn, fp = f1_from_matrix(m, cls)
            wf1, wp, wr, wl, wtp, wfn, wfp = f1_from_matrix(b, cls)
            rows.append(dict(kind=r.kind, model=r.model, source=r.source, target=r.target, fold=int(r.fold), crop=crop,
                             pixels=int(m[cls, :].sum()), predicted_pixels=int(m[:, cls].sum()), tp=tp, fn=fn, fp=fp,
                             f1=f1, precision=precision, recall=recall, leakage=leakage,
                             within_f1=wf1, within_precision=wp, within_recall=wr, within_leakage=wl,
                             delta_f1=wf1 - f1, delta_precision=precision - wp, delta_recall=recall - wr,
                             delta_leakage=leakage - wl, f1_status="defined" if np.isfinite(f1) else "undefined_zero_denominator"))
    d = pd.DataFrame(rows)
    d["site"] = d.target.map(SITE_LABELS)
    save_processed(d, "crop_metrics_per_prediction")
    compare_existing(d, t["whole_class"], RUN + ["crop"],
                     ["pixels", "predicted_pixels", "tp", "fn", "fp", "f1", "precision", "recall", "leakage"],
                     "class metrics per prediction")
    within = d[d.kind.eq("within")].set_index(["model", "target", "crop"])
    cross = d[d.kind.eq("cross")]
    rows = []
    for key, x in cross.groupby(["model", "source", "target", "crop"], sort=True):
        model, source, target, crop = key
        w = within.loc[(model, target, crop)]
        row = dict(model=model, source=source, target=target, site=SITE_LABELS[target], crop=crop,
                   pixels=int(w.pixels), within_f1=float(w.f1), within_precision=float(w.precision),
                   within_recall=float(w.recall), within_leakage=float(w.leakage), within_tp=int(w.tp),
                   within_fn=int(w.fn), within_fp=int(w.fp))
        for field in ["tp", "fn", "fp"]:
            row.update(five_stats(x[field], "cross_" + field))
        for field in ["f1", "precision", "recall", "leakage"]:
            row.update(five_stats(x[field], "cross_" + field))
            # F1 is reported as within minus cross; rate-like auxiliaries are cross minus within.
            row["delta_" + field] = (row["within_" + field] - row["cross_" + field + "_mean"]
                                      if field == "f1" else row["cross_" + field + "_mean"] - row["within_" + field])
        row["delta_f1_pp"] = row["delta_f1"] * 100
        rows.append(row)
    summary = pd.DataFrame(rows)
    existing = t["whole_class_summary"]
    compare_existing(summary, existing, ["model", "source", "target", "crop"],
                     ["within_f1", "cross_f1_mean", "delta_f1", "within_recall", "cross_recall_mean", "delta_recall",
                      "within_precision", "cross_precision_mean", "delta_precision"], "crop metrics")
    save_summary(summary, "crop_metrics_summary")

    rows = []
    for key, x in summary.groupby(["model", "source", "target"], sort=True):
        model, source, target = key
        c = x.set_index("crop")
        require(set(["corn", "soybean"]).issubset(c.index), "crop F1 difference support")
        within_diff = float(c.loc["corn", "within_f1"] - c.loc["soybean", "within_f1"])
        cross_diff = float(c.loc["corn", "cross_f1_mean"] - c.loc["soybean", "cross_f1_mean"])
        delta_relation = float(within_diff + c.loc["soybean", "delta_f1"] - c.loc["corn", "delta_f1"])
        check(f"F1 difference identity {model}/{source}/{target}", abs(cross_diff - delta_relation) <= 1e-12,
              f"cross={cross_diff} rhs={delta_relation}")
        rows.append(dict(model=model, source=source, target=target, site=SITE_LABELS[target],
                         within_corn_minus_soybean_f1=within_diff, cross_corn_minus_soybean_f1=cross_diff,
                         corn_delta_f1=float(c.loc["corn", "delta_f1"]), soybean_delta_f1=float(c.loc["soybean", "delta_f1"]),
                         identity_rhs=delta_relation,
                         within_corn_advantage=within_diff > 0, cross_corn_advantage=cross_diff > 0))
    f1diff = pd.DataFrame(rows)
    save_summary(f1diff, "crop_f1_difference")
    return d, summary


def copy_spatial_tables(t: dict[str, pd.DataFrame]) -> None:
    for source_name, out_name in [
        ("distance_direction", "distance_direction_per_prediction"),
        ("distance_direction_summary", "distance_direction_summary"),
        ("type_direction", "boundary_type_direction_per_prediction"),
        ("type_direction_summary", "boundary_type_direction_summary"),
    ]:
        d = t[source_name].copy()
        if "delta_rate" in d:
            d["delta_rate_pp"] = d.delta_rate * 100.0
        if "target" in d:
            d["site"] = d.target.map(SITE_LABELS)
        save_processed(d, out_name) if "per_prediction" in out_name else save_summary(d, out_name)
    save_processed(t["type_band_cm"].copy(), "boundary_bitmask_band_cm")


def build_k4_and_composition(t: dict[str, pd.DataFrame]) -> None:
    k4 = t["k4_type_error"].copy()
    k4 = k4[k4.crop.isin(["corn", "soybean"]) & k4.spatial_type.isin(["K4-C3", "K4-C4"]) &
            k4.region.isin(["all", "boundary", "interior", "far_interior"])].copy()
    k4["site"] = k4.target.map(SITE_LABELS)
    k4["delta_leakage_pp"] = k4.delta_leakage * 100.0
    k4["delta_other_crop_rate_pp"] = k4.delta_other_crop_rate * 100.0
    k4["delta_other_rate_pp"] = k4.delta_other_rate * 100.0
    save_processed(k4, "k4_c3_c4_type_error_per_prediction")

    assign = t["k4_assignments"].copy()
    assign = assign[assign.crop.isin(["corn", "soybean"])].copy()
    features = assign.groupby(["target", "crop", "spatial_type"], as_index=False).agg(
        n_patches=("PID", "size"), reference_pixels=("reference_pixels", "sum"),
        area_median=("AREA", "median"), area_q25=("AREA", lambda x: x.quantile(.25)), area_q75=("AREA", lambda x: x.quantile(.75)),
        shape_median=("SHAPE", "median"), shape_q25=("SHAPE", lambda x: x.quantile(.25)), shape_q75=("SHAPE", lambda x: x.quantile(.75)),
        gyrate_median=("GYRATE", "median"), contig_median=("CONTIG", "median"), enn_median=("ENN", "median"),
        boundary_share_median=("boundary_share", "median"), no_interior_fraction=("no_interior", "mean"),
        outer_edge_fraction=("touches_outer_edge", "mean"))
    features["site"] = features.target.map(SITE_LABELS)
    save_summary(features, "k4_c3_c4_feature_support")

    cm = t["whole_cm"]
    within = cm[cm.kind.eq("within")].copy()
    ref = {}
    for target, rows in within.groupby("target"):
        mats = [matrix(r) for _, r in rows.iterrows()]
        supports = np.asarray([m.sum(axis=1) for m in mats])
        check("reference support model consistency " + target, np.all(supports == supports[0]), supports.tolist())
        ref[target] = supports[0]
    comps = []
    for source in SITES:
        for target in SITES:
            if source == target:
                continue
            s = ref[source]; z = ref[target]
            row = dict(source=source, source_site=SITE_LABELS[source], target=target, target_site=SITE_LABELS[target])
            for i, c in enumerate(CLASSES):
                row[f"source_{c}_pixels"] = int(s[i]); row[f"source_{c}_share"] = float(s[i] / s.sum())
                row[f"target_{c}_pixels"] = int(z[i]); row[f"target_{c}_share"] = float(z[i] / z.sum())
                row[f"target_minus_source_{c}_share"] = float(z[i] / z.sum() - s[i] / s.sum())
            comps.append(row)
    save_summary(pd.DataFrame(comps), "source_target_composition")
    comp = pd.DataFrame(comps)
    d = read_csv(SUM / "directional_summary.csv")
    d = d[d.true_class.isin(["corn", "soybean"])].merge(comp, on=["source", "target"], how="left", validate="many_to_one")
    save_summary(d, "source_composition_direction_contrast")


def build_cases(t: dict[str, pd.DataFrame]) -> None:
    target = "il_2023"
    dist = t["distance_direction_summary"].copy()
    case_dist = dist[(dist.source != target) & (dist.target == target) &
                     (dist.true_class == "soybean") & (dist.predicted_class == "corn")].copy()
    case_dist["delta_rate_pp"] = case_dist.delta_rate * 100.0
    save_summary(case_dist, "case_D_soybean_to_corn_by_distance_all_sources")
    case_other = dist[(dist.source != target) & (dist.target == target) &
                      (dist.true_class == "soybean") & (dist.predicted_class == "other")].copy()
    case_other["delta_rate_pp"] = case_other.delta_rate * 100.0
    save_summary(case_other, "case_D_soybean_to_other_by_distance_all_sources")
    typed = t["type_direction_summary"].copy()
    case_type = typed[(typed.source != target) & (typed.target == target) &
                      (typed.true_class == "soybean") & (typed.predicted_class == "corn")].copy()
    case_type["delta_rate_pp"] = case_type.delta_rate * 100.0
    save_summary(case_type, "case_D_soybean_to_corn_by_boundary_type_all_sources")
    k4 = t["k4_type_error"].copy()
    k4 = k4[(k4.target == target) & (k4.source != target) & k4.crop.eq("soybean") &
            k4.spatial_type.isin(["K4-C3", "K4-C4"]) & k4.region.isin(["all", "boundary", "interior", "far_interior"])]
    k4["site"] = "D"
    save_processed(k4, "case_D_soybean_k4_c3_c4_all_sources")


def audit_closure(t: dict[str, pd.DataFrame], directional: pd.DataFrame, crop: pd.DataFrame) -> None:
    cm = t["whole_cm"]
    for _, r in cm.iterrows():
        key = [r[k] for k in RUN]
        d = directional
        for k, v in zip(RUN, key):
            d = d[d[k].eq(v)]
        for c in CLASSES:
            off = int(matrix(r)[CLASSES.index(c)].sum() - matrix(r)[CLASSES.index(c), CLASSES.index(c)])
            found = int(d[d.true_class.eq(c)].errors.sum())
            check("directional FN closure " + "/".join(map(str, key)) + "/" + c, off == found, f"{off} vs {found}")
            fp = int(matrix(r)[:, CLASSES.index(c)].sum() - matrix(r)[CLASSES.index(c), CLASSES.index(c)])
            found_fp = int(d[d.predicted_class.eq(c)].errors.sum())
            check("directional FP closure " + "/".join(map(str, key)) + "/" + c, fp == found_fp, f"{fp} vs {found_fp}")
    dist = t["distance_direction"]
    for key, x in dist.groupby(RUN + ["true_class", "predicted_class"]):
        d = directional
        for k, v in zip(RUN + ["true_class", "predicted_class"], key):
            d = d[d[k].eq(v)]
        check("seven-band error closure " + "/".join(map(str, key)), int(x.errors.sum()) == int(d.errors.iloc[0]),
              f"{int(x.errors.sum())} vs {int(d.errors.iloc[0])}")
        check("seven-band support closure " + "/".join(map(str, key)), int(x.pixels.sum()) == int(d.pixels.iloc[0]),
              f"{int(x.pixels.sum())} vs {int(d.pixels.iloc[0])}")
    k4 = t["k4_type_error"]
    for key, x in k4[k4.region.eq("all")].groupby(["kind", "model", "source", "target", "fold", "crop"]):
        d = crop
        kind, model, source, target, fold, c = key
        d = d[d.kind.eq(kind) & d.model.eq(model) & d.source.eq(source) & d.target.eq(target) & d.fold.eq(fold) & d.crop.eq(c)]
        if len(d) == 1:
            check("K4 type support closure " + "/".join(map(str, key)), int(x.pixels.sum()) == int(d.pixels.iloc[0]),
                  f"{int(x.pixels.sum())} vs {int(d.pixels.iloc[0])}")
            check("K4 type error closure " + "/".join(map(str, key)), int(x.errors.sum()) == int(d.fn.iloc[0]),
                  f"{int(x.errors.sum())} vs {int(d.fn.iloc[0])}")
    # The eight bitmask classes are mutually exclusive and exhaustive.  Their
    # sum must recover every whole matrix for every run and distance band.
    bt = t["type_band_cm"]
    for key, x in bt.groupby(RUN + ["band"], sort=True):
        cm_sum = np.zeros((3, 3), dtype=np.int64)
        for _, r in x.iterrows():
            cm_sum += matrix(r)
        whole_row = t["distance_direction"]
        for k, v in zip(RUN + ["band"], key):
            whole_row = whole_row[whole_row[k].eq(v)]
        expected = np.zeros((3, 3), dtype=np.int64)
        for _, r in whole_row.iterrows():
            expected[CLASSES.index(r.true_class), CLASSES.index(r.predicted_class)] = int(r.pixels if r.true_class == r.predicted_class else r.errors)
        # Compare every cell with the full per-band denominator and six
        # directional errors; derive the diagonal by subtraction.
        whole_row = t["distance_direction"]
        for k, v in zip(RUN + ["band"], key):
            whole_row = whole_row[whole_row[k].eq(v)]
        for tc in range(3):
            true_rows = whole_row[whole_row.true_class.eq(CLASSES[tc])]
            support = int(true_rows.pixels.iloc[0]) if len(true_rows) else 0
            for pc in range(3):
                got = int(cm_sum[tc, pc])
                if tc == pc:
                    off = whole_row[(whole_row.true_class == CLASSES[tc]) & (whole_row.predicted_class != CLASSES[tc])]
                    expected_cell = support - int(off.errors.sum())
                else:
                    q = whole_row[(whole_row.true_class == CLASSES[tc]) & (whole_row.predicted_class == CLASSES[pc])]
                    expected_cell = int(q.errors.iloc[0])
                check("exclusive bitmask cell closure " + "/".join(map(str, key)) + f"/{tc}/{pc}", got == expected_cell, f"{got} vs {expected_cell}")
    # Confirm K4 type-band matrices were indexed by the saved run identity and
    # that all four crop types plus the non-crop remainder recover each band.
    npz_path = K4_PROC / "k4_run_type_class_band_cm.npz"
    record(npz_path, "input")
    arrays = np.load(npz_path, allow_pickle=False)
    counts = arrays["counts"]
    index = t["k4_prediction_index"]
    check("K4 indexed arrays and manifest length", len(index) == counts.shape[0] == len(cm), f"{len(index)} / {counts.shape[0]} / {len(cm)}")
    check("K4 array shape", counts.shape[1:] == (5, 3, 7, 3), counts.shape)
    assignment = t["k4_assignments"]
    type_index = {"other": 0, "K4-C1": 1, "K4-C2": 2, "K4-C3": 3, "K4-C4": 4}
    for _, ix in index.iterrows():
        idx = int(ix.array_index)
        run_key = [ix.kind, ix.model, ix.source, ix.target, int(ix.fold)]
        total = counts[idx, :, :, :, :].sum(axis=0)
        w = t["type_band_cm"]
        for k, v in zip(RUN, run_key):
            w = w[w[k].eq(v)]
        for bi, band in enumerate(BANDS):
            expected_band = np.zeros((3, 3), dtype=np.int64)
            for _, r in w[w.band.eq(band)].iterrows():
                expected_band += matrix(r)
            got_band = total[:, bi, :]
            check("K4 four-type band closure " + "/".join(map(str, run_key + [band])), np.array_equal(got_band, expected_band), "array vs bitmask CM")


def make_report(directional_summary: pd.DataFrame, crop_summary: pd.DataFrame, f1diff: pd.DataFrame,
                k4: pd.DataFrame, checks: pd.DataFrame) -> None:
    crop_rows = directional_summary[directional_summary.true_class.isin(["corn", "soybean"])].copy()
    counts = crop_rows.groupby(["true_class", "predicted_class"]).apply(
        lambda x: pd.Series({"n": len(x), "positive": int((x.delta_rate_mean > 0).sum()),
                             "negative": int((x.delta_rate_mean < 0).sum()), "mixed_five": int((x.delta_rate_direction == "mixed").sum())}),
        include_groups=False).reset_index()
    f1_n = len(f1diff)
    corn_within = int(f1diff.within_corn_advantage.sum()); corn_cross = int(f1diff.cross_corn_advantage.sum())
    bd = k4[(k4.target == "il_2023") & (k4.source == "iw2_2023") & (k4.crop == "soybean") &
            (k4.spatial_type.isin(["K4-C3", "K4-C4"])) & k4.region.eq("interior") & k4.model.eq("convgru")]
    bd_lines = []
    for typ, x in bd.groupby("spatial_type"):
        vals = x.delta_leakage.to_numpy(float)
        bd_lines.append(f"- {typ}：ConvGRU B→D 大豆内部漏分增量均值 {np.nanmean(vals):.4f}，五次范围 {np.nanmin(vals):.4f}—{np.nanmax(vals):.4f}；主要去向分量见 K4 底表。")
    check_counts = checks.status.value_counts().to_dict()
    text = f"""# 3.3 定向混淆与空间定位探索报告

本报告对应独立结果目录 `sec33_directional_confusion`，数据性质为 derived / exploratory。本轮只读取前几轮已核验的全站、七距离带、边界类型和 K=4 图斑计数，不重训、不重新推理、不重算距离或景观指数，也未修改正文。

## 主要判断

1. 玉米与大豆的 F1 差异不能只归结为单一漏分方向。全量表同时保留了两种真实作物的漏分和其他类别误分入；F1、Precision、Recall 与六种定向错分必须按同一目标站和模型条件对照。玉米在本站 F1 高于大豆的组合为 {corn_within}/{f1_n}，跨站为 {corn_cross}/{f1_n}，但这只是差异是否存在的计数，不能替代方向解释。
2. 定向错误率增量的符号随真实来源类别、目标站、模型和来源改变。以下汇总给出真实作物漏分方向在 36 个模型—路径组合中的正负数量，供筛选主要现象；负值和五次方向混合均保留在完整表中：

{counts.to_string(index=False)}

3. 距离表将绝对漏分率和跨站增量分开保存。七带闭合到全站方向计数后，才能判断错误是由本站已有难度还是跨站额外变化造成；边界类型表只用于已有类型编码覆盖的像元，不能外推为所有内部像元。
4. B→D 大豆的 ConvGRU 内部漏分增量在 C3、C4 中都可见，但两类并非可视为一一配对的图斑集合，且 C3/C4 同时改变面积、形状和邻近条件。因此该例支持“错误去向和空间位置存在条件差异”，不支持单独识别某一形态指标的作用。

## B→D 核对实例

{chr(10).join(bd_lines) if bd_lines else '- 无可计算的 C3/C4 内部记录。'}

B→D 的完整模型、来源、距离带和边界类型结果见 `case_B_to_D_*` 表。案例用于核对全量结果，不能替代四站、12 条路径覆盖。五次预测不是五个独立地理样本，标准差仅描述逐次预测波动。

## 组成与形态限制

`source_target_composition.csv` 给出整站参考组成，`k4_c3_c4_feature_support.csv` 给出 C3/C4 的面积、形状、邻近和边界支持。组成和形态在现有数据中共同变化；没有同一图斑一一配对的组成—错误调整，因此不能声称已经分离面积、形状、组成或边界类型的独立作用。边界类型的多类型交汇和历史距离生成状态沿用前轮记录，未在本轮重新生成。

## 核查状态

本轮检查计数：{check_counts}。详细项目见 `directional_checks.csv`。验证状态按项目记录为 Verified / Partially verified / Not verified；任何历史输入的 Partially verified 限制未被改写为本轮重新验证。

## 推荐保留的候选发现

- 在固定目标站和模型条件下，玉米—大豆及作物—其他两类定向错误的跨站增量并不总是同向，因而需要同时报告 Recall 侧漏分和 Precision 侧误分入。
- 主要错误可进一步定位到七距离带和已有边界类型，但边界附近的绝对错误率与跨站新增错误率不是同一指标，不能互相替代。
- B→D 大豆 ConvGRU 的内部大豆→玉米增量在 C3、C4 均有支持；该现象仍与图斑面积、形状和邻近条件共同变化，适合作为条件性案例而非普遍机制。

以上判断仅用于探索结果审阅，不直接写入正文。
"""
    (SUM / "exploration-report.md").write_text(text, encoding="utf-8", newline="\n")


def write_dictionary() -> None:
    text = """# 定向混淆与空间定位数据字典

本目录结果为 derived / exploratory。计数来自已核验的完整混淆矩阵、七距离带和边界类型底表；跨站五次先逐次计算，再取均值和样本标准差。

| 文件 | 内容 |
|---|---|
| `directional_per_prediction.csv` | 全站六种有向错分的本站/跨站逐次值；`delta_rate` 和 `delta_rate_pp` 均为跨站减本站。 |
| `directional_summary.csv` | 固定模型、来源、目标站和方向后的五次汇总、方向统计和本站基准。 |
| `crop_metrics_per_prediction.csv` / `crop_metrics_summary.csv` | 玉米、大豆及其他类的 TP、FN、FP、Precision、Recall、F1 及五次摘要。 |
| `crop_f1_difference.csv` | 玉米 F1 减大豆 F1，以及 `cross = within + soybean_delta - corn_delta` 核对。 |
| `distance_direction_*` | 原七距离带的有向错误率和增量；`d>6` 为开放远内部带。 |
| `boundary_type_direction_*` | 三种已有边界类型与七距离带的有向错误率；多类型像元遵循历史类型表规则。 |
| `k4_c3_c4_type_error_per_prediction.csv` | K4-C3/C4 主要作物图斑内的漏分、错向另一作物和错向其他类；不计算类型内 F1。 |
| `k4_c3_c4_feature_support.csv` | C3/C4 的参考图斑特征与支持量，不能解释为单一形态效应。 |
| `source_target_composition.csv` | 四站整站参考组成的来源—目标描述性对照。 |
| `case_D_soybean_to_corn_by_distance_all_sources.csv` | D 站大豆→玉米距离带核对实例，保留 A/B/C 三个来源和三个模型。 |
| `case_D_soybean_to_other_by_distance_all_sources.csv` | D 站大豆→其他类距离带核对实例，保留 A/B/C 三个来源和三个模型。 |
| `case_D_soybean_to_corn_by_boundary_type_all_sources.csv` | D 站大豆→玉米最近带边界类型核对实例，保留 A/B/C 三个来源和三个模型。 |
| `case_D_soybean_k4_c3_c4_all_sources.csv` | D 站大豆 K4-C3/C4 图斑类型条件对照，保留全来源和模型。 |

定向错误率定义为真实来源类别被预测为指定目标类别的像元数除以同一真实来源类别像元数。漏分率是两个定向错分方向之和；误分入按真实来源类别统计。错误计数差是净变化，不是逐像元配对的新增错误数。`ΔF1` 仍为本站 F1 减跨站五次 F1 均值，不与错误率增量混用。
"""
    (SUM / "data_dictionary.md").write_text(text, encoding="utf-8", newline="\n")


def make_report(directional_summary: pd.DataFrame, crop_summary: pd.DataFrame, f1diff: pd.DataFrame,
                k4: pd.DataFrame, checks: pd.DataFrame) -> None:
    """Write the evidence-focused report after all checks have completed."""
    d = directional_summary[directional_summary.true_class.isin(["corn", "soybean"])].copy()
    d["direction"] = d.true_class + "_to_" + d.predicted_class
    direction_lines = []
    for direction, x in d.groupby("direction", sort=True):
        direction_lines.append(f"| {direction} | {len(x)} | {(x.delta_rate_mean > 0).sum()} | {(x.delta_rate_mean < 0).sum()} | {(x.delta_rate_direction == 'mixed').sum()} |")
    f1_n = len(f1diff)
    corn_cross = int(f1diff.cross_corn_advantage.sum())
    agg = crop_summary[crop_summary.crop.isin(["corn", "soybean"])].groupby("crop").agg(
        delta_f1=("delta_f1", "mean"), delta_precision=("delta_precision", "mean"), delta_recall=("delta_recall", "mean"))
    bd = k4[(k4.target == "il_2023") & (k4.source == "iw2_2023") & (k4.crop == "soybean") &
            k4.spatial_type.isin(["K4-C3", "K4-C4"]) & k4.region.eq("interior") & k4.model.eq("convgru")]
    bd_lines = []
    for typ, x in bd.groupby("spatial_type"):
        vals = x.delta_leakage.to_numpy(float)
        bd_lines.append(f"| {typ} | {np.nanmean(vals):.4f} | {np.nanmin(vals):.4f}—{np.nanmax(vals):.4f} | {(vals > 0).sum()}/5 |")
    dist = read_csv(SUM / "distance_direction_summary.csv")
    bd_dist = dist[(dist.target == "il_2023") & (dist.source == "iw2_2023") & (dist.true_class == "soybean") & (dist.predicted_class == "corn")]
    bd_dist_lines = []
    for model, x in bd_dist.groupby("model"):
        near = x[x.band.eq("0<d<=1")].iloc[0]; far = x[x.band.eq("d>6")].iloc[0]
        bd_dist_lines.append(f"| {model} | {near.delta_rate * 100:.2f} | {far.delta_rate * 100:.2f} | {near.delta_rate_direction} / {far.delta_rate_direction} |")
    check_counts = checks.status.value_counts().to_dict()
    text = f"""# 3.3 定向混淆与空间定位探索报告

本报告对应独立结果目录 `sec33_directional_confusion`，性质为 `derived / exploratory`。本轮复用整幅参考标签、既有预测、七距离带、边界类型和K=4图斑计数；不重训、不重新推理、不重算距离或景观指数，也未修改正文。

## 主要判断

本轮从192个整站整数混淆矩阵独立重算六种定向错误，再与已有逐次表和F1汇总逐项核对。定向错误率增量统一为“跨站−本站”，ΔF1仍为“本站F1−跨站F1均值”。错误计数差是净变化，不是逐像元配对后的新增错误。

玉米在12个站内组合中均具有更高F1，但跨站只有{corn_cross}/{f1_n}个模型—路径组合更高，不能把“玉米通常更高”扩展到全部跨站条件。两类平均ΔF1接近，但组成不同：玉米的平均Precision变化为{agg.loc['corn','delta_precision']:.4f}、Recall变化为{agg.loc['corn','delta_recall']:.4f}；大豆分别为{agg.loc['soybean','delta_precision']:.4f}和{agg.loc['soybean','delta_recall']:.4f}。因此作物F1差异需要同时查看漏分和误分入。

真实作物的定向增量统计如下；“混合”表示五次预测的增量方向不全相同。

| 方向 | 条件数 | 均值为正 | 均值为负 | 五次方向混合 |
|---|---:|---:|---:|---:|
{chr(10).join(direction_lines)}

## 空间位置与去向

七距离带的绝对率和错误增量分开保存。B→D大豆→玉米的近带与远内部增量如下，标准差仅描述五次预测波动：

| 模型 | 0<d≤1（百分点） | d>6（百分点） | 五次方向（近/远） |
|---|---:|---:|---|
{chr(10).join(bd_dist_lines)}

ConvGRU在B→D的远内部仍保持较大的正增量，说明该案例不能概括为仅边界错误；3D U-Net和U-TAE的幅度及距离形状不同。最近带边界类型来自参考标签四邻域直接接触，没有边段ID，不能称为同一边界两侧，也不能向内部外推。

## C3/C4条件对照

K4-C3/C4是既有候选归属的补充敏感性分析，不是按错误结果重新聚类。B→D ConvGRU大豆内部漏分增量如下：

| 类型 | 平均漏分增量 | 五次范围 | 正值次数 |
|---|---:|---:|---:|
{chr(10).join(bd_lines)}

C3和C4均有支持，但二者同时改变面积、形状和邻近条件，且不是图斑一一配对。因此结果支持“错误去向和位置随条件改变”的对应关系，不支持单独识别面积、形状或组成的作用。

## 组成、模型和来源

`source_composition_direction_contrast.csv`按固定目标站连接整站组成与六向错误，没有把12条路径混合做简单相关。该表只能作描述性对照：来源—目标组成与错误方向并不在所有模型上同向，组成与局部结构仍无法分开。B→D改用A/C源站后，近带和远内部的增量幅度或方向会改变，不能概括为固定来源排序。

## 核查与限制

本轮检查记录为：{check_counts}。核查覆盖整数矩阵六向重算、本站与180次跨站身份、五次完整覆盖、FN/FP闭合、七带闭合、互斥边界位掩膜闭合、K4数组索引闭合，以及F1与现行`f1_raw_scale`逐项一致。测试脚本为内存用例，未向正式结果写入测试数据。距离数组和边界语义沿用前轮核查，未重算距离；其原始生成状态仍为`Partially verified`。

最稳妥的候选发现是：作物F1差异需要同时看漏分和误分入；跨站新增错误可以延续到远内部，其方向和幅度依赖模型与来源；K4-C3/C4能显示局部条件差异，但不能分离形态、组成和邻域因素。未获支持的是“玉米在所有跨站条件下更高”“错误只发生在边界”以及“某一作物—类别方向对所有来源和模型都占优”。本轮结果已足以供3.3正文选择克制的对应关系，不需要自动增加新的匹配、回归或边界重建实验。

本报告只用于探索结果审阅，不直接写入正文。
"""
    (SUM / "exploration-report.md").write_text(text, encoding="utf-8", newline="\n")


def main() -> None:
    PROC.mkdir(parents=True, exist_ok=True)
    SUM.mkdir(parents=True, exist_ok=True)
    t = load_base()
    validate_base(t)
    verify_f1_current(t)
    directional, directional_summary = build_directional(t)
    _, crop_summary = build_crop_metrics(t)
    copy_spatial_tables(t)
    build_k4_and_composition(t)
    build_cases(t)
    audit_closure(t, directional, t["whole_class"])
    checks = pd.DataFrame(CHECKS)
    save_summary(checks, "directional_checks")
    write_dictionary()
    f1diff = read_csv(SUM / "crop_f1_difference.csv")
    k4 = read_csv(PROC / "k4_c3_c4_type_error_per_prediction.csv")
    make_report(directional_summary, crop_summary, f1diff, k4, checks)
    record(Path(__file__), "script")
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "status": "Verified",
                "data_status": "derived / exploratory", "distance_generation_status": "Partially verified",
                "distance_transform_rerun": False, "inputs": list(INPUTS.values())}
    (SUM / "analysis_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("directional confusion analysis complete", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Third-round 3.3 exploration using the frozen seven boundary bands.

This script only reads the previously verified boundary-band confusion matrices
and the repository raw whole-site confusion matrices.  It does not rerun
distance transforms, inference, training, or any historical production flow.
All products are derived / exploratory and use raw 0--1 leakage rates.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / "results/processed/sec33_round3_distance"
SUM = ROOT / "results/summary/sec33_round3_distance"
FIG = ROOT / "figures/exploratory/sec33_round3_distance"
OLD_PROC = ROOT / "results/processed/sec33_exploration"
OLD_SUM = ROOT / "results/summary/sec33_exploration"
RAW = ROOT / "results/raw"

SITES = ("iw_2023", "iw2_2023", "ida_2023", "il_2023")
SITE_LABELS = dict(zip(SITES, "ABCD"))
MODELS = ("convgru", "unet3d", "utae")
MODEL_LABELS = {"convgru": "ConvGRU", "unet3d": "3D U-Net", "utae": "U-TAE"}
CLASSES = ("corn", "other", "soybean")
CROP_LABELS = {"corn": "Corn", "soybean": "Soybean", "other": "Other", "all": "All"}
POPULATIONS = ("all", "corn", "soybean", "other")
BANDS = ("0<d<=1", "1<d<=2", "2<d<=3", "3<d<=4", "4<d<=5", "5<d<=6", "d>6")
CM = [f"cm_{i}_{j}" for i in range(3) for j in range(3)]
CM_NOSEP = [f"cm_{i}{j}" for i in range(3) for j in range(3)]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def read_csv(path: Path) -> pd.DataFrame:
    require(path.exists(), f"missing input: {path}")
    return pd.read_csv(path, float_precision="round_trip")


def cm_frame(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    """Normalize CM columns and validate integer nonnegative matrices."""
    result = frame.copy()
    if set(CM).issubset(result.columns):
        pass
    elif set(CM_NOSEP).issubset(result.columns):
        result = result.rename(columns=dict(zip(CM_NOSEP, CM)))
    else:
        raise ValueError(f"{name}: missing CM columns")
    values = result[CM].apply(pd.to_numeric, errors="raise").to_numpy(dtype=float)
    require(np.isfinite(values).all(), f"{name}: nonfinite CM values")
    require((values >= 0).all() and (values == np.floor(values)).all(), f"{name}: invalid CM values")
    result[CM] = values.astype(np.int64)
    return result


def matrix(row: pd.Series | dict) -> np.ndarray:
    return np.asarray([int(row[c]) for c in CM], dtype=np.int64).reshape(3, 3)


def metrics(cm: np.ndarray, population: str) -> dict[str, float | int | str]:
    """Return true-class support, errors, and leakage e=1-Recall."""
    if population == "all":
        n = int(cm.sum())
        errors = int(n - np.trace(cm))
    else:
        index = CLASSES.index(population)
        n = int(cm[index].sum())
        errors = int(n - cm[index, index])
    if n == 0:
        return {"pixels": 0, "errors": 0, "error_rate": np.nan, "status": "undefined_zero_support"}
    return {"pixels": n, "errors": errors, "error_rate": float(errors / n), "status": "defined"}


def full_error_rate(cm: np.ndarray, population: str) -> float:
    return float(metrics(cm, population)["error_rate"])


def std_or_nan(values: np.ndarray) -> float:
    return float(values.std(ddof=1)) if len(values) == 5 and np.isfinite(values).all() else np.nan


def mean_or_nan(values: np.ndarray) -> float:
    return float(values.mean()) if len(values) == 5 and np.isfinite(values).all() else np.nan


def record_cm(row: pd.Series | dict) -> dict[str, int]:
    return {column: int(row[column]) for column in CM}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_record(path: Path) -> dict[str, object]:
    return {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path), "bytes": path.stat().st_size}


def write_csv(path: Path, frame: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format="%.17g", lineterminator="\n")


def load_inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    within_bands = cm_frame(read_csv(OLD_PROC / "boundary_within_cm.csv"), "within bands")
    cross_bands = cm_frame(read_csv(OLD_PROC / "boundary_cross_fold_cm.csv"), "cross bands")
    raw_within = cm_frame(read_csv(RAW / "within_site_confusion_matrices.csv"), "raw within")
    raw_cross = cm_frame(read_csv(RAW / "cross_site_confusion_matrices.csv"), "raw cross")
    return within_bands, cross_bands, raw_within, raw_cross


def validate_keys_and_closure(within_bands: pd.DataFrame, cross_bands: pd.DataFrame,
                              raw_within: pd.DataFrame, raw_cross: pd.DataFrame) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        checks.append({"check": name, "status": "Verified" if condition else "Not verified", "detail": detail})
        require(condition, f"{name}: {detail}")

    check("within band row count", len(within_bands) == 84, str(len(within_bands)))
    check("cross band row count", len(cross_bands) == 1260, str(len(cross_bands)))
    check("within band names", set(within_bands.band) == set(BANDS), str(sorted(within_bands.band.unique())))
    check("cross band names", set(cross_bands.band) == set(BANDS), str(sorted(cross_bands.band.unique())))
    check("within band keys unique", not within_bands.duplicated(["model", "target", "band"]).any())
    check("cross band keys unique", not cross_bands.duplicated(["model", "source", "target", "fold", "band"]).any())
    check("within key set", set(zip(within_bands.model, within_bands.target)) == set(itertools.product(MODELS, SITES)))
    check("cross key set", set(zip(cross_bands.model, cross_bands.source, cross_bands.target)) ==
          set((m, s, t) for m in MODELS for s in SITES for t in SITES if s != t))
    check("cross five folds", all(set(x.fold) == {1, 2, 3, 4, 5} and len(x) == 35
                                  for _, x in cross_bands.groupby(["model", "source", "target"])))
    raw_wp = raw_within[raw_within.result_type == "oof_pooled"].copy()
    raw_wf = raw_within[raw_within.result_type == "fold"].copy()
    check("raw within pooled rows", len(raw_wp) == 12)
    check("raw within fold rows", len(raw_wf) == 60)
    check("raw cross rows", len(raw_cross) == 180)

    for key, rows in within_bands.groupby(["model", "target"], sort=False):
        pooled = raw_wp.set_index(["model", "target"]).loc[key]
        summed = rows[CM].sum().to_numpy(dtype=np.int64).reshape(3, 3)
        check(f"within seven-band closure {key}", np.array_equal(summed, matrix(pooled)),
              f"sum={summed.tolist()} raw={matrix(pooled).reshape(-1).tolist()}")
    for key, rows in cross_bands.groupby(["model", "source", "target", "fold"], sort=False):
        raw = raw_cross.set_index(["model", "source", "target", "fold"]).loc[key]
        summed = rows[CM].sum().to_numpy(dtype=np.int64).reshape(3, 3)
        check(f"cross seven-band closure {key}", np.array_equal(summed, matrix(raw)))
    # All cross and within target supports must be the same target image support.
    for target in SITES:
        w = raw_wp[raw_wp.target == target].iloc[0]
        support = matrix(w).sum(axis=1)
        for _, row in raw_cross[raw_cross.target == target].iterrows():
            check(f"target support identity {target}/{row.model}/{row.source}/{int(row.fold)}",
                  np.array_equal(matrix(row).sum(axis=1), support))
    return checks


def build_band_tables(within_bands: pd.DataFrame, cross_bands: pd.DataFrame,
                      raw_within: pd.DataFrame, raw_cross: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    wp = raw_within[raw_within.result_type == "oof_pooled"].set_index(["model", "target"])
    cp = raw_cross.set_index(["model", "source", "target", "fold"])
    within_rows: list[dict[str, object]] = []
    cross_rows: list[dict[str, object]] = []
    for _, row in within_bands.iterrows():
        cm = matrix(row)
        for population in POPULATIONS:
            m = metrics(cm, population)
            total_cm = matrix(wp.loc[(row.model, row.target)])
            total_n = metrics(total_cm, population)["pixels"]
            within_rows.append({"model": row.model, "target": row.target, "band": row.band,
                                "population": population, **m,
                                "pixel_share": float(m["pixels"] / total_n) if total_n else np.nan,
                                "source": "", "fold": ""})
    for _, row in cross_bands.iterrows():
        cm = matrix(row)
        for population in POPULATIONS:
            m = metrics(cm, population)
            total_cm = matrix(cp.loc[(row.model, row.source, row.target, int(row.fold))])
            total_n = metrics(total_cm, population)["pixels"]
            cross_rows.append({"model": row.model, "source": row.source, "target": row.target,
                               "fold": int(row.fold), "band": row.band, "population": population, **m,
                               "pixel_share": float(m["pixels"] / total_n) if total_n else np.nan})
    within = pd.DataFrame(within_rows)
    cross = pd.DataFrame(cross_rows)
    # Summaries use the same fixed within target/band support for every source and fold.
    summary_rows: list[dict[str, object]] = []
    for key, x in cross.groupby(["model", "source", "target", "band", "population"], sort=True):
        model, source, target, band, population = key
        w = within[(within.model == model) & (within.target == target) &
                   (within.band == band) & (within.population == population)].iloc[0]
        vals_e = x.error_rate.to_numpy(dtype=float)
        vals_err = x.errors.to_numpy(dtype=float)
        n = int(w.pixels)
        e_mean = mean_or_nan(vals_e)
        err_mean = mean_or_nan(vals_err)
        within_e = float(w.error_rate) if np.isfinite(w.error_rate) else np.nan
        delta = e_mean - within_e if np.isfinite(e_mean) and np.isfinite(within_e) else np.nan
        p = float(w.pixel_share) if np.isfinite(w.pixel_share) else np.nan
        summary_rows.append({"model": model, "source": source, "target": target, "band": band,
                             "population": population, "pixels": n, "pixel_share": p,
                             "within_errors": int(w.errors), "within_error_rate": within_e,
                             "cross_errors_mean": err_mean, "cross_errors_std": std_or_nan(vals_err),
                             "cross_error_rate_mean": e_mean, "cross_error_rate_std": std_or_nan(vals_e),
                             "delta_error_rate": delta,
                             "net_added_errors_mean": err_mean - int(w.errors) if np.isfinite(err_mean) else np.nan,
                             "net_added_errors_std": std_or_nan(vals_err),
                             "net_overall_contribution": p * delta if np.isfinite(p) and np.isfinite(delta) else np.nan,
                             "n_predictions": 5, "n_defined_error_rate": int(np.isfinite(vals_e).sum()),
                             "status": "defined" if np.isfinite(e_mean) and np.isfinite(within_e) else "incomplete_five_or_zero_support"})
    summary = pd.DataFrame(summary_rows)
    overview_rows: list[dict[str, object]] = []
    for key, x in summary.groupby(["model", "target", "band", "population"], sort=True):
        model, target, band, population = key
        w = x.iloc[0]
        e = x.cross_error_rate_mean.to_numpy(dtype=float)
        d = x.delta_error_rate.to_numpy(dtype=float)
        c = x.net_overall_contribution.to_numpy(dtype=float)
        overview_rows.append({"model": model, "target": target, "band": band, "population": population,
                              "within_error_rate": float(w.within_error_rate),
                              "pixel_share": float(w.pixel_share),
                              "cross_error_rate_three_source_mean": float(e.mean()) if np.isfinite(e).all() else np.nan,
                              "delta_error_rate_three_source_mean": float(d.mean()) if np.isfinite(d).all() else np.nan,
                              "net_overall_contribution_three_source_mean": float(c.mean()) if np.isfinite(c).all() else np.nan,
                              "source_count": int(np.isfinite(e).sum()),
                              "aggregation": "equal_weight_three_sources"})
    overview = pd.DataFrame(overview_rows)
    return within, cross, summary, overview


def build_pair_table(cross: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    near = cross[cross.band == BANDS[0]].rename(columns={"error_rate": "near_error_rate", "errors": "near_errors"})
    far = cross[cross.band == BANDS[-1]].rename(columns={"error_rate": "gt6_error_rate", "errors": "gt6_errors"})
    keys = ["model", "source", "target", "fold", "population"]
    pair = near[keys + ["near_error_rate", "near_errors"]].merge(
        far[keys + ["gt6_error_rate", "gt6_errors"]], on=keys, how="outer", validate="one_to_one")
    pair["gt6_minus_near_error_rate"] = pair.gt6_error_rate - pair.near_error_rate
    pair["direction"] = np.where(pair.gt6_minus_near_error_rate > 0, "gt6_higher",
                                  np.where(pair.gt6_minus_near_error_rate < 0, "near_higher", "equal"))
    rows: list[dict[str, object]] = []
    for key, x in pair.groupby(["model", "source", "target", "population"], sort=True):
        vals = x.gt6_minus_near_error_rate.to_numpy(dtype=float)
        rows.append({"model": key[0], "source": key[1], "target": key[2], "population": key[3],
                     "n_pairs": len(vals), "n_gt6_higher": int((vals > 0).sum()),
                     "n_near_higher": int((vals < 0).sum()), "n_equal": int((vals == 0).sum()),
                     "difference_min": float(vals.min()), "difference_max": float(vals.max()),
                     "difference_mean": float(vals.mean()),
                     "status": "defined" if np.isfinite(vals).all() else "incomplete"})
    return pair, pd.DataFrame(rows)


def build_d_soybean_decomposition(within_bands: pd.DataFrame, cross_bands: pd.DataFrame) -> pd.DataFrame:
    target = "il_2023"
    w = within_bands[(within_bands.target == target)].copy()
    c = cross_bands[(cross_bands.target == target)].copy()
    rows: list[dict[str, object]] = []
    for model, source in itertools.product(MODELS, (s for s in SITES if s != target)):
        for band in BANDS:
            wr = w[(w.model == model) & (w.band == band)].iloc[0]
            wcm = matrix(wr)
            n = int(wcm[2].sum())
            w_to_corn = float(wcm[2, 0] / n) if n else np.nan
            w_to_other = float(wcm[2, 1] / n) if n else np.nan
            x = c[(c.model == model) & (c.source == source) & (c.band == band)].sort_values("fold")
            component_rows = []
            for _, cr in x.iterrows():
                cm = matrix(cr)
                denom = int(cm[2].sum())
                component_rows.append((float(cm[2, 0] / denom) if denom else np.nan,
                                       float(cm[2, 1] / denom) if denom else np.nan))
            vals = np.asarray(component_rows, dtype=float)
            means = np.asarray([mean_or_nan(vals[:, i]) for i in range(2)])
            stds = np.asarray([std_or_nan(vals[:, i]) for i in range(2)])
            rows.append({"model": model, "source": source, "target": target, "band": band,
                         "soybean_pixels": n, "within_soybean_to_corn_rate": w_to_corn,
                         "within_soybean_to_other_rate": w_to_other,
                         "cross_soybean_to_corn_rate_mean": means[0], "cross_soybean_to_corn_rate_std": stds[0],
                         "cross_soybean_to_other_rate_mean": means[1], "cross_soybean_to_other_rate_std": stds[1],
                         "delta_soybean_to_corn_rate": means[0] - w_to_corn if np.isfinite(means[0]) and np.isfinite(w_to_corn) else np.nan,
                         "delta_soybean_to_other_rate": means[1] - w_to_other if np.isfinite(means[1]) and np.isfinite(w_to_other) else np.nan,
                         "delta_soybean_error_rate": (means.sum() - w_to_corn - w_to_other) if np.isfinite(means).all() and np.isfinite(w_to_corn) and np.isfinite(w_to_other) else np.nan,
                         "n_predictions": 5, "n_defined_predictions": int(np.isfinite(vals).all(axis=1).sum())})
    result = pd.DataFrame(rows)
    result["component_sum_check"] = result.delta_soybean_to_corn_rate + result.delta_soybean_to_other_rate
    result["component_closure_abs_error"] = result.component_sum_check - result.delta_soybean_error_rate
    result["status"] = np.where(result.n_defined_predictions == 5, "defined", "incomplete_five_predictions")
    return result


def make_figures(summary: pd.DataFrame, overview: pd.DataFrame, dsoy: pd.DataFrame) -> list[Path]:
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    FIG.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    x = np.arange(len(BANDS))
    colors = {"convgru": "#0072B2", "unet3d": "#D55E00", "utae": "#009E73"}
    labels = {"convgru": "ConvGRU", "unet3d": "3D U-Net", "utae": "U-TAE"}
    fig, axes = plt.subplots(4, 2, figsize=(13, 15), sharex=True)
    for ri, target in enumerate(SITES):
        for ci, population in enumerate(("corn", "soybean")):
            ax = axes[ri, ci]
            for model in MODELS:
                q = overview[(overview.target == target) & (overview.population == population) & (overview.model == model)].set_index("band").reindex(BANDS)
                ax.plot(x, q.cross_error_rate_three_source_mean, marker="o", color=colors[model], label=labels[model] if ri == 0 and ci == 0 else None)
                ax.plot(x, q.within_error_rate, marker="x", linestyle="--", color=colors[model], alpha=0.65)
            ax.set_title(f"Target {SITE_LABELS[target]} ({CROP_LABELS[population]})")
            ax.set_ylim(bottom=0)
            ax.grid(alpha=0.25)
            if ci == 0:
                ax.set_ylabel("Leakage rate (1 - recall)")
            if ri == 3:
                ax.set_xticks(x, BANDS, rotation=25, ha="right")
                ax.set_xlabel("Distance band (pixels; >6 is open-ended)")
    model_handles = [Line2D([0], [0], color=colors[m], marker="o", label=labels[m]) for m in MODELS]
    style_handles = [Line2D([0], [0], color="black", marker="o", label="Cross-site (three-source mean)"),
                     Line2D([0], [0], color="black", marker="x", linestyle="--", label="Within-site")]
    axes[0, 0].legend(handles=model_handles + style_handles, loc="upper left", frameon=False, fontsize=8)
    fig.suptitle("Within-site and equal-weight three-source cross-site leakage by distance band", y=0.995)
    fig.tight_layout()
    path = FIG / "distance_leakage_curves_overview.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    fig, axes = plt.subplots(4, 2, figsize=(13, 15), sharex=True)
    for ri, target in enumerate(SITES):
        for ci, population in enumerate(("corn", "soybean")):
            ax = axes[ri, ci]
            for model in MODELS:
                q = overview[(overview.target == target) & (overview.population == population) & (overview.model == model)].set_index("band").reindex(BANDS)
                ax.plot(x, q.net_overall_contribution_three_source_mean, marker="o", color=colors[model], label=labels[model] if ri == 0 and ci == 0 else None)
            ax2 = ax.twinx()
            q_share = overview[(overview.target == target) & (overview.population == population) & (overview.model == MODELS[0])].set_index("band").reindex(BANDS)
            ax2.plot(x, q_share.pixel_share, color="#666666", marker="x", linestyle=":", linewidth=1.2, label="Pixel share")
            ax2.set_ylim(0, 1)
            if ci == 1:
                ax2.set_ylabel("Target-class pixel share")
            ax.axhline(0, color="black", linewidth=0.8)
            ax.set_title(f"Target {SITE_LABELS[target]} ({CROP_LABELS[population]})")
            ax.grid(alpha=0.25)
            if ci == 0:
                ax.set_ylabel("Contribution to whole-site leakage difference")
            if ri == 3:
                ax.set_xticks(x, BANDS, rotation=25, ha="right")
                ax.set_xlabel("Distance band (pixels; >6 is open-ended)")
    contribution_handles = [Line2D([0], [0], color=colors[m], marker="o", label=labels[m]) for m in MODELS]
    contribution_handles.append(Line2D([0], [0], color="#666666", marker="x", linestyle=":", label="Pixel share"))
    axes[0, 0].legend(handles=contribution_handles, loc="best", frameon=False, fontsize=8)
    fig.suptitle("Equal-weight three-source band contribution and sign", y=0.995)
    fig.tight_layout()
    path = FIG / "distance_leakage_contributions_overview.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    # D-site soybean: each panel is a model, each source has cross curves;
    # within baseline is shown once as a dashed black line.
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    source_colors = {"iw_2023": "#0072B2", "iw2_2023": "#D55E00", "ida_2023": "#009E73"}
    for ax, model in zip(axes, MODELS):
        q = summary[(summary.target == "il_2023") & (summary.population == "soybean") & (summary.model == model)]
        for source in ("iw_2023", "iw2_2023", "ida_2023"):
            r = q[q.source == source].set_index("band").reindex(BANDS)
            ax.plot(x, r.cross_error_rate_mean, marker="o", color=source_colors[source], label=f"{SITE_LABELS[source]} source")
        w = q.drop_duplicates("band").set_index("band").reindex(BANDS)
        ax.plot(x, w.within_error_rate, marker="x", linestyle="--", color="black", label="Within")
        ax.set_title(labels[model])
        ax.set_xticks(x, BANDS, rotation=25, ha="right")
        ax.grid(alpha=0.25)
        ax.set_xlabel("Distance band (pixels)")
    axes[0].set_ylabel("Soybean leakage rate (1 - recall)")
    axes[-1].legend(loc="upper left", fontsize=8, frameon=False)
    fig.suptitle("Target D soybean: source-specific leakage by distance band", y=1.02)
    fig.tight_layout()
    path = FIG / "d_soybean_source_model_leakage.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8), sharey=True)
    for ax, model in zip(axes, MODELS):
        q = dsoy[dsoy.model == model]
        for source in ("iw_2023", "iw2_2023", "ida_2023"):
            r = q[q.source == source].set_index("band").reindex(BANDS)
            ax.plot(x, r.delta_soybean_to_corn_rate, marker="o", color=source_colors[source], label=f"{SITE_LABELS[source]}: S->C")
            ax.plot(x, r.delta_soybean_to_other_rate, marker="s", linestyle="--", color=source_colors[source], label=f"{SITE_LABELS[source]}: S->O")
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title(labels[model])
        ax.set_xticks(x, BANDS, rotation=25, ha="right")
        ax.grid(alpha=0.25)
        ax.set_xlabel("Distance band (pixels)")
    axes[0].set_ylabel("Cross-site minus within leakage component")
    axes[-1].legend(loc="upper left", fontsize=7, frameon=False)
    fig.suptitle("Target D soybean: leakage-direction differences", y=1.02)
    fig.tight_layout()
    path = FIG / "d_soybean_leakage_components.png"
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    paths.append(path)
    return paths


def write_report(summary: pd.DataFrame, overview: pd.DataFrame, pair_summary: pd.DataFrame,
                 dsoy: pd.DataFrame, checks: list[dict[str, object]], paths: list[Path]) -> Path:
    # Report is deliberately descriptive and points to reproducible tables rather than
    # promoting exploratory patterns to causal claims.
    target_rows = []
    for target, population in itertools.product(SITES, ("corn", "soybean")):
        q = overview[(overview.target == target) & (overview.population == population)]
        changes = []
        for model in MODELS:
            x = q[q.model == model].set_index("band").reindex(BANDS).delta_error_rate_three_source_mean
            if np.isfinite(x).all():
                changes.append((model, float(x.iloc[-1] - x.iloc[0])))
        target_rows.append(f"- {SITE_LABELS[target]} {CROP_LABELS[population]}: 三源等权平均的 >6 与最近带差值为 " + ", ".join(f"{MODEL_LABELS[m]} {v:+.4f}" for m, v in changes) + "。")
    focal = summary[summary.population.isin(("corn", "soybean"))].copy()
    max_delta = focal.loc[focal.groupby(["model", "source", "target", "population"]).delta_error_rate.idxmax()]
    max_contribution = focal.loc[focal.groupby(["model", "source", "target", "population"]).net_overall_contribution.idxmax()]
    delta_max_counts = max_delta.band.value_counts().to_dict()
    contribution_max_counts = max_contribution.band.value_counts().to_dict()
    pairs = pair_summary[pair_summary.population.isin(("corn", "soybean"))]
    pair_counts = pairs[["n_gt6_higher", "n_near_higher", "n_equal"]].sum().astype(int).to_dict()
    far_higher_delta = 0
    near_higher_delta = 0
    for _, x in focal.groupby(["model", "source", "target", "population"]):
        x = x.set_index("band").reindex(BANDS)
        if x.delta_error_rate.iloc[-1] > x.delta_error_rate.iloc[0]:
            far_higher_delta += 1
        elif x.delta_error_rate.iloc[-1] < x.delta_error_rate.iloc[0]:
            near_higher_delta += 1
    d_high = dsoy[dsoy.band == "d>6"].copy()
    d_near = dsoy[dsoy.band == "0<d<=1"].copy()
    d_lines = []
    for model in MODELS:
        for source in ("iw_2023", "iw2_2023", "ida_2023"):
            a = d_near[(d_near.model == model) & (d_near.source == source)].iloc[0]
            b = d_high[(d_high.model == model) & (d_high.source == source)].iloc[0]
            d_lines.append(f"- {MODEL_LABELS[model]}，{SITE_LABELS[source]}源：最近带到 >6 带，大豆→玉米分量差由 {a.delta_soybean_to_corn_rate:+.4f} 变为 {b.delta_soybean_to_corn_rate:+.4f}，大豆→其他类分量差由 {a.delta_soybean_to_other_rate:+.4f} 变为 {b.delta_soybean_to_other_rate:+.4f}。")
    report = """# 3.3 第三轮探索报告：边界距离带与跨站净增错误

本报告对应 `derived / exploratory` 结果，未修改论文正文。分析复用已核验的七带整数混淆矩阵，距离定义为完整标签图中有效类别四邻域共享边到像元中心的欧氏距离；本轮未重新执行距离变换。七带范围为 `(0,1]`、`(1,2]`、`(2,3]`、`(3,4]`、`(4,5]`、`(5,6]` 和 `>6` 像元。跨站漏分率为五次预测分别计算后取均值，标准差为样本标准差；三源概览是现有三个来源的等权平均。

## 发现

距离带结果不能把“带内额外漏分率”与“全站净增错误承担比例”混为一谈。带内贡献同时受到带内像元占比影响，且允许为负。以下各站点—作物的最近带与 `>6` 带差异用于描述空间分布，不作因果解释：

""" + "\n".join(target_rows) + "\n\n" + "## D 站大豆\n\n" + "\n".join(d_lines) + "\n\n" + "D 站大豆的两项分解是大豆→玉米和大豆→其他类的类内漏分率差；两项之和逐组恢复大豆的 Δe。完整逐带、逐模型、逐来源结果见 `d_soybean_error_decomposition.csv`。四项分解的更细版本不在本轮扩展，避免把漏分率分解替代 F1 的全部变化。\n\n## 证据边界\n\n距离带矩阵闭合、目标支持量一致、五次预测覆盖和贡献加和均由本轮脚本核查。历史记录中的两处参考指纹不一致和一份 GeoTIFF 缺完整 CRS GeoKey 仍保留；本轮沿用历史数组和身份核查，没有重新执行 EDT 或修补元数据。因此空间指标状态为 Partially verified。结果可以回答额外漏分在七个固定距离带中的对应分布，以及模型和来源排序是否随带改变；不能单独区分类别组成与空间结构，也不能证明边界是错误的因果来源。\n\n## 结果文件\n\n- 距离—漏分率曲线：`figures/exploratory/sec33_round3_distance/distance_leakage_curves_overview.png`\n- 带内净贡献图：`figures/exploratory/sec33_round3_distance/distance_leakage_contributions_overview.png`\n- D 站大豆源站图：`figures/exploratory/sec33_round3_distance/d_soybean_source_model_leakage.png`\n- D 站大豆漏分方向图：`figures/exploratory/sec33_round3_distance/d_soybean_leakage_components.png`\n- 最近带与 `>6` 配对表：`nearest_vs_gt6_per_fold.csv` 及 `nearest_vs_gt6_summary.csv`\n\n"""
    report += f"""## 统一模式与例外

在 72 个模型—来源—目标—作物组合中，带内 Δe 最大值位于最近带 {delta_max_counts.get("0<d<=1", 0)} 次、第二带 {delta_max_counts.get("1<d<=2", 0)} 次、第三带 {delta_max_counts.get("2<d<=3", 0)} 次、>6 带 {delta_max_counts.get("d>6", 0)} 次；带内净贡献最大值位于最近带 {contribution_max_counts.get("0<d<=1", 0)} 次、第二带 {contribution_max_counts.get("1<d<=2", 0)} 次、第三带 {contribution_max_counts.get("2<d<=3", 0)} 次、>6 带 {contribution_max_counts.get("d>6", 0)} 次。逐次绝对漏分率的最近带与 >6 配对中，>6 较高 {pair_counts.get("n_gt6_higher", 0)} 次、最近带较高 {pair_counts.get("n_near_higher", 0)} 次、相等 {pair_counts.get("n_equal", 0)} 次；然而以本站同带漏分率为基准的 Δe 在 {far_higher_delta} 个组合中由最近带到 >6 增大，在 {near_higher_delta} 个组合中减小。这说明边界附近的绝对漏分率普遍更高，但相对本站的额外漏分仍可能在内部带更大，原因是本站基准也随距离带变化。

D 站大豆中，B 源的 ConvGRU 在中远距离带仍保持较高的 Δe，A、C 源和其他模型则更多表现为最近带较高后快速下降；3D U-Net 和 U-TAE 的 B 源也保留了部分内部额外漏分，但程度和方向不同。该差异支持模型和来源会改变空间分布，不能据此推断架构机制或边界因果。

"""
    out = SUM / "exploration-report.md"
    out.write_text(report, encoding="utf-8")
    return out


def main() -> None:
    global ROOT, PROC, SUM, FIG, OLD_PROC, OLD_SUM, RAW
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    ROOT = args.root.resolve()
    PROC = ROOT / "results/processed/sec33_round3_distance"
    SUM = ROOT / "results/summary/sec33_round3_distance"
    FIG = ROOT / "figures/exploratory/sec33_round3_distance"
    OLD_PROC = ROOT / "results/processed/sec33_exploration"
    OLD_SUM = ROOT / "results/summary/sec33_exploration"
    RAW = ROOT / "results/raw"
    within_bands, cross_bands, raw_within, raw_cross = load_inputs()
    checks = validate_keys_and_closure(within_bands, cross_bands, raw_within, raw_cross)
    within, cross, summary, overview = build_band_tables(within_bands, cross_bands, raw_within, raw_cross)
    pair, pair_summary = build_pair_table(cross)
    dsoy = build_d_soybean_decomposition(within_bands, cross_bands)

    # Contribution closure against whole-site raw matrices.
    closure_rows: list[dict[str, object]] = []
    raw_wp = raw_within[raw_within.result_type == "oof_pooled"].set_index(["model", "target"])
    raw_cp = raw_cross.set_index(["model", "source", "target", "fold"])
    for model, source, target, population in itertools.product(MODELS, SITES, SITES, POPULATIONS):
        if source == target:
            continue
        s = summary[(summary.model == model) & (summary.source == source) & (summary.target == target) & (summary.population == population)]
        wcm = matrix(raw_wp.loc[(model, target)])
        cross_cms = [matrix(raw_cp.loc[(model, source, target, fold)]) for fold in range(1, 6)]
        w_e = full_error_rate(wcm, population)
        cross_es = np.asarray([full_error_rate(cm, population) for cm in cross_cms], dtype=float)
        cross_mean = mean_or_nan(cross_es)
        expected = cross_mean - w_e if np.isfinite(cross_mean) and np.isfinite(w_e) else np.nan
        actual = float(s.net_overall_contribution.sum()) if s.net_overall_contribution.notna().all() else np.nan
        closure_rows.append({"model": model, "source": source, "target": target, "population": population,
                             "whole_within_error_rate": w_e, "whole_cross_error_rate_mean": cross_mean,
                             "whole_delta_error_rate": expected, "sum_band_contributions": actual,
                             "absolute_error": actual - expected if np.isfinite(actual) and np.isfinite(expected) else np.nan,
                             "status": "Verified" if np.isfinite(actual) and np.isfinite(expected) and abs(actual - expected) <= 1e-12 else "Not verified"})
    closure = pd.DataFrame(closure_rows)
    checks.append({"check": "band contribution closure", "status": "Verified" if closure.status.eq("Verified").all() else "Not verified",
                   "detail": f"{int(closure.status.eq('Verified').sum())}/{len(closure)} path-population records"})
    require(closure.status.eq("Verified").all(), "band contribution closure failed")
    checks.append({"check": "D soybean component closure", "status": "Verified" if (dsoy.component_closure_abs_error.abs() <= 1e-12).all() else "Not verified",
                   "detail": f"max_abs_error={dsoy.component_closure_abs_error.abs().max():.3g}"})
    require((dsoy.component_closure_abs_error.abs() <= 1e-12).all(), "D soybean component closure failed")

    PROC.mkdir(parents=True, exist_ok=True)
    SUM.mkdir(parents=True, exist_ok=True)
    write_csv(PROC / "boundary_within_cm_reused.csv", within_bands)
    write_csv(PROC / "boundary_cross_fold_cm_reused.csv", cross_bands)
    write_csv(PROC / "band_metrics_within.csv", within)
    write_csv(PROC / "band_metrics_cross_fold.csv", cross)
    write_csv(PROC / "nearest_vs_gt6_per_fold.csv", pair)
    write_csv(PROC / "d_soybean_error_decomposition.csv", dsoy)
    write_csv(SUM / "band_metrics_summary.csv", summary)
    write_csv(SUM / "three_source_overview.csv", overview)
    write_csv(SUM / "nearest_vs_gt6_summary.csv", pair_summary)
    write_csv(SUM / "d_soybean_error_decomposition.csv", dsoy)
    write_csv(SUM / "band_contribution_closure.csv", closure)
    write_csv(SUM / "checks.csv", pd.DataFrame(checks))
    fig_paths = make_figures(summary, overview, dsoy)
    report = write_report(summary, overview, pair_summary, dsoy, checks, fig_paths)
    input_paths = [OLD_PROC / "boundary_within_cm.csv", OLD_PROC / "boundary_cross_fold_cm.csv",
                   RAW / "within_site_confusion_matrices.csv", RAW / "cross_site_confusion_matrices.csv",
                   ROOT / "legacy/manuscript/HLS-Crop/src/learning/distance_band_analysis.py",
                   OLD_SUM / "boundary_manifest.json"]
    outputs = [p for p in [*PROC.glob("*.csv"), *SUM.glob("*.csv"), report, *fig_paths] if p.exists()]
    manifest = {"data_status": "derived", "analysis_status": "exploratory", "pipeline_status": "Verified",
                "spatial_metric_status": "Partially verified",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "bands": list(BANDS), "band_endpoint_rule": "(left,right], final band >6, pixel unit",
                "distance_definition": "reused class-shared-edge center EDT definition; not rerun",
                "class_order": list(CLASSES), "populations": list(POPULATIONS), "std_ddof": 1,
                "within_rule": "sum same-band pooled OOF CM before leakage calculation",
                "cross_rule": "five separate fold leakage rates, then arithmetic mean and sample SD",
                "delta_rule": "cross-site mean leakage minus within-site leakage",
                "contribution_rule": "target-class band pixel share times delta leakage rate",
                "source_aggregation": "equal weight of exactly three sources; no pooling of fifteen predictions",
                "historical_limitations": {"original_edt_rerun": False, "reference_fingerprint_mismatches": 2,
                                           "missing_geotiff_tags": 1, "metadata_repaired": False},
                "inputs": [file_record(p) for p in input_paths],
                "script": file_record(Path(__file__)),
                "outputs": [file_record(p) for p in outputs],
                "checks": {"count": len(checks), "all_verified": all(x["status"] == "Verified" for x in checks)}}
    (SUM / "run_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Verified: {len(within)} within-band rows, {len(cross)} cross-band rows, {len(summary)} summaries; outputs in {SUM}")


if __name__ == "__main__":
    main()

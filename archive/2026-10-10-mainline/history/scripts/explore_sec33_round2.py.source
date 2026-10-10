#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""3.3 second-round exploratory plots and D-site soybean error decomposition.

All products are derived / exploratory.  The script reuses the frozen AREA_MN
group matrices from the first raw-scale exploration and never reruns inference.
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
SOURCE_SUM = ROOT / "results/summary/sec33_f1_raw_scale"
SOURCE_PROC = ROOT / "results/processed/sec33_f1_raw_scale"
SUM = ROOT / "results/summary/sec33_round2"
PROC = ROOT / "results/processed/sec33_round2"
FIG = ROOT / "figures/exploratory/sec33_round2"

SITES = ["iw_2023", "iw2_2023", "ida_2023", "il_2023"]
SITE_LABELS = {"iw_2023": "A", "iw2_2023": "B", "ida_2023": "C", "il_2023": "D"}
MODELS = ["convgru", "unet3d", "utae"]
MODEL_LABELS = {"convgru": "ConvGRU", "unet3d": "3D U-Net", "utae": "U-TAE"}
CROPS = ["corn", "soybean"]
CROP_LABELS = {"corn": "玉米", "soybean": "大豆"}
CLASSES = ["corn", "other", "soybean"]
CLASS_LABELS = {"corn": "玉米", "other": "其它", "soybean": "大豆"}
GROUPS = ["low", "mid", "high"]
GROUP_LABELS = {"low": "低", "mid": "中", "high": "高", "missing": "缺类"}
GROUP_SHAPES = {"low": "o", "mid": "s", "high": "^"}
CM_FIELDS = [f"cm_{i}{j}" for i in range(3) for j in range(3)]
COMPONENTS = ["soy_to_corn", "soy_to_other", "corn_to_soy", "other_to_soy"]
COMPONENT_LABELS = {
    "soy_to_corn": "大豆→玉米",
    "soy_to_other": "大豆→其它",
    "corn_to_soy": "玉米→大豆",
    "other_to_soy": "其它→大豆",
}
MODEL_COLORS = {"convgru": "#7B3FA0", "unet3d": "#1B9E9E", "utae": "#E8731A"}
SOURCE_COLORS = {"iw_2023": "#2166AC", "iw2_2023": "#C51B7D", "ida_2023": "#388443"}
SOURCE_LABELS = {"iw_2023": "A源", "iw2_2023": "B源", "ida_2023": "C源"}
CLASS_COLORS = {"corn": "#F2C14E", "soybean": "#4C9F70", "other": "#BDBDBD"}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, float_precision="round_trip")


def cm_from_row(row: pd.Series) -> np.ndarray:
    return np.array([[int(row[f"cm_{i}{j}"]) for j in range(3)] for i in range(3)], dtype=np.int64)


def f1_from_cm(cm: np.ndarray, crop: str) -> float:
    idx = {"corn": 0, "other": 1, "soybean": 2}[crop]
    tp = float(cm[idx, idx])
    denom = float(cm[idx, :].sum() + cm[:, idx].sum())
    return 2 * tp / denom if denom > 0 else np.nan


def error_components(cm: np.ndarray) -> dict[str, float]:
    """Return soybean F1 components and source-class denominators.

    The four component numerators are the requested directions.  Each is
    divided by Z = 2TP + FP + FN, so their sum equals 1 - soybean F1.
    """
    tp = float(cm[2, 2])
    values = {
        "soy_to_corn_pixels": float(cm[2, 0]),
        "soy_to_other_pixels": float(cm[2, 1]),
        "corn_to_soy_pixels": float(cm[0, 2]),
        "other_to_soy_pixels": float(cm[1, 2]),
        "true_corn_pixels": float(cm[0, :].sum()),
        "true_other_pixels": float(cm[1, :].sum()),
        "true_soybean_pixels": float(cm[2, :].sum()),
        "predicted_soybean_pixels": float(cm[:, 2].sum()),
        "soybean_tp_pixels": tp,
    }
    values["Z"] = 2 * tp + sum(values[k] for k in (
        "soy_to_corn_pixels", "soy_to_other_pixels", "corn_to_soy_pixels", "other_to_soy_pixels"
    ))
    z = values["Z"]
    for name, pixels in (("soy_to_corn", "soy_to_corn_pixels"), ("soy_to_other", "soy_to_other_pixels"),
                         ("corn_to_soy", "corn_to_soy_pixels"), ("other_to_soy", "other_to_soy_pixels")):
        values[f"{name}_component"] = values[pixels] / z if z > 0 else np.nan
    values["soybean_f1"] = 2 * tp / z if z > 0 else np.nan
    true_soy = values["true_soybean_pixels"]
    pred_soy = values["predicted_soybean_pixels"]
    values["soybean_recall"] = tp / true_soy if true_soy > 0 else np.nan
    values["soybean_precision"] = tp / pred_soy if pred_soy > 0 else np.nan
    for name, pixels, denominator in (
        ("soy_to_corn", "soy_to_corn_pixels", "true_soybean_pixels"),
        ("soy_to_other", "soy_to_other_pixels", "true_soybean_pixels"),
        ("corn_to_soy", "corn_to_soy_pixels", "true_corn_pixels"),
        ("other_to_soy", "other_to_soy_pixels", "true_other_pixels"),
    ):
        values[f"{name}_rate_by_true_class"] = values[pixels] / values[denominator] if values[denominator] > 0 else np.nan
    values["component_sum"] = sum(values[f"{name}_component"] for name in COMPONENTS) if z > 0 else np.nan
    values["component_sum_error"] = values["component_sum"] - (1 - values["soybean_f1"]) if np.isfinite(values["soybean_f1"]) else np.nan
    return values


def safe_mean(values: pd.Series) -> float:
    return float(values.mean()) if values.notna().all() else np.nan


def safe_std(values: pd.Series) -> float:
    return float(values.std(ddof=1)) if values.notna().all() and len(values) == 5 else np.nan


def direction_label(values: pd.Series) -> str:
    x = np.asarray(values, dtype=float)
    if len(x) != 5 or not np.isfinite(x).all():
        return "undefined"
    pos, neg, zero = int((x > 0).sum()), int((x < 0).sum()), int((x == 0).sum())
    if pos == 5:
        return "all_positive"
    if neg == 5:
        return "all_negative"
    if pos >= 4:
        return "mostly_positive"
    if neg >= 4:
        return "mostly_negative"
    if zero == 5:
        return "all_zero"
    return "mixed"


def validate_component_sum(frame: pd.DataFrame, tolerance: float = 1e-12) -> tuple[bool, float]:
    check = frame[[f"{c}_component" for c in COMPONENTS]].sum(axis=1) - (1 - frame["soybean_f1"])
    maximum = float(np.nanmax(np.abs(check))) if len(check) else 0.0
    return bool(maximum <= tolerance), maximum


def aggregate_decomposition(within: pd.DataFrame, cross: pd.DataFrame, features: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build per-prediction and per-source summary tables for D-site soybean."""
    within = within[(within.target == "il_2023") & (within.crop == "soybean")].copy()
    cross = cross[(cross.target == "il_2023") & (cross.crop == "soybean")].copy()
    features = features[(features.target == "il_2023") & (features.crop == "soybean")].copy()
    feature_cols = ["patches", "feature_median", "feature_min", "feature_max", "corn_pixels", "other_pixels", "soybean_pixels", "corn_ratio", "other_ratio", "soybean_ratio"]
    feature_lookup = features.set_index("group")[feature_cols].to_dict("index")
    rows = []
    for _, row in within.iterrows():
        item = {"kind": "within", "model": row.model, "source": "within", "target": row.target, "crop": row.crop,
                "group": row.group, "fold": np.nan}
        item.update(error_components(cm_from_row(row)))
        item.update(feature_lookup.get(row.group, {}))
        rows.append(item)
    for _, row in cross.iterrows():
        item = {"kind": "cross", "model": row.model, "source": row.source, "target": row.target, "crop": row.crop,
                "group": row.group, "fold": int(row.fold)}
        item.update(error_components(cm_from_row(row)))
        item.update(feature_lookup.get(row.group, {}))
        rows.append(item)
    detail = pd.DataFrame(rows)
    summaries = []
    for (model, source, group), z in detail[detail.kind == "cross"].groupby(["model", "source", "group"], sort=False):
        base = detail[(detail.kind == "within") & (detail.model == model) & (detail.group == group)]
        if len(base) != 1 or len(z) != 5 or set(z.fold) != {1, 2, 3, 4, 5}:
            raise ValueError(f"D soybean coverage mismatch: {model}/{source}/{group}")
        w = base.iloc[0]
        item = {"model": model, "source": source, "target": "il_2023", "crop": "soybean", "group": group,
                "n_predictions": len(z), "within_f1": w.soybean_f1, "within_precision": w.soybean_precision,
                "within_recall": w.soybean_recall, "within_Z": w.Z}
        for field in ["feature_median", "feature_min", "feature_max", "patches", "corn_pixels", "other_pixels", "soybean_pixels", "corn_ratio", "other_ratio", "soybean_ratio"]:
            item[field] = w[field]
        item["cross_f1_mean"] = safe_mean(z.soybean_f1)
        item["cross_f1_std"] = safe_std(z.soybean_f1)
        item["cross_f1_min"] = float(z.soybean_f1.min())
        item["cross_f1_max"] = float(z.soybean_f1.max())
        item["delta_f1"] = item["within_f1"] - item["cross_f1_mean"]
        item["delta_f1_min"] = item["within_f1"] - item["cross_f1_max"]
        item["delta_f1_max"] = item["within_f1"] - item["cross_f1_min"]
        for field in ["Z", "true_corn_pixels", "true_other_pixels", "true_soybean_pixels", "predicted_soybean_pixels", "soybean_tp_pixels"]:
            item[f"cross_{field}_mean"] = safe_mean(z[field])
        for component in COMPONENTS:
            col = f"{component}_component"
            item[f"within_{col}"] = w[col]
            item[f"cross_{col}_mean"] = safe_mean(z[col])
            item[f"cross_{col}_std"] = safe_std(z[col])
            item[f"cross_{col}_min"] = float(z[col].min()) if z[col].notna().all() else np.nan
            item[f"cross_{col}_max"] = float(z[col].max()) if z[col].notna().all() else np.nan
            item[f"{component}_delta"] = item[f"cross_{col}_mean"] - item[f"within_{col}"] if np.isfinite(item[f"cross_{col}_mean"]) and np.isfinite(item[f"within_{col}"]) else np.nan
            fold_diff = z[col] - w[col]
            item[f"{component}_direction"] = direction_label(fold_diff)
        item["component_delta_sum"] = sum(item[f"{c}_delta"] for c in COMPONENTS)
        item["delta_recovery_error"] = item["component_delta_sum"] - item["delta_f1"]
        item["component_delta_status"] = "defined" if np.isfinite(item["delta_recovery_error"]) else "undefined"
        summaries.append(item)
    return detail, pd.DataFrame(summaries)


def build_plot_data(summary_source: Path = SOURCE_SUM) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    group = read_csv(summary_source / "group_f1_difference.csv")
    means = read_csv(summary_source / "three_source_means.csv")
    features = read_csv(summary_source / "group_features.csv")
    plot = means[means.group.isin(GROUPS)].merge(
        features[["target", "crop", "group", "feature_median", "patches", "corn_ratio", "other_ratio", "soybean_ratio"]],
        on=["target", "crop", "group"], how="left", validate="many_to_one"
    )
    plot["target_label"] = plot.target.map(SITE_LABELS)
    plot["crop_label"] = plot.crop.map(CROP_LABELS)
    plot["group_order"] = plot.group.map({g: i for i, g in enumerate(GROUPS)})
    composition = features[features.group.isin(GROUPS)].copy()
    composition["target_label"] = composition.target.map(SITE_LABELS)
    composition["crop_label"] = composition.crop.map(CROP_LABELS)
    source = group[(group.target == "il_2023") & (group.crop == "soybean") & group.group.isin(GROUPS)].copy()
    source["source_label"] = source.source.map(SOURCE_LABELS)
    return plot, composition, source


def key_contrasts(summary: pd.DataFrame, detail: pd.DataFrame) -> pd.DataFrame:
    """Compact high-minus-low diagnostics for every D-soy model/source pair."""
    rows = []
    for (model, source), z in summary[summary.group.isin(GROUPS)].groupby(["model", "source"], sort=False):
        x = z.set_index("group").loc[["low", "high"]]
        item = {"model": model, "source": source, "target": "il_2023", "crop": "soybean",
                "low_delta_f1": x.loc["low", "delta_f1"], "high_delta_f1": x.loc["high", "delta_f1"],
                "high_minus_low_delta_f1": x.loc["high", "delta_f1"] - x.loc["low", "delta_f1"]}
        for component in COMPONENTS:
            item[f"low_{component}_delta"] = x.loc["low", f"{component}_delta"]
            item[f"high_{component}_delta"] = x.loc["high", f"{component}_delta"]
            item[f"high_minus_low_{component}_delta"] = x.loc["high", f"{component}_delta"] - x.loc["low", f"{component}_delta"]
            item[f"high_{component}_direction"] = x.loc["high", f"{component}_direction"]
            low_base = detail[(detail.kind == "within") & (detail.model == model) & (detail.group == "low")].iloc[0][f"{component}_component"]
            high_base = detail[(detail.kind == "within") & (detail.model == model) & (detail.group == "high")].iloc[0][f"{component}_component"]
            low_folds = detail[(detail.kind == "cross") & (detail.model == model) & (detail.source == source) & (detail.group == "low")].set_index("fold")[f"{component}_component"] - low_base
            high_folds = detail[(detail.kind == "cross") & (detail.model == model) & (detail.source == source) & (detail.group == "high")].set_index("fold")[f"{component}_component"] - high_base
            item[f"high_minus_low_{component}_direction"] = direction_label(high_folds - low_folds)
        item["dominant_abs_high_minus_low_component"] = max(COMPONENTS, key=lambda c: abs(item[f"high_minus_low_{c}_delta"]))
        rows.append(item)
    return pd.DataFrame(rows)


def setup_matplotlib():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "font.family": ["Times New Roman", "SimSun"], "font.size": 8.5,
        "axes.unicode_minus": False, "axes.linewidth": 0.6,
        "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "pdf.fonttype": 42, "savefig.dpi": 250,
    })
    return plt


def plot_overall(plot: pd.DataFrame, out_dir: Path) -> list[Path]:
    plt = setup_matplotlib()
    import matplotlib.lines as mlines
    import matplotlib.patches as mpatches
    paths = []
    for metric in ["absolute", "delta"]:
        fig, axes = plt.subplots(4, 2, figsize=(8.4, 11.0), sharex=False, sharey=True)
        axes = np.asarray(axes)
        for ax, (key, z) in zip(axes.flat, plot.groupby(["target", "crop"], sort=False)):
            target, crop = key
            for model in MODELS:
                unit = z[z.model == model].sort_values("feature_median")
                color = MODEL_COLORS[model]
                field = "cross_f1_mean" if metric == "absolute" else "delta_f1"
                ax.plot(unit.feature_median, unit[field], color=color, lw=1.1, marker="o", ms=3.5, label=MODEL_LABELS[model])
                if metric == "absolute":
                    ax.plot(unit.feature_median, unit.within_f1, color=color, lw=0.9, ls="--", marker="", alpha=.85)
                for _, r in unit.iterrows():
                    ax.annotate(GROUP_LABELS[r.group], (r.feature_median, r[field]), xytext=(2, 3), textcoords="offset points", fontsize=7, color=color)
            ax.set_title(f"目标站 {SITE_LABELS[target]} · {CROP_LABELS[crop]}", fontsize=9)
            ax.grid(axis="y", alpha=.2)
            ax.set_xlabel("AREA_MN 中位数 / ha")
            ax.set_ylabel("F1" if metric == "absolute" else "ΔF1")
            if metric == "absolute":
                ax.set_ylim(0.35, 1.0)
            else:
                ax.axhline(0, color="#555555", lw=.5)
                ax.set_ylim(float(min(-.02, plot.delta_f1.min() - .01)), float(max(.08, plot.delta_f1.max() + .01)))
        handles = [mlines.Line2D([], [], color=MODEL_COLORS[m], marker="o", lw=1.1, label=MODEL_LABELS[m]) for m in MODELS]
        if metric == "absolute":
            handles.append(mlines.Line2D([], [], color="#444444", ls="--", lw=.9, label="同组本站 F1"))
        fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .015), ncol=4, frameon=False)
        caption = ("实线为三个来源等权平均跨站 F1；虚线为同组本站 F1。点旁标注低/中/高组，各站阈值独立。"
                   if metric == "absolute" else
                   "实线为三个来源等权平均跨站 F1 与同组本站 F1 的 ΔF1；点旁标注低/中/高组，各站阈值独立。")
        fig.text(.5, .002, caption, ha="center", fontsize=8)
        fig.subplots_adjust(left=.09, right=.98, bottom=.08, top=.97, hspace=.35, wspace=.22)
        stem = "overall_absolute_f1_by_area_mn" if metric == "absolute" else "overall_delta_f1_by_area_mn"
        for ext in ["png", "pdf"]:
            path = out_dir / f"{stem}.{ext}"
            fig.savefig(path, bbox_inches="tight")
            paths.append(path)
        plt.close(fig)
    return paths


def plot_composition(composition: pd.DataFrame, out_dir: Path) -> list[Path]:
    plt = setup_matplotlib()
    fig, axes = plt.subplots(4, 2, figsize=(8.4, 10.5), sharey=True)
    for ax, (key, z) in zip(np.asarray(axes).flat, composition.groupby(["target", "crop"], sort=False)):
        z = z.set_index("group").reindex(GROUPS)
        bottom = np.zeros(3)
        for cls in ["corn", "soybean", "other"]:
            values = z[f"{cls}_ratio"].to_numpy(float)
            ax.bar(np.arange(3), values, bottom=bottom, color=CLASS_COLORS[cls], width=.65, label=CLASS_LABELS[cls])
            bottom += values
        ax.set_title(f"目标站 {SITE_LABELS[key[0]]} · {CROP_LABELS[key[1]]}", fontsize=9)
        ax.set_xticks(np.arange(3), [GROUP_LABELS[g] for g in GROUPS])
        ax.set_ylim(0, 1)
        ax.set_ylabel("参考像元占比")
        ax.grid(axis="y", alpha=.2)
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        ax2.set_yticks([])
        ax2.set_ylabel("AREA_MN / ha", color="#555555")
        for x, (_, row) in enumerate(z.iterrows()):
            ax.text(x, 1.02, f"{row.feature_median:.1f}", ha="center", va="bottom", fontsize=7, color="#555555")
    handles = [plt.Rectangle((0, 0), 1, 1, color=CLASS_COLORS[c], label=CLASS_LABELS[c]) for c in ["corn", "soybean", "other"]]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .01), ncol=3, frameon=False)
    fig.text(.5, .002, "柱顶数字为该组 AREA_MN 中位数（ha）；组成按参考像元计。", ha="center", fontsize=8)
    fig.subplots_adjust(left=.09, right=.93, bottom=.08, top=.97, hspace=.42, wspace=.22)
    paths = []
    for ext in ["png", "pdf"]:
        path = out_dir / f"composition_by_area_mn.{ext}"
        fig.savefig(path, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def plot_d_source(source: pd.DataFrame, out_dir: Path) -> list[Path]:
    plt = setup_matplotlib()
    paths = []
    fig, axes = plt.subplots(2, 3, figsize=(10.0, 6.5), sharex=True)
    for col, model in enumerate(MODELS):
        z = source[source.model == model]
        ax_top, ax_bottom = axes[0, col], axes[1, col]
        base = z.drop_duplicates("group").set_index("group").reindex(GROUPS)
        x = np.arange(3)
        ax_top.plot(x, base.within_f1, color="#333333", ls="--", lw=1.0, marker="o", ms=3, label="本站 F1")
        for source_id in ["iw_2023", "iw2_2023", "ida_2023"]:
            u = z[z.source == source_id].set_index("group").reindex(GROUPS)
            ax_top.errorbar(x, u.cross_f1_mean, yerr=u.cross_f1_std, color=SOURCE_COLORS[source_id], marker="o", ms=3.5, capsize=2, lw=1.0, label=SOURCE_LABELS[source_id])
            ax_bottom.errorbar(x, u.delta_f1, yerr=u.cross_f1_std, color=SOURCE_COLORS[source_id], marker="o", ms=3.5, capsize=2, lw=1.0)
        ax_top.set_title(MODEL_LABELS[model], fontsize=9)
        ax_top.set_ylim(.45, 1.0); ax_top.grid(axis="y", alpha=.2); ax_top.set_ylabel("F1")
        ax_bottom.axhline(0, color="#555555", lw=.5); ax_bottom.grid(axis="y", alpha=.2); ax_bottom.set_ylabel("ΔF1")
        ax_bottom.set_xticks(x, [GROUP_LABELS[g] for g in GROUPS]); ax_bottom.set_xlabel("AREA_MN 组")
        ax_bottom.set_ylim(-.02, max(.16, float(z.delta_f1.max() + .015)))
    handles = [plt.Line2D([], [], color="#333333", ls="--", marker="o", lw=1, label="本站 F1")]
    handles += [plt.Line2D([], [], color=SOURCE_COLORS[s], marker="o", lw=1, label=SOURCE_LABELS[s]) for s in ["iw_2023", "iw2_2023", "ida_2023"]]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .01), ncol=4, frameon=False)
    fig.text(.5, .002, "D站大豆；上排为跨站五次 F1 均值，误差线为五次样本标准差；下排 ΔF1 = 本站 F1 − 跨站均值。", ha="center", fontsize=8)
    fig.subplots_adjust(left=.07, right=.98, bottom=.12, top=.94, hspace=.28, wspace=.2)
    for ext in ["png", "pdf"]:
        path = out_dir / f"d_soybean_source_f1_delta.{ext}"
        fig.savefig(path, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def plot_d_components(summary: pd.DataFrame, out_dir: Path) -> list[Path]:
    plt = setup_matplotlib()
    component_colors = {"soy_to_corn": "#D95F02", "soy_to_other": "#7570B3", "corn_to_soy": "#1B9E77", "other_to_soy": "#E7298A"}
    fig, axes = plt.subplots(3, 3, figsize=(10.0, 9.0), sharex=True, sharey=True)
    y_max = max(.01, float(np.nanmax(np.abs(summary[[f"{c}_delta" for c in COMPONENTS]].to_numpy()))))
    for ax, (key, z) in zip(np.asarray(axes).flat, summary.groupby(["model", "source"], sort=False)):
        model, source_id = key
        u = z.set_index("group").reindex(GROUPS)
        x = np.arange(3)
        for component in COMPONENTS:
            ax.plot(x, u[f"{component}_delta"], color=component_colors[component], marker="o", ms=3, lw=1.0, label=COMPONENT_LABELS[component])
        ax.plot(x, u.delta_f1, color="#222222", marker="x", ms=4, lw=1.2, ls="--", label="ΔF1")
        ax.axhline(0, color="#555555", lw=.5)
        ax.set_title(f"{MODEL_LABELS[model]} · {SOURCE_LABELS[source_id]}", fontsize=9)
        ax.set_xticks(x, [GROUP_LABELS[g] for g in GROUPS]); ax.grid(axis="y", alpha=.2)
        ax.set_ylim(-max(.01, y_max * 1.25), max(.01, y_max * 1.25))
        ax.set_ylabel("跨站分量均值 − 本站分量")
    handles = [plt.Line2D([], [], color={"soy_to_corn": "#D95F02", "soy_to_other": "#7570B3", "corn_to_soy": "#1B9E77", "other_to_soy": "#E7298A"}[c], marker="o", lw=1, label=COMPONENT_LABELS[c]) for c in COMPONENTS]
    handles.append(plt.Line2D([], [], color="#222222", marker="x", ls="--", lw=1.2, label="ΔF1"))
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(.5, .005), ncol=3, frameon=False)
    fig.text(.5, .0, "四项为 F1 差距的误差分量，不表示因果贡献；均值先对五次预测分别计算后取算术平均。", ha="center", fontsize=8)
    fig.subplots_adjust(left=.08, right=.98, bottom=.1, top=.96, hspace=.35, wspace=.23)
    paths = []
    for ext in ["png", "pdf"]:
        path = out_dir / f"d_soybean_error_components.{ext}"
        fig.savefig(path, bbox_inches="tight")
        paths.append(path)
    plt.close(fig)
    return paths


def write_report(plot: pd.DataFrame, composition: pd.DataFrame, summary: pd.DataFrame, detail: pd.DataFrame, checks: pd.DataFrame, key: pd.DataFrame, path: Path):
    ordered = summary[summary.group.isin(GROUPS)].copy()
    d = ordered[(ordered.model == "convgru") & (ordered.source == "iw2_2023")].set_index("group")
    lines = [
        "# 3.3 第二轮探索报告：探索图与 D 站大豆误差分解",
        "",
        "本报告对应 `derived / exploratory` 结果，不写入论文正文。所有图和表均复用上一轮冻结的 AREA_MN 分组与整数混淆矩阵；不重新推理。",
        "",
        "## 证据范围",
        "",
        f"D站大豆覆盖 {len(ordered)} 个模型—来源—有序组组合和 {len(detail[detail.kind == 'cross'])} 次跨站预测。四项分量闭合核查最大绝对误差为 {checks.loc[checks.check == 'component_delta_sum_recovers_delta_f1', 'maximum_abs_error'].iloc[0]:.3g}。",
        "",
        "## 科学问题判断",
        "",
        "1. 总体关系适合作为 3.3 的主体证据：上一轮的高组 ΔF1 较低关系可由两张总体图直观呈现，但应同时保留本站 F1、三源等权平均跨站 F1 和 ΔF1。该关系是跨站差距与目标条件的对应关系，不足以证明 AREA_MN 的独立作用。",
        "2. D站大豆的例外需要拆开本站与跨站变化。B源 ConvGRU 的低—高组跨站 F1变化、本站 F1变化和 ΔF1变化分别见 D站分源图；误差分量图和底表进一步显示差距变化对应哪一类方向的 F1分量变化。",
        "3. 模型与来源差异可以解释到固定目标组的绝对 F1、ΔF1 和四类分量对应关系。来源排序仍是同一跨站差异的两种表达，不能把跨站 F1 与 ΔF1 当作两个独立发现。模型结构本身不作为机制证据。",
        "4. 各 AREA_MN 组同时发生类别组成变化，因此现有结果不能区分组成与空间结构的作用。组成对照图用于限定解释强度。",
        "5. 现有结果已足以支撑短文 3.3 的探索性证据主线，但正式正文仍需作者决定保留哪些图表和两三个发现。边界分带本轮没有展开；只有在需要解释某个明确的误分去向时，才值得作为最小补充。",
        "",
        "## D站大豆重点核对",
        "",
    ]
    if len(d) == 3:
        lines.append("B源 ConvGRU 的低、中、高组数值（原尺度）为：")
        for g in GROUPS:
            r = d.loc[g]
            lines.append(f"- {GROUP_LABELS[g]}组：本站 F1={r.within_f1:.4f}，跨站 F1={r.cross_f1_mean:.4f}，ΔF1={r.delta_f1:.4f}；四项分量差值之和={r.component_delta_sum:.4f}。")
        lines.append("")
    lines.extend([
        "关键高低组对照（误差分量的绝对变化最大项）为：",
    ])
    for _, r in key.iterrows():
        lines.append(f"- {MODEL_LABELS[r.model]}、{SOURCE_LABELS[r.source]}：ΔF1高−低={r.high_minus_low_delta_f1:.4f}；最大绝对分量变化为{COMPONENT_LABELS[r.dominant_abs_high_minus_low_component]}（{r[f'high_minus_low_{r.dominant_abs_high_minus_low_component}_delta']:.4f}）；该高低组变化在五次预测中为{r[f'high_minus_low_{r.dominant_abs_high_minus_low_component}_direction']}。")
    lines.extend([
        "",
        "误差分量的正负和五次方向一致性见 `d_soybean_error_components_summary.csv`；四项按 Z 归一化，不能替代按真实类别像元数归一化的误分类率。负值表示该分量在跨站均值中低于本站基准，不能解释为单独的因果贡献。",
        "",
        "## 限制与最小后续方案",
        "",
        "当前结果只能报告空间条件、类别组成、模型和来源之间的对应关系。若作者需要区分组成与结构，最小补充应在一个明确的 D站大豆例外上，按三类组成中的两个独立占比匹配低、高组后复算同一误差分量；边界分析只有在误分去向仍无法解释时才有必要。",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build(root: Path = ROOT):
    within = read_csv(root / "results/processed/sec33_f1_raw_scale/within_group_cm.csv")
    cross = read_csv(root / "results/processed/sec33_f1_raw_scale/cross_group_fold_cm.csv")
    features = read_csv(root / "results/summary/sec33_f1_raw_scale/group_features.csv")
    plot, composition, source = build_plot_data(root / "results/summary/sec33_f1_raw_scale")
    detail, summary = aggregate_decomposition(within, cross, features)
    key = key_contrasts(summary, detail)
    ok_detail, max_detail = validate_component_sum(detail[detail.kind == "cross"])
    delta_errors = summary["delta_recovery_error"].abs()
    ok_delta = bool(delta_errors.max() <= 1e-12)
    checks = pd.DataFrame([
        {"check": "d_soybean_within_coverage", "status": "Verified", "n": len(within[(within.target == "il_2023") & (within.crop == "soybean")]), "maximum_abs_error": 0.0},
        {"check": "d_soybean_cross_coverage", "status": "Verified", "n": len(cross[(cross.target == "il_2023") & (cross.crop == "soybean")]), "maximum_abs_error": 0.0},
        {"check": "component_sum_equals_one_minus_f1", "status": "Verified" if ok_detail else "Not verified", "n": int((detail.kind == "cross").sum()), "maximum_abs_error": max_detail},
        {"check": "component_delta_sum_recovers_delta_f1", "status": "Verified" if ok_delta else "Not verified", "n": len(summary), "maximum_abs_error": float(delta_errors.max())},
        {"check": "five_prediction_direction_counts", "status": "Verified" if (summary.n_predictions == 5).all() else "Not verified", "n": len(summary), "maximum_abs_error": 0.0},
        {"check": "missing_group_retained", "status": "Verified" if "missing" in set(detail.group) else "Not verified", "n": int((detail.group == "missing").sum()), "maximum_abs_error": 0.0},
    ])
    return {"within": within, "cross": cross, "features": features, "plot": plot, "composition": composition, "source": source, "detail": detail, "summary": summary, "key": key, "checks": checks}


def output_tables(data: dict[str, pd.DataFrame], root: Path = ROOT):
    PROC.mkdir(parents=True, exist_ok=True); SUM.mkdir(parents=True, exist_ok=True); FIG.mkdir(parents=True, exist_ok=True)
    tables = {
        PROC / "d_soybean_components_per_prediction.csv": data["detail"],
        SUM / "d_soybean_error_components_summary.csv": data["summary"],
        SUM / "d_soybean_key_contrasts.csv": data["key"],
        SUM / "d_soybean_error_component_checks.csv": data["checks"],
        SUM / "overall_relation_plot_data.csv": data["plot"],
        SUM / "composition_plot_data.csv": data["composition"],
        SUM / "d_soybean_source_plot_data.csv": data["source"],
    }
    for path, frame in tables.items():
        if path.exists():
            raise FileExistsError(f"Refusing to overwrite existing result: {path}")
        frame.to_csv(path, index=False, float_format="%.17g", na_rep="NA", lineterminator="\n")
    return list(tables)


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true", help="calculate and validate without writing")
    parser.add_argument("--append-key", action="store_true", help="add the compact key-contrast table to an existing run")
    args = parser.parse_args(argv)
    data = build(ROOT)
    if not data["checks"].status.eq("Verified").all():
        raise RuntimeError("A second-round check did not pass")
    print(json.dumps({"status": "Verified", "tables": {k: len(v) for k, v in data.items() if isinstance(v, pd.DataFrame)}, "checks": len(data["checks"])}, ensure_ascii=False, indent=2))
    if args.check_only:
        return
    source_paths = [SOURCE_PROC / "within_group_cm.csv", SOURCE_PROC / "cross_group_fold_cm.csv", SOURCE_SUM / "group_features.csv", SOURCE_SUM / "group_f1_difference.csv", SOURCE_SUM / "three_source_means.csv"]
    manifest_path = SUM / "run_manifest.json"
    if args.append_key:
        key_path = SUM / "d_soybean_key_contrasts.csv"
        # Refresh this explicitly requested derived table when diagnostics change;
        # the normal generation path still refuses to overwrite a completed run.
        data["key"].to_csv(key_path, index=False, float_format="%.17g", na_rep="NA", lineterminator="\n")
        write_report(data["plot"], data["composition"], data["summary"], data["detail"], data["checks"], data["key"], SUM / "exploration-report.md")
        refreshed_figures = []
        refreshed_figures += plot_overall(data["plot"], FIG)
        refreshed_figures += plot_composition(data["composition"], FIG)
        refreshed_figures += plot_d_source(data["source"], FIG)
        refreshed_figures += plot_d_components(data["summary"], FIG)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["script"] = {"path": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))}
        manifest["outputs"] = [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in [Path(x["path"]) if Path(x["path"]).is_absolute() else ROOT / x["path"] for x in manifest["outputs"]]]
        extra = [key_path, SUM / "exploration-report.md", SUM / "README.md"] + refreshed_figures
        known = {x["path"] for x in manifest["outputs"]}
        for p in extra:
            rel = str(p.relative_to(ROOT))
            if rel not in known:
                manifest["outputs"].append({"path": rel, "sha256": sha(p)})
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Appended key contrasts and refreshed the exploratory report.")
        return
    if manifest_path.exists() or any(p.exists() for p in [PROC / "d_soybean_components_per_prediction.csv", SUM / "d_soybean_error_components_summary.csv"]):
        raise FileExistsError("Second-round outputs already exist; preserve them and audit before rerunning.")
    written = output_tables(data, ROOT)
    plot_files = []
    plot_files += plot_overall(data["plot"], FIG)
    plot_files += plot_composition(data["composition"], FIG)
    plot_files += plot_d_source(data["source"], FIG)
    plot_files += plot_d_components(data["summary"], FIG)
    report = SUM / "exploration-report.md"
    write_report(data["plot"], data["composition"], data["summary"], data["detail"], data["checks"], data["key"], report)
    readme = SUM / "README.md"
    readme.write_text("""# 3.3 第二轮探索结果\n\n本目录保存 AREA_MN 原尺度结果的探索图数据及 D 站大豆四类混淆去向分解，均为 `derived / exploratory`。\n\n- `d_soybean_error_components_summary.csv`：固定 D 站、三模型、三来源、低中高组；跨站五次分别计算分量后取均值，四项分量差值之和恢复 ΔF1。\n- `../processed/sec33_round2/d_soybean_components_per_prediction.csv`：本站组汇总和跨站逐次底表，含支持量、Precision、Recall、按真实类分母的误分类率。\n- `overall_relation_plot_data.csv`、`composition_plot_data.csv`、`d_soybean_source_plot_data.csv`：图件对应数据。\n- `exploration-report.md`：本轮证据判断，不是论文正文。\n\nF1 分量的分母为 `Z=2TP+FP+FN`；它们与按真实类别像元数归一化的误分类率分开保存。误差线是五次预测的样本标准差，不是置信区间。\n""", encoding="utf-8")
    files = written + [report, readme] + plot_files
    manifest = {
        "data_status": "derived", "analysis_status": "exploratory", "pipeline_status": "Verified",
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "script": {"path": str(Path(__file__).resolve()), "sha256": sha(Path(__file__))},
        "inputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in source_paths],
        "outputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in files],
        "component_definition": "Each soybean error direction divided by Z=2TP+FP+FN; cross means are means of five per-fold components.",
        "difference_definition": "mean cross component minus within component; four component differences sum to raw-scale delta F1.",
        "spatial_metric_limit": "AREA_MN and composition reused from verified first-round tables; not recomputed from labels.",
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(files)} tables/reports/figures to the independent second-round directories.")


if __name__ == "__main__":
    main()

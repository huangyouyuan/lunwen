#!/usr/bin/env python3
"""Exploratory figures for the directional-confusion analysis.

The plotted values are read from the independent summary tables produced by
``explore_sec33_directional_confusion.py``.  Figures are exploratory assets;
no manuscript or historical result is modified.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SUM = ROOT / "results/summary/sec33_directional_confusion"
FIG = ROOT / "figures/exploratory/sec33_directional_confusion"
PROC = ROOT / "results/processed/sec33_directional_confusion"
FIG.mkdir(parents=True, exist_ok=True)

SITE = {"iw_2023": "A", "iw2_2023": "B", "ida_2023": "C", "il_2023": "D"}
MODEL = {"convgru": "ConvGRU", "unet3d": "3D U-Net", "utae": "U-TAE"}
CROP = {"corn": "玉米", "soybean": "大豆", "other": "其他"}
DIR = {"corn_to_soybean": "玉米→大豆", "corn_to_other": "玉米→其他",
       "soybean_to_corn": "大豆→玉米", "soybean_to_other": "大豆→其他",
       "other_to_corn": "其他→玉米", "other_to_soybean": "其他→大豆"}
BANDS = ["0<d<=1", "1<d<=2", "2<d<=3", "3<d<=4", "4<d<=5", "5<d<=6", "d>6"]


def setup() -> None:
    plt.rcParams.update({"font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
                         "axes.unicode_minus": False, "font.size": 8})


def overview() -> None:
    d = pd.read_csv(SUM / "directional_summary.csv")
    d["site"] = d.target.map(SITE)
    d["model_label"] = d.model.map(MODEL)
    d["direction_label"] = d.true_class + "_to_" + d.predicted_class
    d["combo"] = d.site + "←" + d.source.map(SITE) + "\n" + d.model_label
    order = [(t, s, m) for t in ["iw_2023", "iw2_2023", "ida_2023", "il_2023"]
             for s in [x for x in ["iw_2023", "iw2_2023", "ida_2023", "il_2023"] if x != t]
             for m in ["convgru", "unet3d", "utae"]]
    labels = [SITE[t] + "←" + SITE[s] + "\n" + MODEL[m] for t, s, m in order]
    d["key"] = list(zip(d.target, d.source, d.model))
    fig, axes = plt.subplots(3, 2, figsize=(13.2, 10.0), sharex=True, sharey=True)
    vals = []
    for ax, (direction, title) in zip(axes.flat, DIR.items()):
        x = []
        y = []
        for k, key in enumerate(order):
            t, s, m = key
            r = d[(d.target == t) & (d.source == s) & (d.model == m) &
                  (d.true_class + "_to_" + d.predicted_class == direction)].iloc[0]
            x.append(k); y.append(float(r.delta_rate_pp)); vals.append(float(r.delta_rate_pp))
        ax.axhline(0, color="#555555", lw=.7)
        colors = ["#c44e52" if v >= 0 else "#4c72b0" for v in y]
        ax.bar(x, y, color=colors, width=.86, edgecolor="none")
        ax.set_title(title, fontsize=9)
        ax.grid(axis="y", color="#dddddd", lw=.5)
        ax.set_axisbelow(True)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=90, fontsize=5.6)
    lo = min(vals); hi = max(vals); pad = max((hi - lo) * .1, 1)
    for ax in axes.flat:
        ax.set_ylim(lo - pad, hi + pad)
    fig.suptitle("六种定向错分的跨站错误率增量（跨站−本站，百分点）", fontsize=13, y=.995)
    fig.text(.5, .005, "横轴：目标站←源站；误差率分母为真实来源类别像元数。红色为正增量，蓝色为负增量。", ha="center", fontsize=8)
    fig.text(.006, .5, "定向错分率增量（百分点）", va="center", rotation="vertical", fontsize=9)
    fig.tight_layout(rect=[.02, .03, 1, .97])
    fig.savefig(FIG / "01_directional_increment_overview.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG / "01_directional_increment_overview.pdf", bbox_inches="tight")
    d[["site", "source", "target", "model", "true_class", "predicted_class", "direction_label",
       "within_rate", "cross_rate_mean", "delta_rate_pp", "delta_rate_direction"]].to_csv(
        FIG / "01_directional_increment_overview_data.csv", index=False, float_format="%.17g")


def case() -> None:
    dist = pd.read_csv(SUM / "distance_direction_summary.csv")
    typ = pd.read_csv(SUM / "boundary_type_direction_summary.csv")
    filt = (dist.source == "iw2_2023") & (dist.target == "il_2023") & (dist.true_class == "soybean") & (dist.predicted_class == "corn")
    dist = dist[filt].copy(); dist["model_label"] = dist.model.map(MODEL)
    dist["band_order"] = dist.band.map({b: i for i, b in enumerate(BANDS)})
    filt_t = (typ.source == "iw2_2023") & (typ.target == "il_2023") & (typ.true_class == "soybean") & (typ.predicted_class == "corn") & (typ.band == "0<d<=1")
    typ = typ[filt_t].copy(); typ["model_label"] = typ.model.map(MODEL)
    fig, axes = plt.subplots(2, 3, figsize=(15.0, 8.0), gridspec_kw={"height_ratios": [1.25, 1]})
    colors = {"iw_2023": "#4c72b0", "iw2_2023": "#dd8452", "ida_2023": "#55a868"}
    # The distance panel compares the three models for B->D.  The five-fold
    # standard deviation is shown only as a descriptive band, never a CI.
    for model, ax in zip(["convgru", "unet3d", "utae"], axes[0]):
        x = dist[dist.model == model].sort_values("band_order")
        ax.axhline(0, color="#555", lw=.7)
        ax.plot(range(len(x)), x.delta_rate_pp, marker="o", color="#c44e52", label="错误率增量")
        ax.fill_between(range(len(x)), x.delta_rate_pp - x.delta_rate_std * 100, x.delta_rate_pp + x.delta_rate_std * 100,
                        color="#c44e52", alpha=.15, label="五次±标准差")
        ax.set_title(MODEL[model]); ax.set_xticks(range(len(x))); ax.set_xticklabels(BANDS, rotation=35, fontsize=7)
        ax.grid(axis="y", color="#dddddd", lw=.5); ax.set_axisbelow(True)
    # Boundary types are descriptive overlapping views.  Keep them separate
    # from the mutually exclusive bitmask partition used for closure.
    for model, ax in zip(["convgru", "unet3d", "utae"], axes[1]):
        x = typ[typ.model == model]
        ax.axhline(0, color="#555", lw=.7)
        bt_label = {"corn_soybean": "玉米—大豆", "corn_other": "玉米—其他", "other_soybean": "其他—大豆"}
        bt_color = {"corn_soybean": "#4c72b0", "corn_other": "#dd8452", "other_soybean": "#55a868"}
        for bt, g in x.groupby("boundary_type"):
            r = g.iloc[0]; ax.bar(bt_label.get(bt, bt), r.delta_rate * 100, color=bt_color.get(bt, "#999"), width=.65, label=bt_label.get(bt, bt))
        ax.set_title(MODEL[model] + "（最近带三类边界）"); ax.tick_params(axis="x", rotation=25)
        ax.grid(axis="y", color="#dddddd", lw=.5); ax.set_axisbelow(True)
    for ax in axes.flat:
        ax.set_ylabel("错误率增量（百分点）")
    handles, labels = axes[1, 2].get_legend_handles_labels(); fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(.5, .018), fontsize=8)
    fig.suptitle("B→D 大豆→玉米：距离带与最近带边界类型", fontsize=13, y=.995)
    fig.text(.5, -.025, "距离带：>6 为开放远内部带；标准差描述五次预测波动。边界类型为重叠的描述性视图。", ha="center", fontsize=8)
    fig.tight_layout(rect=[.03, .085, 1, .97])
    fig.savefig(FIG / "02_case_B_to_D_soybean_to_corn_spatial.png", dpi=220, bbox_inches="tight")
    fig.savefig(FIG / "02_case_B_to_D_soybean_to_corn_spatial.pdf", bbox_inches="tight")
    dist.to_csv(FIG / "02_case_distance_data.csv", index=False, float_format="%.17g")
    typ.to_csv(FIG / "02_case_boundary_type_data.csv", index=False, float_format="%.17g")


def update_manifest() -> None:
    """Record the generated figures and the complete local artifact inventory."""
    manifest_path = SUM / "analysis_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}

    def digest(path: Path) -> dict[str, object]:
        h = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(block)
        return {"path": path.resolve().as_posix(), "sha256": h.hexdigest(),
                "bytes": path.stat().st_size, "role": "artifact"}

    artifact_dirs = (PROC, SUM, FIG)
    artifacts = []
    for directory in artifact_dirs:
        for path in sorted(directory.iterdir()):
            if path.is_file() and path.name != "analysis_manifest.json":
                artifacts.append(digest(path))
    scripts = [ROOT / "scripts/explore_sec33_directional_confusion.py",
               ROOT / "scripts/plot_sec33_directional_confusion.py",
               ROOT / "scripts/test/test_sec33_directional_confusion.py"]
    manifest["scripts"] = [digest(path) | {"role": "script"} for path in scripts]
    manifest["artifacts"] = artifacts
    manifest["figures_generated_at_utc"] = datetime.now(timezone.utc).isoformat()
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    setup(); overview(); case(); update_manifest(); print("directional figures complete")


if __name__ == "__main__":
    main()

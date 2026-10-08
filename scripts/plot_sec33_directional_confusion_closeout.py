#!/usr/bin/env python3
"""Exploratory closeout figures for the directional-confusion correction."""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SUM = ROOT / "results/summary/sec33_directional_confusion_closeout"
FIG = ROOT / "figures/exploratory/sec33_directional_confusion_closeout"
FIG.mkdir(parents=True, exist_ok=True)

MODEL_LABEL = {"convgru": "ConvGRU", "unet3d": "3D U-Net", "utae": "U-TAE"}
CROP_LABEL = {"corn": "玉米", "soybean": "大豆"}
GROUP_LABEL = {
    "contact_1_only": "仅直接接触玉米",
    "contact_2_only": "仅直接接触其他类",
    "mixed": "同时接触玉米和其他类",
    "nearest_no_direct": "最近带无四邻域\n异类直接接触",
}
GROUP_ORDER = list(GROUP_LABEL)
CHECKS = []


def figure_data(frame: pd.DataFrame, name: str) -> None:
    path = FIG / (name + ".csv")
    frame.to_csv(path, index=False, float_format="%.17g", lineterminator="\n")
    recovered = pd.read_csv(path, float_precision="round_trip")
    pd.testing.assert_frame_equal(frame.reset_index(drop=True), recovered, check_dtype=False,
                                  check_exact=False, atol=1e-12, rtol=0)
    CHECKS.append(dict(check=name + " exported values match plotted input", status="Verified", rows=len(frame)))


def setup() -> None:
    plt.rcParams.update({"font.sans-serif": ["Microsoft YaHei", "SimHei", "DejaVu Sans"],
                         "axes.unicode_minus": False, "font.size": 8})


def boundary_case() -> None:
    d = pd.read_csv(SUM / "exclusive_boundary_summary.csv", float_precision="round_trip")
    d = d[(d.model.isin(MODEL_LABEL)) & (d.source == "iw2_2023") & (d.target == "il_2023") &
          (d.band == "0<d<=1") & (d.true_class == "soybean") & (d.predicted_class == "corn")].copy()
    d["group_order"] = d.exclusive_boundary_group.map({g: i for i, g in enumerate(GROUP_ORDER)})
    d = d.sort_values(["model", "group_order"])
    if len(d) != 12 or d.group_order.isna().any() or d.duplicated(["model", "exclusive_boundary_group"]).any():
        raise ValueError("case must cover three models and four exclusive groups")
    figure_data(d, "01_B_to_D_soybean_to_corn_exclusive_boundary_data")

    fig, axes = plt.subplots(2, 3, figsize=(13.2, 6.9), sharex="col", sharey="row")
    for col, model in enumerate(["convgru", "unet3d", "utae"]):
        x = d[d.model == model].sort_values("group_order")
        pos = np.arange(len(x))
        ax = axes[0, col]
        ax.axhline(0, color="#444", lw=.8)
        ax.bar(pos, x.delta_rate_mean * 100, yerr=x.delta_rate_std * 100,
               color=["#c44e52" if v >= 0 else "#4c72b0" for v in x.delta_rate_mean],
               capsize=3, width=.72, edgecolor="none")
        ax.set_title(MODEL_LABEL[model])
        ax.set_ylabel("定向错分率增量（百分点）")
        ax.grid(axis="y", color="#dddddd", lw=.5); ax.set_axisbelow(True)
        for p, (_, r) in zip(pos, x.iterrows()):
            if not np.isfinite(r.delta_rate_mean):
                ax.text(p, 0, "NA", ha="center", va="bottom", fontsize=8)
        ax = axes[1, col]
        ax.plot(pos, x.within_rate * 100, marker="o", color="#4c72b0", label="本站")
        ax.plot(pos, x.cross_rate_mean * 100, marker="s", color="#c44e52", label="跨站五次均值")
        ax.set_ylabel("大豆→玉米错分率（%）")
        ax.grid(axis="y", color="#dddddd", lw=.5); ax.set_axisbelow(True)
        ax.set_xticks(pos)
        ax.set_xticklabels([GROUP_LABEL[r.exclusive_boundary_group] + f"\nn={int(r.within_reference_pixels):,}"
                            for r in x.itertuples()], rotation=25, ha="right", fontsize=7)
    axes[1, 2].legend(loc="best", fontsize=7, frameon=False)
    fig.suptitle("B→D 大豆→玉米：互斥最近带边界组", fontsize=13, y=.995)
    axes[1, 0].set_ylim(bottom=0)
    axes[0, 0].margins(y=.18)
    if not all(axes[row, 0].get_ylim() == axes[row, col].get_ylim() for row in range(2) for col in range(3)):
        raise ValueError("same-metric model panels must share y limits")
    CHECKS.append(dict(check="exclusive case same-metric model panels share y limits", status="Verified", rows=12))
    fig.text(.5, .024, "增量=跨站−本站；误差线为五次预测样本标准差。n 为同组真实大豆像元数；无支持时显示 NA。", ha="center", fontsize=8)
    fig.text(.5, .004, "仅展示大豆→玉米方向；负增量不代表总漏分率或 F1 改善。", ha="center", fontsize=8)
    fig.tight_layout(rect=[.02, .06, 1, .95])
    fig.savefig(FIG / "01_B_to_D_soybean_to_corn_exclusive_boundary.png", dpi=240, bbox_inches="tight")
    fig.savefig(FIG / "01_B_to_D_soybean_to_corn_exclusive_boundary.pdf", bbox_inches="tight")
    plt.close(fig)


def model_crop() -> None:
    d = pd.read_csv(SUM / "model_crop_metrics_summary.csv", float_precision="round_trip")
    d = d[d.crop.isin(["corn", "soybean"])].copy()
    figure_data(d, "02_model_crop_metrics_data")
    fig, axes = plt.subplots(1, 2, figsize=(10.8, 4.5), sharey=True)
    colors = {"delta_precision_pp": "#4c72b0", "delta_recall_pp": "#dd8452", "delta_f1_pp": "#55a868"}
    labels = {"delta_precision_pp": "Precision（跨站−本站）", "delta_recall_pp": "Recall（跨站−本站）", "delta_f1_pp": "ΔF1（本站−跨站）"}
    for ax, crop in zip(axes, ["corn", "soybean"]):
        x = d[d.crop == crop].set_index("model").loc[["convgru", "unet3d", "utae"]]
        pos = np.arange(3); width = .23
        for i, field in enumerate(colors):
            ax.bar(pos + (i - 1) * width, x[field], width=width, color=colors[field], label=labels[field])
        ax.axhline(0, color="#444", lw=.8)
        ax.set_title(CROP_LABEL[crop])
        ax.set_xticks(pos); ax.set_xticklabels([MODEL_LABEL[m] for m in x.index])
        ax.grid(axis="y", color="#dddddd", lw=.5); ax.set_axisbelow(True)
        ax.set_ylabel("指标差（百分点；符号见图例）")
    handles, legend_labels = axes[1].get_legend_handles_labels()
    fig.legend(handles, legend_labels, fontsize=8, frameon=False, loc="upper center", bbox_to_anchor=(.5, .94), ncol=3)
    fig.suptitle("按模型分层的作物指标变化（12条迁移路径等权）", fontsize=12, y=.995)
    fig.text(.5, .01, "F1变化定义为本站F1−跨站五次均值；Precision和Recall为跨站−本站。", ha="center", fontsize=8)
    fig.tight_layout(rect=[.02, .04, 1, .86])
    fig.savefig(FIG / "02_model_crop_metrics_change.png", dpi=240, bbox_inches="tight")
    fig.savefig(FIG / "02_model_crop_metrics_change.pdf", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    setup(); boundary_case(); model_crop()
    pd.DataFrame(CHECKS).to_csv(FIG / "figure_data_checks.csv", index=False, lineterminator="\n")
    print("directional closeout figures complete")


if __name__ == "__main__":
    main()

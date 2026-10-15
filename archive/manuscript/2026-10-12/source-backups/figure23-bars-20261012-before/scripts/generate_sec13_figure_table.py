#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从已核验的 2023 年整站底表生成 1.3 组成图与斑块分布表，不重新计算指标。

运行：python scripts/generate_sec13_figure_table.py
已有输出时停止；修订需指定新的输出路径，保留历史产物。
"""

import hashlib
import json
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

import figstyle as fs


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/summary/sec13_sec31_foundations"
FIGURE = ROOT / "figures/study_area/fig_sec13_composition"
TABLE = ROOT / "tables/sec13_patch_distribution_rows.tex"
RECORD = ROOT / "verification/sec13-figure-table-v2-2026-10-11.json"
CROPS = (("corn", 1), ("soybean", 3), ("other", 2))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--table-only", action="store_true",
                        help="仅生成斑块分布表；用于复用已存在且已核对的组成图")
    args = parser.parse_args()
    inputs = [SOURCE / name for name in (
        "reference_composition.csv", "crop_patch_distribution_reading.csv")]
    figure_outputs = [FIGURE.with_suffix(".pdf"), FIGURE.with_suffix(".png")]
    outputs = ([TABLE, RECORD] if args.table_only else figure_outputs + [TABLE, RECORD])
    for path in outputs:
        if path.exists():
            raise FileExistsError(f"保留已有产物，停止写入：{path}")

    # 核对输入与基础证据清单中的字节哈希。
    manifest = json.loads((SOURCE / "manifest.json").read_text(encoding="utf-8"))
    expected = {row["path"]: row["sha256"] for row in manifest["outputs"]}
    for path in inputs:
        assert digest(path) == expected[path.relative_to(ROOT).as_posix()]
    composition, distributions = [pd.read_csv(path, float_precision="round_trip") for path in inputs]
    keys = {(site, crop) for site in fs.SITES for crop, _ in CROPS}
    assert len(composition) == 12 and not composition.duplicated(["site", "crop"]).any()
    assert set(zip(composition.site, composition.crop)) == keys
    assert composition.target.map(fs.SITE_MAP).equals(composition.site)
    distribution_keys = {(site, crop, metric, weighting)
                         for site in fs.SITES for crop, _ in CROPS[:2]
                         for metric in ("AREA", "SHAPE")
                         for weighting in ("patch_equal", "reference_pixel_area")}
    distributions = distributions[
        distributions.metric.isin(["AREA", "SHAPE"])
        & distributions.weighting.isin(["patch_equal", "reference_pixel_area"])
        & distributions.distribution_level.isin(["patch_count", "reference_pixel_area"])
    ].copy()
    assert len(distributions) == 32 and not distributions.duplicated(
        ["site", "crop", "metric", "weighting"]).any()
    assert set(zip(distributions.site, distributions.crop, distributions.metric,
                   distributions.weighting)) == distribution_keys
    assert distributions.current_status.eq("Verified").all()
    assert distributions.target.map(fs.SITE_MAP).equals(distributions.site)
    assert (distributions.q25 <= distributions["median"]).all()
    assert (distributions["median"] <= distributions.q75).all()
    comp = composition.set_index(["site", "crop"])
    dist = distributions.set_index(["site", "crop", "metric", "weighting"])
    for site in fs.SITES:
        group = comp.loc[site]
        assert group.pixels.sum() == 6553600
        assert np.allclose(group.area_ha, group.pixels * 0.09)
        assert np.isclose(group.area_ha.sum(), 589824)
        assert np.allclose(group.area_share, group.pixels / group.pixels.sum())
        assert np.isclose(group.area_share.sum(), 1)
        for crop, _ in CROPS[:2]:
            c = comp.loc[(site, crop)]
            counts = distributions[(distributions.site == site) & (distributions.crop == crop)]
            assert counts.n_total.nunique() == 1 and counts.n_total.iloc[0] > 0
            assert counts.pixels_total.eq(c.pixels).all()

    if not args.table_only:
        fs.setup()
        fig, axes = fs.grid(w=2, h=1.5)
        ax = axes[0, 0]
        y = np.arange(4)
        step = 0.25
        for index, (crop, code) in enumerate(CROPS):
            values = [100 * comp.loc[(site, crop), "area_share"] for site in fs.SITES]
            bars = ax.barh(y + (index - 1) * step, values, height=0.22,
                           color=fs.CLASS_COLORS[code], edgecolor="black", linewidth=0.4)
            for bar, value in zip(bars, values):
                ax.text(value + 0.65, bar.get_y() + bar.get_height() / 2,
                        f"{value:.2f}", ha="left", va="center")
        ax.set_yticks(y, fs.SITES)
        ax.set_ylim(3.5, -0.5)
        ax.set_xlim(0, 52)
        ax.set_xticks(np.arange(0, 51, 10))
        ax.set_xlabel("面积占比/%")
        ax.set_ylabel("站点", labelpad=2)
        ax.tick_params(axis="y", length=0, pad=1.5)
        ax.grid(axis="x", color="#D8D8D8", linewidth=0.4)
        ax.set_axisbelow(True)
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        labels = [text.get_window_extent(renderer) for text in ax.texts]
        assert not any(a.overlaps(b) for i, a in enumerate(labels) for b in labels[i + 1:])
        assert all(box.x1 <= ax.get_window_extent(renderer).x1 for box in labels)
        width_cm = (fig.get_tightbbox(renderer).width + 0.02) * 2.54
        assert width_cm <= 8.325, f"图宽超出单栏：{width_cm:.3f} cm"
        for path in figure_outputs:
            path.parent.mkdir(parents=True, exist_ok=True)
        for suffix in (".pdf", ".png"):
            fig.savefig(FIGURE.with_suffix(suffix))
        fs.plt.close(fig)
    else:
        assert all(path.exists() for path in figure_outputs)
        previous_record = ROOT / "verification/sec13-figure-table-2026-10-11.json"
        previous = json.loads(previous_record.read_text(encoding="utf-8"))
        recorded = {row["path"]: row["sha256"] for row in previous["inputs"] + previous["outputs"]}
        for path in figure_outputs + [inputs[0]]:
            assert digest(path) == recorded[path.relative_to(ROOT).as_posix()]
        width_cm = previous["figure_width_cm"]

    rows = ["% 由 scripts/generate_sec13_figure_table.py 从 2023 年完整参考斑块分布生成。"]
    for site in fs.SITES:
        for index, (crop, code) in enumerate(CROPS[:2]):
            area_equal = dist.loc[(site, crop, "AREA", "patch_equal")]
            area_weighted = dist.loc[(site, crop, "AREA", "reference_pixel_area")]
            shape_equal = dist.loc[(site, crop, "SHAPE", "patch_equal")]
            shape_weighted = dist.loc[(site, crop, "SHAPE", "reference_pixel_area")]
            site_cell = rf"\multirow{{2}}{{*}}{{{site}}}" if index == 0 else ""
            fmt = lambda row: f"{row['median']:.2f} ({row.q25:.2f}～{row.q75:.2f})"
            rows.append(f"{site_cell} & {fs.CLASS_NAMES[code]} & {int(area_equal.n_total)} & "
                        f"{fmt(area_equal)} & {fmt(area_weighted)} & "
                        f"{fmt(shape_equal)} & {fmt(shape_weighted)} " + r"\\")
        if site != fs.SITES[-1]:
            rows.append(r"\addlinespace[2pt]")
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    TABLE.write_text("\n".join(rows) + "\n", encoding="utf-8")

    sources = inputs + [SOURCE / "manifest.json", Path(__file__), ROOT / "scripts/figstyle.py"]
    if args.table_only:
        sources.append(previous_record)
    record = {
        "status": "Verified", "data_status": "derived_from_verified_summary",
        "scope": "2023 whole-site composition and crop AREA/SHAPE distributions for Section 1.3",
        "checks": ["input hashes", "site/class identities", "area and pixel closure",
                   "two-weight distribution identity and support", "quantile ordering"],
        "figure_checks": "reused prior figure/input hashes and visual check" if args.table_only
                         else "label overlap and single-column width checked in this run",
        "figure_axes_cm": [7.6, 5.7], "figure_width_cm": width_cm,
        "font_size_pt": fs.FS, "manuscript_compiled": False,
        "combined_crop_percent": {
            site: float(100 * (comp.loc[(site, "corn"), "area_share"] +
                               comp.loc[(site, "soybean"), "area_share"])) for site in fs.SITES},
        "inputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)} for p in sources],
        "outputs": [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p)}
                    for p in figure_outputs + [TABLE]],
    }
    RECORD.parent.mkdir(parents=True, exist_ok=True)
    RECORD.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Verified: 12 composition rows, 32 distribution rows, 8 site/crop groups; figure {width_cm:.2f} cm wide.")
    print(json.dumps(record["combined_crop_percent"], ensure_ascii=False))


if __name__ == "__main__":
    main()

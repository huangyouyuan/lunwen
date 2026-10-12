#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从现有2023年整站组成底表绘制图2，不生成或改写历史斑块分布表。

运行：python scripts/plot_sec13_composition.py
修订前需保留已有图件；图框、字体和三条一组的样式与图3共用figstyle。
"""

from pathlib import Path

import numpy as np
import pandas as pd

import figstyle as fs


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results/summary/sec13_sec31_foundations/reference_composition.csv"
FIGURE = ROOT / "figures/study_area/fig_sec13_composition"
CROPS = (("corn", 1), ("soybean", 3), ("other", 2))


def main():
    composition = pd.read_csv(SOURCE, float_precision="round_trip")
    expected = {(site, crop) for site in fs.SITES for crop, _ in CROPS}
    assert len(composition) == 12
    assert not composition.duplicated(["site", "crop"]).any()
    assert set(zip(composition.site, composition.crop)) == expected
    assert composition.target.map(fs.SITE_MAP).equals(composition.site)
    comp = composition.set_index(["site", "crop"])
    for site in fs.SITES:
        group = comp.loc[site]
        assert group.pixels.sum() == 6553600
        assert group.total_pixels.eq(6553600).all()
        assert np.allclose(group.area_ha, group.pixels * 0.09)
        assert np.allclose(group.area_share, group.pixels / group.total_pixels)
        assert np.isclose(group.area_share.sum(), 1)

    fs.setup()
    fig, axes = fs.grid(w=2, h=1.5)
    ax = axes[0, 0]
    y = np.arange(len(fs.SITES))
    for index, (crop, code) in enumerate(CROPS):
        values = [100 * comp.loc[(site, crop), "area_share"] for site in fs.SITES]
        bars = ax.barh(y + (index - 1) * fs.GROUPED_BAR_STEP, values,
                       height=fs.GROUPED_BAR_HEIGHT, color=fs.CLASS_COLORS[code],
                       edgecolor="black", linewidth=0.4)
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
    ax.grid(axis="x", **fs.GROUPED_BAR_GRID)
    ax.set_axisbelow(True)

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    labels = [text.get_window_extent(renderer) for text in ax.texts]
    assert not any(a.overlaps(b) for i, a in enumerate(labels) for b in labels[i + 1:])
    assert all(box.x1 <= ax.get_window_extent(renderer).x1 for box in labels)
    width_cm = (fig.get_tightbbox(renderer).width + 0.02) * 2.54
    assert width_cm <= 8.325, f"图宽超出单栏：{width_cm:.3f} cm"
    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    for suffix in (".pdf", ".png"):
        fig.savefig(FIGURE.with_suffix(suffix))
    fs.plt.close(fig)
    print(f"Verified: 12 composition rows; figure width {width_cm:.3f} cm.")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.2 用图：不同源—目标区域组合下三种模型的玉米和大豆 F1 差值

六个子图各出一个 PDF + 一个色标 PDF，LaTeX 用 subcaption 拼；子图题、图名是文本：
  a ConvGRU玉米  b 3D U-Net玉米  c U-TAE玉米
  d ConvGRU大豆  e 3D U-Net大豆  f U-TAE大豆
每个子图 4×4 热力图：行=源站，列=目标站（A–D），对角线留空，单元格标两位小数，共用色标。
子图图框边长由命令行参数给（UNIT 的倍数，默认 1 → 3.8 cm）：
  python scripts/plot_degradation_heatmap.py 1      # 3.8 cm，适合 2 行 3 列
  python scripts/plot_degradation_heatmap.py 1.5    # 5.7 cm，适合 3 行 2 列

输入：results/summary/f1_raw_scale/crop_f1_difference_36paths.csv
输出：figures/results/fig_degradation_heatmap_{a..f}.pdf / .png，fig_degradation_heatmap_cbar.pdf / .png
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import figstyle as fs
from f1_display import display_number

fs.setup()

SITE_MAP = fs.SITE_MAP
MODEL_MAP = fs.MODEL_LABELS
CROP_NAMES = {'corn': '玉米', 'soybean': '大豆'}
PANELS = [('corn', 'convgru', 'a'), ('corn', 'unet3d', 'b'), ('corn', 'utae', 'c'),
          ('soybean', 'convgru', 'd'), ('soybean', 'unet3d', 'e'), ('soybean', 'utae', 'f')]


def prepare_heatmap_data(df, model, crop):
    """4×4 展示表（百分点）：行=源站，列=目标站，对角线 NaN。"""
    model_df = df[df['model'] == model].copy()
    model_df['source_abbr'] = model_df['source'].map(SITE_MAP)
    model_df['target_abbr'] = model_df['target'].map(SITE_MAP)
    pivot = model_df.pivot(index='source_abbr', columns='target_abbr', values=f'{crop}_f1_difference')
    pivot = pivot.reindex(index=fs.SITES, columns=fs.SITES)
    for site in fs.SITES:
        pivot.loc[site, site] = np.nan
    return pivot * 100


def shared_color_scale(all_values):
    """One common scale for all six panels, including any negative differences."""
    values = np.asarray(all_values)
    low, high = float(np.nanmin(values)), float(np.nanmax(values))
    if low < 0:
        # A single zero-centred diverging scale; never clip or take abs of data.
        limit = max(1.0, float(np.ceil(max(-low, high))))
        return -limit, limit, 'RdBu_r'
    return 0.0, max(1.0, float(np.ceil(high))), 'YlOrRd'


def main(size):
    df = pd.read_csv('results/summary/f1_raw_scale/crop_f1_difference_36paths.csv',
                     float_precision='round_trip')

    all_values = np.concatenate([prepare_heatmap_data(df, m, c).values.ravel() for c, m, _ in PANELS])
    vmin, vmax, cmap = shared_color_scale(all_values)

    for crop, model, tag in PANELS:
        fig, axes = fs.grid(1, 1, w=size, h=size)
        ax = axes[0, 0]
        values = prepare_heatmap_data(df, model, crop)
        labels = values.map(display_number)
        sns.heatmap(values, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax,
                    annot=labels, fmt='', annot_kws={'size': fs.FS}, cbar=False,
                    linewidths=0, square=True)
        # 网格只画一次，外框不裁切，避免内外线宽不同或重复描边。
        edges = np.arange(len(fs.SITES) + 1)
        ax.hlines(edges, 0, len(fs.SITES), colors='black', linewidths=0.6, clip_on=False)
        ax.vlines(edges, 0, len(fs.SITES), colors='black', linewidths=0.6, clip_on=False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xlabel('目标站')
        ax.set_ylabel('源站')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        ax.tick_params(length=0)
        fs.save(fig, f'fig_degradation_heatmap_{tag}')

    # 横向共用色标宽 2 UNIT；色标名称和单位由 LaTeX 排版。
    bar_width, bar_height = 2 * fs.UNIT, 0.35
    fig_width, fig_height = bar_width + 0.6, 1.2
    fig = plt.figure(figsize=(fig_width * fs.CM, fig_height * fs.CM))
    cax = fig.add_axes([0.3 / fig_width, 0.7 / fig_height,
                       bar_width / fig_width, bar_height / fig_height])
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin, vmax))
    cb = fig.colorbar(sm, cax=cax, orientation='horizontal',
                      ticks=np.linspace(vmin, vmax, 5), format='%.2f')
    cb.outline.set_linewidth(0.6)
    fs.save(fig, 'fig_degradation_heatmap_cbar')

    print(f'Generated: figures/results/fig_degradation_heatmap_{{a..f,cbar}}.pdf / .png  (panel {size * fs.UNIT:.1f} cm)')
    print(f'色标范围：{vmin:.2f} ~ {vmax:.2f}，F1下降（百分点）')
    for crop, model, tag in PANELS:
        v = prepare_heatmap_data(df, model, crop).values
        v = v[~np.isnan(v)]
        print(f'({tag}) {MODEL_MAP[model]}-{CROP_NAMES[crop]}: mean={v.mean():.2f} std={v.std():.2f} '
              f'min={v.min():.2f} max={v.max():.2f}')


if __name__ == '__main__':
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 1.0)

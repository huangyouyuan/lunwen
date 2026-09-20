#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.3.1 用图：不同源—目标区域组合下三种模型的玉米和大豆 F1 泛化退化

六个子图各出一个 PDF + 一个色标 PDF，LaTeX 用 subcaption 拼；子图题、图名是文本：
  a ConvGRU玉米  b 3D U-Net玉米  c U-TAE玉米
  d ConvGRU大豆  e 3D U-Net大豆  f U-TAE大豆
每个子图 4×4 热力图：行=源站，列=目标站（A–D），对角线留空，单元格标两位小数，共用色标。
子图图框边长由命令行参数给（UNIT 的倍数，默认 1.5 → 5.7 cm）：
  python scripts/plot_degradation_heatmap.py 1      # 3.8 cm，适合 2 行 3 列
  python scripts/plot_degradation_heatmap.py 1.5    # 5.7 cm，适合 3 行 2 列

输入：results/summary/crop_f1_degradation_36paths.csv
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

fs.setup()

SITE_MAP = fs.SITE_MAP
MODEL_MAP = fs.MODEL_LABELS
CROP_NAMES = {'corn': '玉米', 'soybean': '大豆'}
PANELS = [('corn', 'convgru', 'a'), ('corn', 'unet3d', 'b'), ('corn', 'utae', 'c'),
          ('soybean', 'convgru', 'd'), ('soybean', 'unet3d', 'e'), ('soybean', 'utae', 'f')]


def prepare_heatmap_data(df, model, crop):
    """4×4 透视表：行=源站，列=目标站，对角线 NaN"""
    model_df = df[df['model'] == model].copy()
    model_df['source_abbr'] = model_df['source'].map(SITE_MAP)
    model_df['target_abbr'] = model_df['target'].map(SITE_MAP)
    pivot = model_df.pivot(index='source_abbr', columns='target_abbr', values=f'{crop}_loss_pp')
    pivot = pivot.reindex(index=fs.SITES, columns=fs.SITES)
    for site in fs.SITES:
        pivot.loc[site, site] = np.nan
    return pivot


def main(size):
    df = pd.read_csv('results/summary/crop_f1_degradation_36paths.csv')

    all_values = np.concatenate([prepare_heatmap_data(df, m, c).values.ravel() for c, m, _ in PANELS])
    vmin = float(np.floor(np.nanmin(all_values)))
    vmax = float(np.ceil(np.nanmax(all_values)))

    for crop, model, tag in PANELS:
        fig, axes = fs.grid(1, 1, w=size, h=size)
        ax = axes[0, 0]
        sns.heatmap(prepare_heatmap_data(df, model, crop), ax=ax, cmap='YlOrRd', vmin=vmin, vmax=vmax,
                    annot=True, fmt='.2f', annot_kws={'size': fs.FS}, cbar=False,
                    linewidths=0.5, linecolor='gray', square=True)
        ax.set_xlabel('目标站')
        ax.set_ylabel('源站')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
        ax.set_yticklabels(ax.get_yticklabels(), rotation=0)
        ax.tick_params(length=0)
        fs.save(fig, f'fig_degradation_heatmap_{tag}')

    # 色标：高 = 一个子图框，宽 0.35 cm
    fig = plt.figure(figsize=((0.35 + 1.6) * fs.CM, (size * fs.UNIT + 0.6) * fs.CM))
    cax = fig.add_axes([0.05, 0.3 / (size * fs.UNIT + 0.6), 0.35 / (0.35 + 1.6), (size * fs.UNIT) / (size * fs.UNIT + 0.6)])
    sm = plt.cm.ScalarMappable(cmap='YlOrRd', norm=plt.Normalize(vmin, vmax))
    cb = fig.colorbar(sm, cax=cax)
    cb.set_label('泛化退化/个百分点')
    cb.outline.set_linewidth(0.6)
    fs.save(fig, 'fig_degradation_heatmap_cbar')

    print(f'Generated: figures/results/fig_degradation_heatmap_{{a..f,cbar}}.pdf / .png  (panel {size * fs.UNIT:.1f} cm)')
    print(f'色标范围：{vmin:.0f} ~ {vmax:.0f} pp')
    for crop, model, tag in PANELS:
        v = prepare_heatmap_data(df, model, crop).values
        v = v[~np.isnan(v)]
        print(f'({tag}) {MODEL_MAP[model]}-{CROP_NAMES[crop]}: mean={v.mean():.2f} std={v.std():.2f} '
              f'min={v.min():.2f} max={v.max():.2f}')


if __name__ == '__main__':
    main(float(sys.argv[1]) if len(sys.argv) > 1 else 1.5)

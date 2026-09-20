#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：三种模型在四个站点的站内玉米、大豆 F1

两个子图各出一个 PDF，由 LaTeX 用 subcaption 上下拼（子图题、图例、图名都是 LaTeX 文本）：
  fig_within_site_f1_a  四站点玉米分类精度
  fig_within_site_f1_b  四站点大豆分类精度
每个子图图框 7.6 × 5.7 cm（2 × 1.5 UNIT），横向条形：纵轴站点 A–D（自上而下），
每站 ConvGRU / 3D U-Net / U-TAE 三条（自上而下）；横轴 F1/%；数值标在条末端，每条一行。

输入：results/summary/within_site_crop_f1.csv（站内汇总 F1）
输出：figures/results/fig_within_site_f1_{a,b}.pdf / .png
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import figstyle as fs

fs.setup()

CROPS = [('corn_f1', 'a', '四站点玉米分类精度'), ('soybean_f1', 'b', '四站点大豆分类精度')]


def main():
    df = pd.read_csv('results/summary/within_site_crop_f1.csv')
    df['site'] = df['target'].map(fs.SITE_MAP)

    y = np.arange(len(fs.SITES))
    h = 0.30                          # 三条占 0.90，组间留 0.10
    xmin, xmax = 88, 98.5             # 上限 98.5：刻度到 98 且 98 的数字不探出图框，整幅才不超栏宽

    for col, tag, title in CROPS:
        fig, axes = fs.grid(1, 1, w=2, h=1.5)
        ax = axes[0, 0]
        for k, key in enumerate(fs.MODEL_ORDER):
            vals = [df[(df['model'] == key) & (df['site'] == s)][col].iloc[0] * 100 for s in fs.SITES]
            bars = ax.barh(y + (k - 1) * h, vals, h, color=fs.MODEL_COLORS[key],
                           edgecolor='black', linewidth=0.4)
            for b, v in zip(bars, vals):
                ax.text(v + 0.1, b.get_y() + b.get_height() / 2, f'{v:.2f}',
                        ha='left', va='center')
        ax.set_yticks(y)
        ax.set_yticklabels(fs.SITES)
        ax.set_ylim(len(fs.SITES) - 0.5, -0.5)          # A 在最上
        ax.set_xlim(xmin, xmax)
        ax.set_xticks(np.arange(xmin, 98 + 1, 2))
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.4)
        ax.set_axisbelow(True)
        ax.tick_params(axis='y', length=0, pad=1.5)
        ax.set_xlabel('F1/%')
        ax.set_ylabel('站点', labelpad=2)
        # 图例由 LaTeX 文本排在两子图之后、图名之前（\modellegend），图里不画
        out = fs.save(fig, f'fig_within_site_f1_{tag}')
        print(f'({tag}) {title}: {out}')
        for key in fs.MODEL_ORDER:
            row = [f"{df[(df['model']==key)&(df['site']==s)][col].iloc[0]*100:.2f}" for s in fs.SITES]
            print(f'  {fs.MODEL_LABELS[key]:9s}', ' '.join(row))


if __name__ == '__main__':
    main()

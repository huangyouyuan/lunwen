#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：三种模型在四个站点的站内玉米、大豆 F1

单栏 8 cm × 12 cm，上下两子图，横向条形图：
  (a) 四站点玉米分类精度   (b) 四站点大豆分类精度
  纵轴站点 A–D（自上而下），每站 ConvGRU / 3D U-Net / U-TAE 三条（自上而下）；横轴 F1/%
  数值标在条末端，每条一行，数字之间不会横向相挨（竖柱时 12 根柱在 8 cm 内放不下 12 个两位小数）
  子图题在各子图下；图例在整幅图底部。图名在正文 caption。

输入：results/summary/within_site_crop_f1.csv（站内汇总 F1）
输出：figures/results/fig_within_site_f1.png / .pdf
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import figstyle as fs

fs.setup()

CROPS = [('corn_f1', '（a）四站点玉米分类精度'), ('soybean_f1', '（b）四站点大豆分类精度')]


def main():
    df = pd.read_csv('results/summary/within_site_crop_f1.csv')
    df['site'] = df['target'].map(fs.SITE_MAP)

    fig, axes = plt.subplots(2, 1, figsize=(fs.COL_W, 3 * fs.MODULE))
    y = np.arange(len(fs.SITES))
    h = 0.30                          # 三条占 0.90，组间留 0.10
    xmin, xmax = 88, 98

    for ax, (col, subtitle) in zip(axes, CROPS):
        for k, key in enumerate(fs.MODEL_ORDER):
            vals = [df[(df['model'] == key) & (df['site'] == s)][col].iloc[0] * 100 for s in fs.SITES]
            bars = ax.barh(y + (k - 1) * h, vals, h, label=fs.MODEL_LABELS[key],
                           color=fs.MODEL_COLORS[key], edgecolor='black', linewidth=0.4)
            for b, v in zip(bars, vals):
                ax.text(v + 0.08, b.get_y() + b.get_height() / 2, f'{v:.2f}',
                        ha='left', va='center', fontsize=fs.FS_ANNOT)
        ax.set_yticks(y)
        ax.set_yticklabels(fs.SITES)
        ax.set_ylim(len(fs.SITES) - 0.5, -0.5)          # A 在最上
        ax.set_xlim(xmin, xmax)
        ax.set_xticks(np.arange(xmin, xmax + 1, 2))
        ax.grid(axis='x', alpha=0.3, linestyle='--', linewidth=0.4)
        ax.set_axisbelow(True)
        ax.tick_params(axis='y', length=0)
        ax.set_xlabel('F1/%\n' + subtitle, fontsize=fs.FS_SUBTITLE, labelpad=2, linespacing=1.4)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.0), handlelength=1.4, columnspacing=1.2)

    plt.tight_layout(rect=[0, 0.045, 1, 1], h_pad=0.6, pad=0.3)
    plt.savefig('figures/results/fig_within_site_f1.png')
    plt.savefig('figures/results/fig_within_site_f1.pdf')
    plt.close()

    print('Generated: figures/results/fig_within_site_f1.png / .pdf')
    for col, subtitle in CROPS:
        print(subtitle)
        for key in fs.MODEL_ORDER:
            row = [f"{df[(df['model']==key)&(df['site']==s)][col].iloc[0]*100:.2f}" for s in fs.SITES]
            print(f'  {fs.MODEL_LABELS[key]:9s}', ' '.join(row))


if __name__ == '__main__':
    main()

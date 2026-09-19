#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：三种模型在四个站点的站内玉米、大豆 F1

双子图分组柱状图：
  (a) 玉米 F1   (b) 大豆 F1
  横轴：站点 A–D；每站并列 ConvGRU、3D U-Net、U-TAE 三根柱
  纵轴：F1（%），两子图同刻度；柱顶标数值；共用图例
图名、图注写在正文 caption，图内不含。

输入：results/summary/within_site_crop_f1.csv（站内汇总 F1）
输出：figures/results/fig_within_site_f1.png / .pdf
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

SITE_MAP = {'iw_2023': 'A', 'iw2_2023': 'B', 'ida_2023': 'C', 'il_2023': 'D'}
SITES = ['A', 'B', 'C', 'D']
MODELS = [('convgru', 'ConvGRU', '#8DA0CB'),
          ('unet3d', '3D U-Net', '#66C2A5'),
          ('utae', 'U-TAE', '#FC8D62')]
CROPS = [('corn_f1', '（a）玉米'), ('soybean_f1', '（b）大豆')]


def main():
    df = pd.read_csv('results/summary/within_site_crop_f1.csv')
    df['site'] = df['target'].map(SITE_MAP)

    # 统一纵轴：取两作物全局最小值向下留 5 个百分点，顶到 100
    all_vals = pd.concat([df['corn_f1'], df['soybean_f1']]) * 100
    ymin = np.floor(all_vals.min() / 5) * 5 - 5
    ymax = 100

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    x = np.arange(len(SITES))
    width = 0.26

    for ax, (col, title) in zip(axes, CROPS):
        for k, (key, label, color) in enumerate(MODELS):
            vals = [df[(df['model'] == key) & (df['site'] == s)][col].iloc[0] * 100 for s in SITES]
            bars = ax.bar(x + (k - 1) * width, vals, width, label=label, color=color,
                          edgecolor='black', linewidth=0.5)
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.3, f'{v:.2f}',
                        ha='center', va='bottom', fontsize=7)
        ax.set_xticks(x)
        ax.set_xticklabels(SITES, fontsize=10)
        ax.set_xlabel('站点', fontsize=10)
        ax.set_title(title, fontsize=11, pad=8)
        ax.set_ylim(ymin, ymax)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        ax.set_axisbelow(True)

    axes[0].set_ylabel('F1（%）', fontsize=10)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 1.02), fontsize=10)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('figures/results/fig_within_site_f1.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/results/fig_within_site_f1.pdf', bbox_inches='tight')
    plt.close()

    print('Generated: figures/results/fig_within_site_f1.png / .pdf')
    print(f'y range: {ymin:.0f}–{ymax:.0f}')
    for col, title in CROPS:
        print(title)
        for key, label, _ in MODELS:
            row = [f"{df[(df['model']==key)&(df['site']==s)][col].iloc[0]*100:.1f}" for s in SITES]
            print(f'  {label:9s}', ' '.join(row))


if __name__ == '__main__':
    main()

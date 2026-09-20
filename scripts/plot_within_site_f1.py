#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：三种模型在四个站点的站内玉米、大豆 F1

上下两子图分组柱状图，单栏宽：
  (a) 四站点玉米分类精度   (b) 四站点大豆分类精度
  横轴：站点 A–D；每站并列 ConvGRU、3D U-Net、U-TAE 三根柱
  纵轴：F1（%），两子图同刻度；柱顶标数值
  子图题在各子图下方；图例在整幅图底部
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
CROPS = [('corn_f1', '（a）四站点玉米分类精度'), ('soybean_f1', '（b）四站点大豆分类精度')]


def main():
    df = pd.read_csv('results/summary/within_site_crop_f1.csv')
    df['site'] = df['target'].map(SITE_MAP)

    # 单栏宽约 8 cm ≈ 3.2 in；两子图上下排
    # 单栏宽约 8 cm ≈ 3.2 in；两子图上下排。纵轴从 85 起，留出柱顶横排数字的空间
    fig, axes = plt.subplots(2, 1, figsize=(3.4, 5.4), sharey=True)
    x = np.arange(len(SITES)) * 1.0
    width = 0.27
    ymin, ymax = 85, 100

    for ax, (col, subtitle) in zip(axes, CROPS):
        for k, (key, label, color) in enumerate(MODELS):
            vals = [df[(df['model'] == key) & (df['site'] == s)][col].iloc[0] * 100 for s in SITES]
            bars = ax.bar(x + (k - 1) * width, vals, width, label=label, color=color,
                          edgecolor='black', linewidth=0.4)
            for b, v in zip(bars, vals):
                ax.text(b.get_x() + b.get_width() / 2, v + 0.15, f'{v:.1f}',
                        ha='center', va='bottom', fontsize=6.5)
        ax.set_xticks(x)
        ax.set_xticklabels(SITES, fontsize=8)
        ax.set_xlim(-0.6, len(SITES) - 0.4)
        ax.set_ylim(ymin, ymax)
        ax.set_yticks(np.arange(ymin, ymax + 1, 5))
        ax.set_ylabel('F1（%）', fontsize=8)
        ax.tick_params(axis='y', labelsize=7)
        ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.4)
        ax.set_axisbelow(True)
        ax.set_xlabel(subtitle, fontsize=8.5, labelpad=3)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.0), fontsize=8, handlelength=1.4, columnspacing=1.2)

    plt.tight_layout(rect=[0, 0.035, 1, 1], h_pad=1.0)
    plt.savefig('figures/results/fig_within_site_f1.png', dpi=300, bbox_inches='tight', pad_inches=0.02)
    plt.savefig('figures/results/fig_within_site_f1.pdf', bbox_inches='tight', pad_inches=0.02)
    plt.close()

    print('Generated: figures/results/fig_within_site_f1.png / .pdf')
    print(f'y range: {ymin:.0f}–{ymax:.0f}')
    for col, subtitle in CROPS:
        print(subtitle)
        for key, label, _ in MODELS:
            row = [f"{df[(df['model']==key)&(df['site']==s)][col].iloc[0]*100:.2f}" for s in SITES]
            print(f'  {label:9s}', ' '.join(row))


if __name__ == '__main__':
    main()

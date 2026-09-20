#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成图X：不同源—目标区域组合下三种模型的玉米和大豆F1泛化退化

6子图布局：
    ConvGRU        3D U-Net       U-TAE
玉米 (a)           (b)            (c)
大豆 (d)           (e)            (f)

每个子图：4×4热力图，对角线留空，共用色标
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import figstyle as fs

fs.setup()

SITE_MAP = fs.SITE_MAP
MODEL_MAP = fs.MODEL_LABELS

def prepare_heatmap_data(df, model, crop):
    """
    准备单个子图的热力图数据

    Parameters
    ----------
    df : DataFrame
        包含 model, source, target, corn_loss_pp, soybean_loss_pp
    model : str
        模型名称（小写）
    crop : str
        'corn' 或 'soybean'

    Returns
    -------
    pivot_table : DataFrame, shape (4, 4)
        行=源站，列=目标站，对角线=NaN
    """
    # 筛选模型数据
    model_df = df[df['model'] == model].copy()

    # 转换站点名称
    model_df['source_abbr'] = model_df['source'].map(SITE_MAP)
    model_df['target_abbr'] = model_df['target'].map(SITE_MAP)

    # 选择对应作物的退化列
    loss_col = f'{crop}_loss_pp'

    # 透视表
    pivot = model_df.pivot(index='source_abbr', columns='target_abbr', values=loss_col)

    # 按字母顺序排序
    sites = ['A', 'B', 'C', 'D']
    pivot = pivot.reindex(index=sites, columns=sites)

    # 对角线置为NaN
    for site in sites:
        pivot.loc[site, site] = np.nan

    return pivot

def create_degradation_heatmap():
    """生成6子图合成热力图"""
    # 读取数据
    df = pd.read_csv('results/summary/crop_f1_degradation_36paths.csv')

    # 计算全局色标范围（排除对角线NaN）
    all_values = []
    for model in ['convgru', 'unet3d', 'utae']:
        for crop in ['corn', 'soybean']:
            pivot = prepare_heatmap_data(df, model, crop)
            all_values.extend(pivot.values[~np.isnan(pivot.values)])

    vmin = np.floor(np.min(all_values))
    vmax = np.ceil(np.max(all_values))

    # 通栏 16 cm × 12 cm（4 模 × 3 模），2 行 3 列等大热力图，色标单独放最右
    fig, axes = plt.subplots(2, 3, figsize=(fs.FULL_W, 3 * fs.MODULE), layout='constrained')

    models = fs.MODEL_ORDER
    crops = ['corn', 'soybean']
    crop_names = {'corn': '玉米', 'soybean': '大豆'}
    subplot_labels = ['（a）', '（b）', '（c）', '（d）', '（e）', '（f）']

    for i, crop in enumerate(crops):
        for j, model in enumerate(models):
            ax = axes[i, j]
            pivot = prepare_heatmap_data(df, model, crop)
            sns.heatmap(
                pivot, ax=ax, cmap='YlOrRd', vmin=vmin, vmax=vmax,
                annot=True, fmt='.2f', annot_kws={'size': fs.FS_ANNOT},
                cbar=False, linewidths=0.5, linecolor='gray', square=True
            )
            subplot_idx = i * 3 + j
            ax.set_xlabel(f'{subplot_labels[subplot_idx]}{MODEL_MAP[model]}{crop_names[crop]}泛化退化',
                          fontsize=fs.FS_SUBTITLE, labelpad=2)
            ax.set_ylabel('源站' if j == 0 else '')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    cbar = fig.colorbar(axes[0, 0].collections[0], ax=axes, shrink=0.6, pad=0.01, aspect=30)
    cbar.set_label('泛化退化（个百分点）', fontsize=fs.FS_TEXT)
    cbar.ax.tick_params(labelsize=fs.FS_TICK)
    fig.supxlabel('列为目标站', fontsize=fs.FS_TEXT)

    output_path = 'figures/results/fig_degradation_heatmap.png'
    plt.savefig(output_path)
    print(f"已保存：{output_path}")
    output_pdf = 'figures/results/fig_degradation_heatmap.pdf'
    plt.savefig(output_pdf)
    print(f"已保存：{output_pdf}")
    plt.close()

    # 输出数据摘要
    print("\n数据摘要：")
    print(f"全局退化范围：{vmin:.2f} ~ {vmax:.2f} pp")

    print("\n各模型-作物组合统计：")
    for model in models:
        for crop in crops:
            pivot = prepare_heatmap_data(df, model, crop)
            valid_values = pivot.values[~np.isnan(pivot.values)]
            print(f"{MODEL_MAP[model]}-{crop_names[crop]}: "
                  f"mean={np.mean(valid_values):.2f}, "
                  f"std={np.std(valid_values):.2f}, "
                  f"min={np.min(valid_values):.2f}, "
                  f"max={np.max(valid_values):.2f}")

if __name__ == '__main__':
    create_degradation_heatmap()

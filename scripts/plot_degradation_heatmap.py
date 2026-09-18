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

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager

# 配置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 站点映射
SITE_MAP = {
    'iw_2023': 'A',
    'iw2_2023': 'B',
    'ida_2023': 'C',
    'il_2023': 'D'
}

MODEL_MAP = {
    'convgru': 'ConvGRU',
    'unet3d': '3D U-Net',
    'utae': 'U-TAE'
}

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

    # 创建画布：2行3列
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))

    # 定义子图
    models = ['convgru', 'unet3d', 'utae']
    crops = ['corn', 'soybean']
    crop_names = {'corn': '玉米', 'soybean': '大豆'}
    subplot_labels = ['(a)', '(b)', '(c)', '(d)', '(e)', '(f)']

    # 绘制6个子图
    for i, crop in enumerate(crops):
        for j, model in enumerate(models):
            ax = axes[i, j]

            # 准备数据
            pivot = prepare_heatmap_data(df, model, crop)

            # 绘制热力图（保留数值注解）
            sns.heatmap(
                pivot,
                ax=ax,
                cmap='YlOrRd',
                vmin=vmin,
                vmax=vmax,
                annot=True,  # 保留数值注解
                fmt='.2f',
                cbar=(j == 2),  # 只在最右侧显示色标
                cbar_kws={'label': '泛化退化 (pp)'} if j == 2 else None,
                linewidths=0.5,
                linecolor='gray',
                square=True
            )

            # 设置标题和标签（去掉英文）
            subplot_idx = i * 3 + j
            title = f'{subplot_labels[subplot_idx]} {MODEL_MAP[model]}{crop_names[crop]}泛化退化'
            ax.set_title(title, fontsize=12, pad=10)

            ax.set_xlabel('目标站', fontsize=10)
            ax.set_ylabel('源站', fontsize=10)

            # 旋转标签
            ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
            ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    # 调整布局（图名和图注将在正文中给出）
    plt.tight_layout()

    # 保存
    output_path = 'figures/results/fig_degradation_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"已保存：{output_path}")

    # 同时保存PDF版本
    output_pdf = 'figures/results/fig_degradation_heatmap.pdf'
    plt.savefig(output_pdf, bbox_inches='tight')
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

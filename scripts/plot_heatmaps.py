#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成跨站泛化热力图
从原始 36 路径数据直接生成三个模型的迁移路径热力图
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# 读取原始 36 路径数据
df = pd.read_csv('results/summary/generalization_degradation_36paths.csv')

# 站点映射：数据集ID → 论文代号ABCD
site_map = {
    'iw_2023': 'A',
    'iw2_2023': 'B',
    'ida_2023': 'C',
    'il_2023': 'D'
}
df['source_display'] = df['source'].map(site_map)
df['target_display'] = df['target'].map(site_map)

# 站点顺序
site_order = ['A', 'B', 'C', 'D']

# 创建 3 个子图
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

models = [
    ('utae', 'U-TAE'),
    ('unet3d', '3D U-Net'),
    ('convgru', 'ConvGRU')
]

for ax, (model_key, model_name) in zip(axes, models):
    # 提取该模型的数据并构建矩阵
    model_df = df[df['model'] == model_key].copy()

    # 构建迁移矩阵
    matrix = model_df.pivot(
        index='source_display',
        columns='target_display',
        values='cross_crop_miou_mean'
    )

    # 确保顺序一致
    matrix = matrix.reindex(index=site_order, columns=site_order)

    # 绘制热力图
    sns.heatmap(
        matrix,
        annot=True,
        fmt='.2f',
        cmap='RdYlGn',
        vmin=0.70,
        vmax=0.95,
        cbar_kws={'label': 'Crop-mIoU'},
        ax=ax,
        square=True,
        linewidths=0.5,
        cbar=(ax == axes[-1])  # 只在最后一个子图显示色标
    )

    ax.set_title(f'{model_name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('目标站', fontsize=12)
    ax.set_ylabel('源站', fontsize=12)
    ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig('figures/results/fig_transfer_heatmaps.png', dpi=300, bbox_inches='tight')
print("Generated: figures/results/fig_transfer_heatmaps.png")
plt.close()

# 生成泛化退化热力图（对角线留空）
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 统一色标范围：0-10 pp
vmin, vmax = 0, 10

for ax, (model_key, model_name) in zip(axes, models):
    model_df = df[df['model'] == model_key].copy()

    matrix = model_df.pivot(
        index='source_display',
        columns='target_display',
        values='generalization_loss_crop_miou_pp'
    )

    matrix = matrix.reindex(index=site_order, columns=site_order)

    # 对角线设为 NaN（留空）
    for i in range(len(site_order)):
        matrix.iloc[i, i] = np.nan

    sns.heatmap(
        matrix,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        vmin=vmin,
        vmax=vmax,
        cbar_kws={'label': '泛化退化 (pp)'},
        ax=ax,
        square=True,
        linewidths=0.5,
        cbar=(ax == axes[-1])  # 只在最后一个子图显示色标
    )

    ax.set_title(f'{model_name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('目标站', fontsize=12)
    ax.set_ylabel('源站', fontsize=12)
    ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig('figures/results/fig_degradation_heatmaps.png', dpi=300, bbox_inches='tight')
print("Generated: figures/results/fig_degradation_heatmaps.png")
plt.close()

print("\n=== Heatmap Generation Complete ===")
print("- fig_transfer_heatmaps.png: Cross-site Crop-mIoU")
print("- fig_degradation_heatmaps.png: Generalization degradation (pp)")

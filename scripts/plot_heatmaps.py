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

# 站点映射
site_map = {
    'ida_2023': 'IDA',
    'il_2023': 'IL',
    'iw2_2023': 'IW2',
    'iw_2023': 'IW'
}
df['source_display'] = df['source'].map(site_map)
df['target_display'] = df['target'].map(site_map)

# 站点顺序
site_order = ['IDA', 'IL', 'IW2', 'IW']

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
        linewidths=0.5
    )

    ax.set_title(f'{model_name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Target Site', fontsize=12)
    ax.set_ylabel('Source Site', fontsize=12)
    ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig('figures/results/fig_transfer_heatmaps.png', dpi=300, bbox_inches='tight')
print("Generated: figures/results/fig_transfer_heatmaps.png")
plt.close()

# 生成泛化退化热力图
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for ax, (model_key, model_name) in zip(axes, models):
    model_df = df[df['model'] == model_key].copy()

    matrix = model_df.pivot(
        index='source_display',
        columns='target_display',
        values='generalization_loss_crop_miou_pp'
    )

    matrix = matrix.reindex(index=site_order, columns=site_order)

    sns.heatmap(
        matrix,
        annot=True,
        fmt='.2f',
        cmap='YlOrRd',
        vmin=0,
        vmax=15,
        cbar_kws={'label': 'Degradation (pp)'},
        ax=ax,
        square=True,
        linewidths=0.5
    )

    ax.set_title(f'{model_name}', fontsize=14, fontweight='bold')
    ax.set_xlabel('Target Site', fontsize=12)
    ax.set_ylabel('Source Site', fontsize=12)
    ax.tick_params(labelsize=11)

plt.tight_layout()
plt.savefig('figures/results/fig_degradation_heatmaps.png', dpi=300, bbox_inches='tight')
print("Generated: figures/results/fig_degradation_heatmaps.png")
plt.close()

print("\n=== Heatmap Generation Complete ===")
print("- fig_transfer_heatmaps.png: Cross-site Crop-mIoU")
print("- fig_degradation_heatmaps.png: Generalization degradation (pp)")

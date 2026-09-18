#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成泛化分析科研图表
从 results/processed/generalization_analysis.csv 读取
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体和样式
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# 读取处理后的数据
def load_section(filepath, section_name):
    """从 CSV 文件中读取特定章节"""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_idx = None
    for i, line in enumerate(lines):
        if line.strip() == f'### {section_name} ###':
            start_idx = i + 1
            break

    if start_idx is None:
        return None

    # 找到下一个分节标记或文件结束
    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if lines[i].strip().startswith('###') and lines[i].strip().endswith('###'):
            end_idx = i
            break

    # 提取该段内容
    section_lines = [l.strip() for l in lines[start_idx:end_idx] if l.strip()]
    from io import StringIO
    return pd.read_csv(StringIO('\n'.join(section_lines)))

model_summary = load_section('results/processed/generalization_analysis.csv', 'model_summary')
asymmetry_df = load_section('results/processed/generalization_analysis.csv', 'asymmetry')

# 模型显示名映射
model_display = {
    'utae': 'U-TAE',
    'unet3d': '3D U-Net',
    'convgru': 'ConvGRU'
}

# ========== 图 A：模型跨站平均 Crop-mIoU 对比 ==========
fig, ax = plt.subplots(figsize=(6, 4))
models = ['utae', 'unet3d', 'convgru']
means = model_summary.set_index('model').loc[models, 'cross_crop_miou_mean_mean'].values
stds = model_summary.set_index('model').loc[models, 'cross_crop_miou_mean_std'].values

x_pos = np.arange(len(models))
bars = ax.bar(x_pos, means, yerr=stds, capsize=5,
              color=['#3B6DFF', '#6EE7B7', '#E9A568'],
              edgecolor='black', linewidth=0.8)

ax.set_ylabel('跨站点 Crop-mIoU', fontsize=11)
ax.set_xticks(x_pos)
ax.set_xticklabels([model_display[m] for m in models], fontsize=10)
ax.set_ylim(0.75, 0.85)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# 添加数值标签
for i, (m, s) in enumerate(zip(means, stds)):
    ax.text(i, m + s + 0.005, f'{m:.4f}', ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('figures/results/fig_model_comparison_cropmIoU.png', dpi=300, bbox_inches='tight')
plt.close()
print("已生成: figures/results/fig_model_comparison_cropmIoU.png")

# ========== 图 B：泛化退化百分点分布（箱线图） ==========
fig, ax = plt.subplots(figsize=(6, 4))

# 从 asymmetry 数据中提取不对称性值作为泛化差异的代理
degradation_data = []
for model in models:
    subset = asymmetry_df[asymmetry_df['model'] == model]
    degradation_data.append(subset['asymmetry'].values)

bp = ax.boxplot(degradation_data, tick_labels=[model_display[m] for m in models],
                patch_artist=True, widths=0.6)

colors = ['#3B6DFF', '#6EE7B7', '#E9A568']
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_ylabel('迁移不对称性 (Crop-mIoU 差值)', fontsize=11)
ax.grid(axis='y', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('figures/results/fig_degradation_boxplot.png', dpi=300, bbox_inches='tight')
plt.close()
print("已生成: figures/results/fig_degradation_boxplot.png")

# ========== 图 D：方向不对称性散点图 ==========
fig, ax = plt.subplots(figsize=(6, 6))

for model, color in zip(models, colors):
    subset = asymmetry_df[asymmetry_df['model'] == model]
    ax.scatter(subset['forward'], subset['backward'],
              label=model_display[model], alpha=0.7,
              s=80, color=color, edgecolors='black', linewidths=0.5)

# 对角线
ax.plot([0.70, 0.87], [0.70, 0.87], 'k--', linewidth=1, alpha=0.5)

ax.set_xlabel('正向迁移 Crop-mIoU', fontsize=11)
ax.set_ylabel('反向迁移 Crop-mIoU', fontsize=11)
ax.set_xlim(0.70, 0.87)
ax.set_ylim(0.70, 0.87)
ax.set_aspect('equal')
ax.legend(frameon=True, loc='upper left', fontsize=9)
ax.grid(alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('figures/results/fig_asymmetry_scatter.png', dpi=300, bbox_inches='tight')
plt.close()
print("已生成: figures/results/fig_asymmetry_scatter.png")

print("\n图表生成完成。")
print("注意: 迁移路径热力图需要完整 36 路径数据，当前从 processed 文件无法重建。")

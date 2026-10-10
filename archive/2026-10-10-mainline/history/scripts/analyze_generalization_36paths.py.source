#!/usr/bin/env python3
"""
分析 36 条跨站泛化路径的退化模式

输入：results/summary/generalization_degradation_36paths.csv
输出：results/processed/generalization_analysis.csv
"""

import pandas as pd
import numpy as np

# 读取数据
df = pd.read_csv('results/summary/generalization_degradation_36paths.csv')

# 站点映射（移除 _2023 后缀用于显示）
site_map = {
    'ida_2023': 'IDA',
    'il_2023': 'IL',
    'iw2_2023': 'IW2',
    'iw_2023': 'IW'
}

df['source_display'] = df['source'].map(site_map)
df['target_display'] = df['target'].map(site_map)

# ========== 1. 按模型汇总 ==========
model_summary = df.groupby('model').agg({
    'cross_crop_miou_mean': ['mean', 'std', 'min', 'max'],
    'generalization_loss_crop_miou_pp': ['mean', 'std', 'min', 'max']
}).round(4)

model_summary.columns = ['_'.join(col) for col in model_summary.columns]
model_summary = model_summary.reset_index()

print("=== 模型跨站性能汇总 ===")
print(model_summary)
print()

# ========== 2. 按源站汇总 ==========
source_summary = df.groupby(['model', 'source_display']).agg({
    'cross_crop_miou_mean': 'mean',
    'generalization_loss_crop_miou_pp': 'mean'
}).round(4).reset_index()

print("=== 按源站汇总（各模型） ===")
print(source_summary.pivot(index='source_display', columns='model',
                            values='cross_crop_miou_mean'))
print()

# ========== 3. 按目标站汇总 ==========
target_summary = df.groupby(['model', 'target_display']).agg({
    'cross_crop_miou_mean': 'mean',
    'generalization_loss_crop_miou_pp': 'mean'
}).round(4).reset_index()

print("=== 按目标站汇总（各模型） ===")
print(target_summary.pivot(index='target_display', columns='model',
                            values='cross_crop_miou_mean'))
print()

# ========== 4. 迁移路径矩阵 ==========
print("=== U-TAE 迁移路径 Crop-mIoU ===")
utae_matrix = df[df['model'] == 'utae'].pivot(
    index='source_display',
    columns='target_display',
    values='cross_crop_miou_mean'
).round(4)
print(utae_matrix)
print()

print("=== 3D U-Net 迁移路径 Crop-mIoU ===")
unet3d_matrix = df[df['model'] == 'unet3d'].pivot(
    index='source_display',
    columns='target_display',
    values='cross_crop_miou_mean'
).round(4)
print(unet3d_matrix)
print()

print("=== ConvGRU 迁移路径 Crop-mIoU ===")
convgru_matrix = df[df['model'] == 'convgru'].pivot(
    index='source_display',
    columns='target_display',
    values='cross_crop_miou_mean'
).round(4)
print(convgru_matrix)
print()

# ========== 5. 方向不对称性 ==========
# 找到所有互逆路径对
pairs = []
for _, row in df.iterrows():
    reverse = df[(df['model'] == row['model']) &
                 (df['source'] == row['target']) &
                 (df['target'] == row['source'])]
    if not reverse.empty:
        src_display = row['source_display']
        tgt_display = row['target_display']
        if src_display < tgt_display:  # 避免重复
            forward = row['cross_crop_miou_mean']
            backward = reverse.iloc[0]['cross_crop_miou_mean']
            pairs.append({
                'model': row['model'],
                'path': f"{src_display}<->{tgt_display}",
                'forward': forward,
                'backward': backward,
                'asymmetry': abs(forward - backward)
            })

asymmetry_df = pd.DataFrame(pairs).round(4)
print("=== 迁移方向不对称性 ===")
print(asymmetry_df.sort_values('asymmetry', ascending=False))
print()

# ========== 6. 保存处理结果 ==========
output = {
    'model_summary': model_summary,
    'source_summary': source_summary,
    'target_summary': target_summary,
    'asymmetry': asymmetry_df
}

# 保存到单个 CSV（追加模式）
with open('results/processed/generalization_analysis.csv', 'w') as f:
    for name, data in output.items():
        f.write(f"\n### {name} ###\n")
        data.to_csv(f, index=False)

print("结果已保存到 results/processed/generalization_analysis.csv")

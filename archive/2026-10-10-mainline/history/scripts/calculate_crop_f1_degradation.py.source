#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算玉米和大豆的泛化退化

ΔF1 = 100 × (站内OOF F1 - 跨站平均F1)
相对退化比例 = 100 × (站内OOF F1 - 跨站平均F1) / 站内OOF F1
两种口径分别输出，原有百分点结果保持不变。
"""

import pandas as pd
import numpy as np

def calculate_degradation():
    """计算泛化退化"""
    # 读取站内基准
    within_df = pd.read_csv('results/summary/within_site_crop_f1.csv')

    # 读取跨站结果
    cross_df = pd.read_csv('results/summary/cross_site_crop_f1_summary.csv')

    results = []

    for _, cross_row in cross_df.iterrows():
        model = cross_row['model']
        target = cross_row['target']

        # 查找该目标站的站内基准
        within_row = within_df[
            (within_df['model'] == model) &
            (within_df['target'] == target)
        ]

        if len(within_row) == 0:
            print(f"警告：未找到 {model} {target} 的站内基准")
            continue

        within_row = within_row.iloc[0]

        # 计算泛化退化（百分点）
        corn_loss = 100 * (within_row['corn_f1'] - cross_row['corn_f1_mean'])
        soybean_loss = 100 * (within_row['soybean_f1'] - cross_row['soybean_f1_mean'])

        results.append({
            'model': model,
            'source': cross_row['source'],
            'target': target,
            'within_corn_f1': within_row['corn_f1'],
            'cross_corn_f1_mean': cross_row['corn_f1_mean'],
            'cross_corn_f1_std': cross_row['corn_f1_std'],
            'corn_loss_pp': corn_loss,
            'within_soybean_f1': within_row['soybean_f1'],
            'cross_soybean_f1_mean': cross_row['soybean_f1_mean'],
            'cross_soybean_f1_std': cross_row['soybean_f1_std'],
            'soybean_loss_pp': soybean_loss
        })

    return pd.DataFrame(results)


def calculate_relative_degradation(degradation_df):
    """以同一模型在目标站的站内汇总 F1 为分母，计算相对退化比例（%）。"""
    result = degradation_df.drop(columns=['corn_loss_pp', 'soybean_loss_pp']).copy()
    for crop in ('corn', 'soybean'):
        within = result[f'within_{crop}_f1']
        cross = result[f'cross_{crop}_f1_mean']
        if not (np.isfinite(within) & (within > 0) & np.isfinite(cross)).all():
            raise ValueError(f'{crop}: 相对退化要求站内 F1 为有限正数、跨站 F1 为有限数')
        result[f'{crop}_relative_loss_pct'] = 100 * (within - cross) / within
    return result


if __name__ == '__main__':
    print("正在计算玉米/大豆泛化退化...")

    degradation_df = calculate_degradation()

    # 保存完整数据
    degradation_df.to_csv('results/summary/crop_f1_degradation_36paths.csv',
                          index=False, float_format='%.6f')
    print("已保存：results/summary/crop_f1_degradation_36paths.csv")

    relative_df = calculate_relative_degradation(degradation_df)
    relative_df.to_csv('results/summary/crop_f1_relative_degradation_36paths.csv',
                       index=False, float_format='%.6f')
    print("已保存：results/summary/crop_f1_relative_degradation_36paths.csv")
    print("\n相对退化比例（%，12条路径均值）：")
    print(relative_df.groupby('model')[['corn_relative_loss_pct',
                                       'soybean_relative_loss_pct']].mean())

    # 统计摘要
    print("\n泛化退化统计（按模型）：")
    summary = degradation_df.groupby('model')[['corn_loss_pp', 'soybean_loss_pp']].agg(['mean', 'std', 'min', 'max'])
    print(summary)

    # 最困难路径（玉米）
    print("\n玉米泛化退化最严重的5条路径：")
    top_corn = degradation_df.nlargest(5, 'corn_loss_pp')[['model', 'source', 'target', 'corn_loss_pp']]
    print(top_corn.to_string(index=False))

    # 最困难路径（大豆）
    print("\n大豆泛化退化最严重的5条路径：")
    top_soybean = degradation_df.nlargest(5, 'soybean_loss_pp')[['model', 'source', 'target', 'soybean_loss_pp']]
    print(top_soybean.to_string(index=False))

    # 检查样本
    print(f"\n总路径数：{len(degradation_df)}")
    print(f"预期：36（3模型×12路径）")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从混淆矩阵计算玉米和大豆 F1

混淆矩阵编码：
- 类别 0: 玉米 (Corn)
- 类别 1: 大豆 (Soybean)
- 类别 2: 其他 (Other)

cm_ij: 真实类别 i，预测类别 j
"""

import pandas as pd
import numpy as np

def calculate_f1_from_cm(cm):
    """
    从 9 元素混淆矩阵计算各类别 F1

    Parameters
    ----------
    cm : array-like, shape (9,)
        展平的混淆矩阵 [cm_00, cm_01, cm_02, cm_10, cm_11, cm_12, cm_20, cm_21, cm_22]

    Returns
    -------
    dict : {'corn_f1', 'soybean_f1', 'other_f1'}
    """
    cm = np.array(cm).reshape(3, 3)

    f1_scores = {}
    class_names = ['corn', 'other', 'soybean']  # 修复：训练时标签-1，corn=0, other=1, soybean=2

    for i, name in enumerate(class_names):
        # TP: 对角线元素
        tp = cm[i, i]

        # FN: 该行非对角线元素之和（真实为该类，预测为其他）
        fn = cm[i, :].sum() - tp

        # FP: 该列非对角线元素之和（真实为其他，预测为该类）
        fp = cm[:, i].sum() - tp

        # Precision 和 Recall
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0

        # F1
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        f1_scores[f'{name}_f1'] = f1

    return f1_scores

def process_within_site_baseline():
    """处理站内 OOF 基准数据"""
    df = pd.read_csv('results/summary/within_site_oof_baseline.csv')

    results = []
    for _, row in df.iterrows():
        cm_cols = [f'cm_{i}{j}' for i in range(3) for j in range(3)]
        cm = row[cm_cols].values

        f1_scores = calculate_f1_from_cm(cm)

        results.append({
            'model': row['model'],
            'target': row['target'],
            'corn_f1': f1_scores['corn_f1'],
            'soybean_f1': f1_scores['soybean_f1'],
            'other_f1': f1_scores['other_f1'],
            'oa': cm.sum() / row['valid_pixels'] if row['valid_pixels'] > 0 else 0
        })

    return pd.DataFrame(results)

if __name__ == '__main__':
    # 计算站内基准
    within_f1 = process_within_site_baseline()
    within_f1.to_csv('results/summary/within_site_crop_f1.csv', index=False, float_format='%.6f')
    print("已生成: results/summary/within_site_crop_f1.csv")

    # 显示摘要
    print("\n站内 OOF 玉米/大豆 F1 基准（按模型汇总）：")
    summary = within_f1.groupby('model')[['corn_f1', 'soybean_f1']].agg(['mean', 'std'])
    print(summary)

    print("\n注意：跨站 36 条路径的混淆矩阵数据缺失。")
    print("需要提供跨站实验的原始混淆矩阵（每条路径 5-fold 的 cm_00 到 cm_22）。")

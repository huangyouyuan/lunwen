#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 legacy 跨站实验结果中提取混淆矩阵并计算玉米/大豆 F1

输入：legacy/experiment-results/cross_site_all_20260916/
输出：results/raw/cross_site_confusion_matrices.csv
      results/summary/cross_site_crop_f1.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re

def parse_experiment_path(exp_path):
    """
    解析实验路径，提取模型和源站
    例如：convgru__ida_2023__2023convgruidaresults_ad649c5b
    """
    parts = exp_path.name.split('__')
    if len(parts) >= 2:
        model = parts[0]
        source = parts[1]
        return model, source
    return None, None

def cm_to_standard_order(row):
    """
    将 cm_gt_X_pred_Y 格式转换为标准 cm_ij 顺序
    类别映射：corn=0, other=1, soybean=2（与站内一致）
    """
    cm = np.zeros(9, dtype=np.int64)

    # gt=corn (i=0)
    cm[0] = row['cm_gt_corn_pred_corn']      # cm_00
    cm[1] = row['cm_gt_corn_pred_other']     # cm_01
    cm[2] = row['cm_gt_corn_pred_soybean']   # cm_02

    # gt=other (i=1)
    cm[3] = row['cm_gt_other_pred_corn']     # cm_10
    cm[4] = row['cm_gt_other_pred_other']    # cm_11
    cm[5] = row['cm_gt_other_pred_soybean']  # cm_12

    # gt=soybean (i=2)
    cm[6] = row['cm_gt_soybean_pred_corn']   # cm_20
    cm[7] = row['cm_gt_soybean_pred_other']  # cm_21
    cm[8] = row['cm_gt_soybean_pred_soybean'] # cm_22

    return cm

def calculate_f1_from_cm(cm):
    """从9元素混淆矩阵计算各类别F1"""
    cm = np.array(cm).reshape(3, 3)

    f1_scores = {}
    class_names = ['corn', 'other', 'soybean']  # 修正顺序

    for i, name in enumerate(class_names):
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        f1_scores[f'{name}_f1'] = f1

    return f1_scores

def extract_cross_site_results():
    """扫描所有跨站实验结果"""
    base_path = Path('legacy/experiment-results/cross_site_all_20260916')

    all_cms = []

    # 遍历所有实验目录
    for exp_dir in sorted(base_path.iterdir()):
        if not exp_dir.is_dir():
            continue

        model, source = parse_experiment_path(exp_dir)
        if model is None:
            continue

        # 遍历目标站点
        for target_dir in sorted(exp_dir.iterdir()):
            if not target_dir.is_dir():
                continue

            target = target_dir.name
            metrics_file = target_dir / 'metrics_summary.csv'

            if not metrics_file.exists():
                print(f"警告：缺失 {metrics_file}")
                continue

            # 读取该路径的结果
            df = pd.read_csv(metrics_file, encoding='utf-8-sig')

            # 过滤 fold 级别数据
            fold_data = df[df['result_type'] == 'fold'].copy()

            if len(fold_data) == 0:
                print(f"警告：{model} {source}->{target} 无fold数据")
                continue

            # 提取每个 fold 的混淆矩阵
            for _, row in fold_data.iterrows():
                fold = row['fold']
                cm = cm_to_standard_order(row)

                all_cms.append({
                    'model': model,
                    'source': source,
                    'target': target,
                    'fold': fold,
                    **{f'cm_{i}{j}': cm[i*3+j] for i in range(3) for j in range(3)}
                })

    return pd.DataFrame(all_cms)

def calculate_cross_site_f1(cm_df):
    """从混淆矩阵计算各路径的玉米/大豆 F1"""
    results = []

    # 按 (model, source, target, fold) 计算
    for _, row in cm_df.iterrows():
        cm_cols = [f'cm_{i}{j}' for i in range(3) for j in range(3)]
        cm = row[cm_cols].values

        f1_scores = calculate_f1_from_cm(cm)

        results.append({
            'model': row['model'],
            'source': row['source'],
            'target': row['target'],
            'fold': row['fold'],
            'corn_f1': f1_scores['corn_f1'],
            'soybean_f1': f1_scores['soybean_f1'],
            'other_f1': f1_scores['other_f1']
        })

    return pd.DataFrame(results)

if __name__ == '__main__':
    print("正在提取跨站混淆矩阵...")
    cm_df = extract_cross_site_results()

    print(f"提取到 {len(cm_df)} 条记录")
    print(f"路径数：{cm_df.groupby(['model', 'source', 'target']).ngroups}")

    # 保存原始混淆矩阵
    cm_df.to_csv('results/raw/cross_site_confusion_matrices.csv', index=False)
    print("已保存：results/raw/cross_site_confusion_matrices.csv")

    # 计算 F1
    print("\n正在计算玉米/大豆 F1...")
    f1_df = calculate_cross_site_f1(cm_df)
    f1_df.to_csv('results/summary/cross_site_crop_f1_per_fold.csv', index=False, float_format='%.6f')
    print("已保存：results/summary/cross_site_crop_f1_per_fold.csv")

    # 汇总统计（每条路径5-fold平均）
    summary = f1_df.groupby(['model', 'source', 'target']).agg({
        'corn_f1': ['mean', 'std'],
        'soybean_f1': ['mean', 'std']
    }).reset_index()
    summary.columns = ['model', 'source', 'target',
                       'corn_f1_mean', 'corn_f1_std',
                       'soybean_f1_mean', 'soybean_f1_std']
    summary.to_csv('results/summary/cross_site_crop_f1_summary.csv', index=False, float_format='%.6f')
    print("已保存：results/summary/cross_site_crop_f1_summary.csv")

    print(f"\n样本数据（前3条路径）：")
    print(summary.head(3))

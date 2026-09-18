#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从站内五折原始混淆矩阵计算玉米 F1、大豆 F1 和 OA

类别顺序（训练时标签减 1）：corn=0, other=1, soybean=2

输入：D:/20{site}/2023{model}{site}results/summary/metrics_summary.csv
      每个文件含 5 个 fold 行（各测试折 CM）和 1 个 oof_pooled 行（汇总 CM）
输出：results/raw/within_site_confusion_matrices.csv   （12 组 × 5 折 + pooled）
      results/summary/within_site_crop_f1.csv          （OOF pooled 指标）
      results/summary/within_site_crop_f1_fold_stats.csv（五折 mean ± std）
"""

from pathlib import Path

import numpy as np
import pandas as pd

CLASS_ORDER = ['corn', 'other', 'soybean']
WITHIN_ROOT = Path('D:/')
MODELS = ['convgru', 'unet3d', 'utae']
SITES = ['ida', 'il', 'iw2', 'iw']


def cm_from_row(row):
    """把 cm_gt_X_pred_Y 列整理成按 CLASS_ORDER 排列的 3×3 矩阵"""
    cm = np.zeros((3, 3), dtype=np.int64)
    for i, gt in enumerate(CLASS_ORDER):
        for j, pred in enumerate(CLASS_ORDER):
            cm[i, j] = row[f'cm_gt_{gt}_pred_{pred}']
    return cm


def metrics_from_cm(cm):
    """F1（各类）与 OA = 对角线之和 / 全部像元"""
    out = {}
    for i, name in enumerate(CLASS_ORDER):
        tp = cm[i, i]
        fn = cm[i, :].sum() - tp
        fp = cm[:, i].sum() - tp
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        out[f'{name}_f1'] = (2 * precision * recall / (precision + recall)
                             if (precision + recall) > 0 else 0.0)
    out['oa'] = np.trace(cm) / cm.sum()
    return out


def within_site_file(model, site):
    """12 个站内结果目录的命名不完全一致，按实际存在的两种写法查找"""
    candidates = [
        WITHIN_ROOT / f'20{site}' / f'2023{model}{site}results' / 'summary' / 'metrics_summary.csv',
        WITHIN_ROOT / f'20{site}' / f'2023{site}{model}results' / 'summary' / 'metrics_summary.csv',
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(f'未找到 {model}/{site} 的站内结果：{[str(c) for c in candidates]}')


def load_within_site():
    raw_rows, pooled_rows, fold_rows = [], [], []

    for model in MODELS:
        for site in SITES:
            df = pd.read_csv(within_site_file(model, site), encoding='utf-8-sig')
            target = f'{site}_2023'

            fold_df = df[df['result_type'] == 'fold']
            pooled_df = df[df['result_type'] == 'oof_pooled']
            if len(fold_df) != 5 or len(pooled_df) != 1:
                raise ValueError(f'{model}/{site}: fold 行 {len(fold_df)}，pooled 行 {len(pooled_df)}')

            for _, row in fold_df.iterrows():
                cm = cm_from_row(row)
                raw_rows.append({'model': model, 'target': target, 'result_type': 'fold',
                                 'fold': int(row['fold']),
                                 **{f'cm_{i}{j}': cm[i, j] for i in range(3) for j in range(3)}})
                fold_rows.append({'model': model, 'target': target, 'fold': int(row['fold']),
                                  **metrics_from_cm(cm)})

            pooled = pooled_df.iloc[0]
            cm = cm_from_row(pooled)
            fold_sum = sum(cm_from_row(r) for _, r in fold_df.iterrows())
            if not np.array_equal(cm, fold_sum):
                raise ValueError(f'{model}/{site}: pooled CM 与五折 CM 之和不一致')
            raw_rows.append({'model': model, 'target': target, 'result_type': 'oof_pooled',
                             'fold': np.nan,
                             **{f'cm_{i}{j}': cm[i, j] for i in range(3) for j in range(3)}})
            pooled_rows.append({'model': model, 'target': target,
                                'valid_pixels': int(cm.sum()), **metrics_from_cm(cm)})

    return pd.DataFrame(raw_rows), pd.DataFrame(pooled_rows), pd.DataFrame(fold_rows)


if __name__ == '__main__':
    raw_df, pooled_df, fold_df = load_within_site()

    Path('results/raw').mkdir(parents=True, exist_ok=True)
    raw_df.to_csv('results/raw/within_site_confusion_matrices.csv', index=False)
    print('已生成: results/raw/within_site_confusion_matrices.csv')

    pooled_df = pooled_df[['model', 'target', 'corn_f1', 'soybean_f1', 'other_f1', 'oa', 'valid_pixels']]
    pooled_df.to_csv('results/summary/within_site_crop_f1.csv', index=False, float_format='%.6f')
    print('已生成: results/summary/within_site_crop_f1.csv')

    stats = (fold_df.groupby(['model', 'target'])[['corn_f1', 'soybean_f1', 'oa']]
             .agg(['mean', 'std']))
    stats.columns = [f'{m}_{s}' for m, s in stats.columns]
    stats = stats.reset_index()
    stats.to_csv('results/summary/within_site_crop_f1_fold_stats.csv', index=False, float_format='%.6f')
    print('已生成: results/summary/within_site_crop_f1_fold_stats.csv')

    print('\n站内 OOF pooled（按模型汇总）:')
    print(pooled_df.groupby('model')[['corn_f1', 'soybean_f1', 'oa']].mean().round(4))
    print('\n五折标准差范围:')
    for col in ['corn_f1_std', 'soybean_f1_std', 'oa_std']:
        print(f'  {col}: {stats[col].min():.4f} ~ {stats[col].max():.4f}')

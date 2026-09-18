#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成论文核心表格：
1. 站内玉米/大豆F1基准表
2. 跨站玉米/大豆F1及泛化退化表
3. 模型显著性检验表（分别对玉米和大豆）
"""

import pandas as pd
import numpy as np
from scipy import stats

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

def generate_table1_within_site_baseline():
    """表1：站内分类性能基准"""
    df = pd.read_csv('results/summary/within_site_crop_f1.csv')

    # 转换站点名称
    df['site'] = df['target'].map(SITE_MAP)
    df['model_name'] = df['model'].map(MODEL_MAP)

    # 透视表：行=模型，列=站点
    pivot_corn = df.pivot(index='model_name', columns='site', values='corn_f1')
    pivot_soybean = df.pivot(index='model_name', columns='site', values='soybean_f1')

    # 添加均值
    pivot_corn['Mean'] = df.groupby('model_name')['corn_f1'].mean()
    pivot_soybean['Mean'] = df.groupby('model_name')['soybean_f1'].mean()

    # 合并
    result = pd.DataFrame()
    for model in ['ConvGRU', '3D U-Net', 'U-TAE']:
        row_corn = pivot_corn.loc[model].copy()
        row_corn.name = f'{model} (Corn)'

        row_soybean = pivot_soybean.loc[model].copy()
        row_soybean.name = f'{model} (Soybean)'

        result = pd.concat([result, row_corn.to_frame().T, row_soybean.to_frame().T])

    return result

def generate_table2_cross_site_performance():
    """表2：跨站分类性能与泛化退化（简化版：均值±std）"""
    df = pd.read_csv('results/summary/crop_f1_degradation_36paths.csv')

    df['source_abbr'] = df['source'].map(SITE_MAP)
    df['target_abbr'] = df['target'].map(SITE_MAP)
    df['model_name'] = df['model'].map(MODEL_MAP)

    # 按模型和作物汇总
    summary_data = []

    for model in ['ConvGRU', '3D U-Net', 'U-TAE']:
        model_df = df[df['model_name'] == model]

        corn_cross_mean = model_df['cross_corn_f1_mean'].mean()
        corn_cross_std = model_df['cross_corn_f1_mean'].std()
        corn_loss_mean = model_df['corn_loss_pp'].mean()
        corn_loss_std = model_df['corn_loss_pp'].std()

        soybean_cross_mean = model_df['cross_soybean_f1_mean'].mean()
        soybean_cross_std = model_df['cross_soybean_f1_mean'].std()
        soybean_loss_mean = model_df['soybean_loss_pp'].mean()
        soybean_loss_std = model_df['soybean_loss_pp'].std()

        summary_data.append({
            'Model': model,
            'Crop': 'Corn',
            'Cross F1 (mean±std)': f'{corn_cross_mean:.4f}±{corn_cross_std:.4f}',
            'Degradation (pp, mean±std)': f'{corn_loss_mean:.2f}±{corn_loss_std:.2f}'
        })

        summary_data.append({
            'Model': model,
            'Crop': 'Soybean',
            'Cross F1 (mean±std)': f'{soybean_cross_mean:.4f}±{soybean_cross_std:.4f}',
            'Degradation (pp, mean±std)': f'{soybean_loss_mean:.2f}±{soybean_loss_std:.2f}'
        })

    return pd.DataFrame(summary_data)

def friedman_posthoc_holm(data_matrix):
    """
    Friedman检验 + Wilcoxon配对检验 + Holm校正

    Parameters
    ----------
    data_matrix : array, shape (n_samples, n_models)
        每行是一个样本（路径），每列是一个模型

    Returns
    -------
    dict : {'friedman_stat', 'friedman_p', 'posthoc_results'}
    """
    # Friedman检验
    stat, p = stats.friedmanchisquare(*data_matrix.T)

    # 配对比较
    n_models = data_matrix.shape[1]
    model_pairs = [(i, j) for i in range(n_models) for j in range(i+1, n_models)]

    posthoc = []
    for i, j in model_pairs:
        wilcoxon_stat, wilcoxon_p = stats.wilcoxon(data_matrix[:, i], data_matrix[:, j])
        posthoc.append({
            'pair': (i, j),
            'wilcoxon_p': wilcoxon_p
        })

    # Holm校正
    posthoc_df = pd.DataFrame(posthoc)
    posthoc_df = posthoc_df.sort_values('wilcoxon_p')
    m = len(posthoc_df)
    posthoc_df['holm_threshold'] = 0.05 / (m - np.arange(m))
    posthoc_df['significant'] = posthoc_df['wilcoxon_p'] < posthoc_df['holm_threshold']

    return {
        'friedman_stat': stat,
        'friedman_p': p,
        'posthoc': posthoc_df
    }

def generate_table3_significance_tests():
    """表3：模型显著性检验（分别对玉米和大豆）"""
    # 读取per-fold数据
    fold_df = pd.read_csv('results/summary/cross_site_crop_f1_per_fold.csv')

    results = []

    for crop, f1_col in [('Corn', 'corn_f1'), ('Soybean', 'soybean_f1')]:
        # 构建数据矩阵：行=路径×fold，列=模型
        pivot_data = []

        # 获取所有路径
        paths = fold_df.groupby(['source', 'target']).size().reset_index()[['source', 'target']]

        for _, path_row in paths.iterrows():
            source = path_row['source']
            target = path_row['target']

            path_data = fold_df[
                (fold_df['source'] == source) &
                (fold_df['target'] == target)
            ]

            for fold in range(1, 6):
                fold_data = path_data[path_data['fold'] == fold]

                if len(fold_data) < 3:  # 缺少某个模型
                    continue

                convgru_val = fold_data[fold_data['model'] == 'convgru'][f1_col].values[0]
                unet3d_val = fold_data[fold_data['model'] == 'unet3d'][f1_col].values[0]
                utae_val = fold_data[fold_data['model'] == 'utae'][f1_col].values[0]

                pivot_data.append([convgru_val, unet3d_val, utae_val])

        data_matrix = np.array(pivot_data)

        # 执行检验
        test_result = friedman_posthoc_holm(data_matrix)

        results.append({
            'Crop': crop,
            'Friedman χ²': f"{test_result['friedman_stat']:.4f}",
            'Friedman p': f"{test_result['friedman_p']:.4e}",
            'ConvGRU vs 3D U-Net': 'Sig.' if test_result['posthoc'].iloc[0]['significant'] else 'n.s.',
            'ConvGRU vs U-TAE': 'Sig.' if test_result['posthoc'].iloc[1]['significant'] else 'n.s.',
            '3D U-Net vs U-TAE': 'Sig.' if test_result['posthoc'].iloc[2]['significant'] else 'n.s.'
        })

    return pd.DataFrame(results)

if __name__ == '__main__':
    print("正在生成表1：站内分类性能基准...")
    table1 = generate_table1_within_site_baseline()
    table1.to_csv('tables/table1_within_site_baseline.csv', float_format='%.4f')
    print("已保存：tables/table1_within_site_baseline.csv")
    print(table1)

    print("\n正在生成表2：跨站分类性能汇总...")
    table2 = generate_table2_cross_site_performance()
    table2.to_csv('tables/table2_cross_site_summary.csv', index=False)
    print("已保存：tables/table2_cross_site_summary.csv")
    print(table2)

    print("\n正在生成表3：模型显著性检验...")
    table3 = generate_table3_significance_tests()
    table3.to_csv('tables/table3_significance_tests.csv', index=False)
    print("已保存：tables/table3_significance_tests.csv")
    print(table3)

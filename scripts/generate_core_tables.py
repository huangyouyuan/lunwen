#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the current manuscript table from saved raw-scale F1 summaries."""

from pathlib import Path

import pandas as pd

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

def generate_table2_cross_site_f1_paths():
    """正文表：12条迁移路径 × 三模型玉米/大豆F1，末行给出路径平均。"""
    df = pd.read_csv('results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv',
                     float_precision='round_trip')

    required = {
        'model', 'source', 'target', 'corn_f1_mean', 'soybean_f1_mean'
    }
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f'跨站F1汇总缺少字段：{sorted(missing)}')

    expected_models = {'convgru', 'unet3d', 'utae'}
    expected_sites = set(SITE_MAP)
    if set(df['model']) != expected_models:
        raise ValueError('跨站F1汇总的模型集合不完整')
    if set(df['source']) != expected_sites or set(df['target']) != expected_sites:
        raise ValueError('跨站F1汇总的站点集合不完整')
    if (df['source'] == df['target']).any():
        raise ValueError('跨站F1汇总不应包含源站与目标站相同的记录')
    if df.duplicated(['model', 'source', 'target']).any() or len(df) != 36:
        raise ValueError('跨站F1汇总必须包含36个唯一的模型—路径组合')

    site_ids = ['iw_2023', 'iw2_2023', 'ida_2023', 'il_2023']
    model_ids = ['convgru', 'unet3d', 'utae']
    rows = []
    for source in site_ids:
        for target in site_ids:
            if source == target:
                continue
            row = {'迁移路径': f'{SITE_MAP[source]}→{SITE_MAP[target]}'}
            for model in model_ids:
                selected = df[
                    (df['model'] == model)
                    & (df['source'] == source)
                    & (df['target'] == target)
                ]
                if len(selected) != 1:
                    raise ValueError(f'{model} {source}→{target}记录数不是1')
                item = selected.iloc[0]
                model_name = MODEL_MAP[model]
                row[f'{model_name}玉米F1'] = item['corn_f1_mean']
                row[f'{model_name}大豆F1'] = item['soybean_f1_mean']
            rows.append(row)

    result = pd.DataFrame(rows)
    mean_row = {'迁移路径': '平均'}
    for column in result.columns[1:]:
        mean_row[column] = result[column].mean()
    return pd.concat([result, pd.DataFrame([mean_row])], ignore_index=True)


def write_table2_cross_site_f1_latex_rows(table):
    """把已验证的正文表写成LaTeX表体，避免正文重复维护数字。"""
    lines = []
    for _, row in table.iterrows():
        path = str(row['迁移路径'])
        if path == '平均':
            path_tex = '平均'
        else:
            source, target = path.split('→')
            path_tex = f'{source}$\\rightarrow${target}'
        values = ' & '.join(f'{float(value):.2f}' for value in row.iloc[1:])
        lines.append(f'{path_tex} & {values} \\\\')
        if path == 'D→C':
            lines.append('\\midrule')
    lines.append('\\bottomrule')
    output = Path('tables/table2_cross_site_f1_12paths_rows.tex')
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == "__main__":
    table = generate_table2_cross_site_f1_paths()
    table.to_csv(
        "tables/table2_cross_site_f1_12paths.csv", index=False,
        float_format="%.2f", encoding="utf-8-sig",
    )
    write_table2_cross_site_f1_latex_rows(table)
    print("Current cross-site F1 table saved.")

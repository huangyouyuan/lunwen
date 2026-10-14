#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate the current manuscript table from saved raw-scale F1 summaries."""

from pathlib import Path

import pandas as pd
from f1_display import f1_number

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


def table2_display(table):
    """Mean F1 only, in percent; per-run results and SDs stay in the summaries."""
    rows = []
    for _, row in table.iterrows():
        formatted = {'迁移路径': row['迁移路径']}
        for name in MODEL_MAP.values():
            for label in ['玉米', '大豆']:
                formatted[f'{name}{label}F1（%）'] = f1_number(row[f'{name}{label}F1'])
        rows.append(formatted)
    return pd.DataFrame(rows)


def write_table2_cross_site_f1_latex_rows(table):
    """把已验证的正文表写成LaTeX表体，避免正文重复维护数字。"""
    lines = []
    for _, row in table.iterrows():
        path = str(row['迁移路径'])
        if path == '平均':
            path_tex = '平均'
        else:
            source, target = path.split('→')
            path_tex = f'{source}→{target}'
        values = ' & '.join(str(value) for value in row.iloc[1:])
        lines.append(f'{path_tex} & {values} \\\\')
        if path == 'D→C':
            lines.append('\\midrule')
    lines.append('\\bottomrule')
    output = Path('tables/table2_cross_site_f1_12paths_rows.tex')
    output.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def f1_text_values():
    """Only reproduce comparisons already cited in 3.1/3.2 from saved results.

    Values stay raw until TeX formatting. No scientific result is written.
    """
    base = Path('results/summary/f1_raw_scale')
    read = lambda name: pd.read_csv(base / name, float_precision='round_trip')
    within = read('within_site_crop_f1.csv')
    cross = read('cross_site_crop_f1_summary.csv')
    delta = read('crop_f1_difference_36paths.csv')
    runs = read('cross_site_crop_f1_per_fold.csv')
    values = {}
    for crop, tag in [('corn', 'Corn'), ('soybean', 'Soy')]:
        values[f'FWithin{tag}Min'] = within[f'{crop}_f1'].min()
        values[f'FWithin{tag}Max'] = within[f'{crop}_f1'].max()
        values[f'FCross{tag}Min'] = cross[f'{crop}_f1_mean'].min()
        values[f'FCross{tag}Max'] = cross[f'{crop}_f1_mean'].max()
    site_diffs = {}
    for site in ['ida_2023', 'il_2023']:
        w = within[within.target == site].set_index('model')
        site_diffs[site] = [w.loc[m, f'{c}_f1'] - w.loc['convgru', f'{c}_f1']
                            for m in ['utae', 'unet3d'] for c in ['corn', 'soybean']]
    for site, tag in [('ida_2023', 'C'), ('il_2023', 'D')]:
        values[f'FModelGap{tag}Min'] = min(site_diffs[site])
        values[f'FModelGap{tag}Max'] = max(site_diffs[site])
    w = within[within.target == 'ida_2023'].set_index('model')
    values['FCUtaeUnetCorn'] = w.loc['utae', 'corn_f1'] - w.loc['unet3d', 'corn_f1']
    values['FCUtaeUnetSoy'] = w.loc['utae', 'soybean_f1'] - w.loc['unet3d', 'soybean_f1']
    means = cross.groupby('model')[['corn_f1_mean', 'soybean_f1_mean']].mean()
    gaps = delta.groupby('model')[['corn_f1_difference', 'soybean_f1_difference']].mean()
    for crop, tag in [('corn', 'Corn'), ('soybean', 'Soy')]:
        values[f'FConvCross{tag}'] = means.loc['convgru', f'{crop}_f1_mean']
        values[f'FConvGap{tag}'] = gaps.loc['convgru', f'{crop}_f1_difference']
    higher_means = means.loc[['unet3d', 'utae']].to_numpy().ravel()
    higher_gaps = gaps.loc[['unet3d', 'utae']].to_numpy().ravel()
    model_gaps = (means.loc[['unet3d', 'utae']] - means.loc['convgru']).to_numpy().ravel()
    for tag, arr in [('OtherCross', higher_means), ('OtherGap', higher_gaps), ('CrossModelGap', model_gaps)]:
        values[f'F{tag}Min'], values[f'F{tag}Max'] = min(arr), max(arr)
    for model, tag in [('convgru', 'Conv'), ('unet3d', 'Unet')]:
        for source, target, path in [('iw2_2023', 'il_2023', 'BD'), ('il_2023', 'iw2_2023', 'DB'), ('ida_2023', 'il_2023', 'CD')]:
            row = delta[(delta.model == model) & (delta.source == source) & (delta.target == target)].iloc[0]
            values[f'F{tag}Soy{path}'] = row.soybean_f1_difference
    ref = within[(within.model == 'convgru') & (within.target == 'il_2023')].soybean_f1.iloc[0]
    for source, tag in [('ida_2023', 'CD'), ('iw2_2023', 'BD')]:
        x = ref - runs[(runs.model == 'convgru') & (runs.source == source) & (runs.target == 'il_2023')].soybean_f1
        values[f'FConvSoy{tag}RunMin'], values[f'FConvSoy{tag}RunMax'] = x.min(), x.max()
    return values


def write_f1_text_values():
    lines = ['% Generated from full-precision results/summary/f1_raw_scale; display only.',
             '% F1 numbers: percent; differences: percentage points. Units are in the prose.']
    for name, raw in f1_text_values().items():
        lines.append(f'\\newcommand{{\\{name}}}{{{f1_number(raw)}}}')
    Path('tables/f1_text_values.tex').write_text('\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == "__main__":
    table = generate_table2_cross_site_f1_paths()
    display = table2_display(table)
    display.to_csv(
        "tables/table2_cross_site_f1_12paths.csv", index=False,
        encoding="utf-8-sig",
    )
    write_table2_cross_site_f1_latex_rows(display)
    write_f1_text_values()
    print("F1 presentation table (percent, mean only) and text values saved; raw summaries unchanged.")

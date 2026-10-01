#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild full-precision, raw-scale F1 products from repository integer CMs.

Legacy summaries are neither inputs nor outputs. CSV outputs preserve binary64
precision (%.17g); downstream readers should use float_precision='round_trip'.
Only presentation layers round to two decimals. No training or inference runs.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

MODELS = ('convgru', 'unet3d', 'utae')
SITES = ('iw_2023', 'iw2_2023', 'ida_2023', 'il_2023')
CLASS_ORDER = ('corn', 'other', 'soybean')
CM_COLUMNS = [f'cm_{i}{j}' for i in range(3) for j in range(3)]
METRICS = ['corn_f1', 'soybean_f1', 'other_f1', 'oa']
FULL_SITE_PIXELS = 6_553_600
PROCESSED = 'results/processed/f1_raw_scale'
SUMMARY = 'results/summary/f1_raw_scale'
WITHIN_RAW = 'results/raw/within_site_confusion_matrices.csv'
CROSS_RAW = 'results/raw/cross_site_confusion_matrices.csv'
MANIFEST = f'{SUMMARY}/run_manifest.json'
TABLE_PATHS = (
    f'{PROCESSED}/within_site_metrics.csv',
    f'{PROCESSED}/cross_site_metrics.csv',
    f'{SUMMARY}/within_site_crop_f1.csv',
    f'{SUMMARY}/within_site_crop_f1_fold_stats.csv',
    f'{SUMMARY}/cross_site_crop_f1_per_fold.csv',
    f'{SUMMARY}/cross_site_crop_f1_summary.csv',
    f'{SUMMARY}/crop_f1_difference_36paths.csv',
)


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _validate_frame(frame, metadata, expected_rows, name):
    _require(frame.columns.is_unique, f'{name}: duplicate column names')
    missing = set(metadata + CM_COLUMNS).difference(frame.columns)
    _require(not missing, f'{name}: missing columns {sorted(missing)}')
    _require(len(frame) == expected_rows, f'{name}: expected {expected_rows} rows')
    result = frame.loc[:, metadata + CM_COLUMNS].copy()
    try:
        counts = result[CM_COLUMNS].apply(pd.to_numeric, errors='raise').to_numpy(dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name}: CM values must be numeric integers') from exc
    _require(np.isfinite(counts).all(), f'{name}: nonfinite CM values')
    _require(((counts >= 0) & (counts <= FULL_SITE_PIXELS)).all(),
             f'{name}: CM values outside allowed pixel-count range')
    _require((counts == np.floor(counts)).all(), f'{name}: noninteger CM values')
    result[CM_COLUMNS] = counts.astype(np.int64)
    return result


def _validate_folds(frame, keys, name):
    try:
        folds = pd.to_numeric(frame['fold'], errors='raise').to_numpy(dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name}: invalid fold IDs') from exc
    _require(np.isfinite(folds).all() and np.isin(folds, [1, 2, 3, 4, 5]).all(),
             f'{name}: fold IDs must be integers 1..5')
    frame['fold'] = folds.astype(np.int64)
    _require(not frame.duplicated(keys + ['fold']).any(), f'{name}: duplicate fold keys')
    for key, group in frame.groupby(keys, dropna=False):
        _require(len(group) == 5 and set(group['fold']) == {1, 2, 3, 4, 5},
                 f'{name}: {key} must have exactly five distinct folds')


def _supports(frame):
    matrices = frame[CM_COLUMNS].to_numpy(dtype=np.int64).reshape(-1, 3, 3)
    return matrices.sum(axis=2)


def metrics_from_cm(cm):
    """Metrics for validated 3x3 integer CMs, in corn/other/soybean order.

    An absent class with no predictions has F1=0, matching the legacy full-site
    scripts. OA requires a positive total; callers validate complete-site counts.
    """
    matrices = np.asarray(cm, dtype=np.int64).reshape(-1, 3, 3)
    tp = np.diagonal(matrices, axis1=1, axis2=2)
    denominator = matrices.sum(axis=2) + matrices.sum(axis=1)
    f1 = np.divide(2.0 * tp, denominator, out=np.zeros_like(tp, dtype=float), where=denominator > 0)
    totals = matrices.sum(axis=(1, 2))
    _require((totals > 0).all(), 'CM total must be positive')
    return pd.DataFrame({
        'corn_f1': f1[:, 0], 'soybean_f1': f1[:, 2],
        'other_f1': f1[:, 1], 'oa': tp.sum(axis=1) / totals,
    })


def _with_metrics(frame):
    frame = frame.reset_index(drop=True)
    return pd.concat([frame, metrics_from_cm(frame[CM_COLUMNS].to_numpy())], axis=1)


def _fold_stats(frame, keys, metrics):
    grouped = frame.groupby(keys, sort=True)[metrics]
    means, stds = grouped.mean(), grouped.std(ddof=1)
    result = pd.DataFrame(index=means.index)
    for metric in metrics:
        result[f'{metric}_mean'] = means[metric]
        result[f'{metric}_std'] = stds[metric]
    return result.reset_index()


def build_tables(within_raw, cross_raw):
    """Validate raw CM DataFrames and return {relative_csv_path: DataFrame}.

    This function is pure with respect to files and does not mutate its inputs.
    A complete 12-experiment / 36-path / 180-prediction dataset is required.
    """
    within_keys = ['model', 'target']
    cross_keys = ['model', 'source', 'target']
    within = _validate_frame(within_raw, within_keys + ['result_type', 'fold'], 72, 'within')
    cross = _validate_frame(cross_raw, cross_keys + ['fold'], 180, 'cross')
    expected_within = {(model, site) for model in MODELS for site in SITES}
    expected_cross = {(model, source, target) for model in MODELS
                      for source in SITES for target in SITES if source != target}
    _require(set(within[within_keys].itertuples(index=False, name=None)) == expected_within,
             'within: model/target key set must equal the 12 expected experiments')
    _require(set(cross[cross_keys].itertuples(index=False, name=None)) == expected_cross,
             'cross: model/source/target key set must equal the 36 expected combinations')
    _require(set(within['result_type']) == {'fold', 'oof_pooled'}, 'within: invalid result types')
    folds = within[within['result_type'] == 'fold'].copy()
    pooled = within[within['result_type'] == 'oof_pooled'].copy()
    _require(len(folds) == 60 and len(pooled) == 12, 'within: expected 60 fold and 12 pooled rows')
    _require(set(pooled[within_keys].itertuples(index=False, name=None)) == expected_within,
             'within: pooled key set is incomplete')
    _require(not pooled.duplicated(within_keys).any(), 'within: duplicate pooled keys')
    _require(pooled['fold'].isna().all(), 'within: pooled fold IDs must be missing')
    _validate_folds(folds, within_keys, 'within')
    _validate_folds(cross, cross_keys, 'cross')

    fold_sum = folds.groupby(within_keys)[CM_COLUMNS].sum().sort_index()
    pooled_cm = pooled.set_index(within_keys)[CM_COLUMNS].sort_index()
    _require(fold_sum.equals(pooled_cm), 'within: pooled CM must equal elementwise fold sum')
    _require((pooled[CM_COLUMNS].sum(axis=1) == FULL_SITE_PIXELS).all(),
             'within: each pooled CM must contain 6553600 pixels')
    _require((folds[CM_COLUMNS].sum(axis=1) == FULL_SITE_PIXELS // 5).all(),
             'within: each test-fold CM must contain 1310720 pixels')
    _require((cross[CM_COLUMNS].sum(axis=1) == FULL_SITE_PIXELS).all(),
             'cross: each full-target CM must contain 6553600 pixels')

    target_supports = {}
    for row, support in zip(pooled.itertuples(index=False), _supports(pooled)):
        support = tuple(int(value) for value in support)
        if row.target in target_supports:
            _require(target_supports[row.target] == support, 'within: target row supports differ across models')
        target_supports[row.target] = support
    fold_supports = {}
    for row, support in zip(folds.itertuples(index=False), _supports(folds)):
        key = (row.target, row.fold)
        support = tuple(int(value) for value in support)
        if key in fold_supports:
            _require(fold_supports[key] == support, 'within: test-fold row supports differ across models')
        fold_supports[key] = support
    for row, support in zip(cross.itertuples(index=False), _supports(cross)):
        _require(tuple(int(value) for value in support) == target_supports[row.target],
                 f'cross: row supports do not match target {row.target}')

    within = pd.concat([folds, pooled], ignore_index=True).sort_values(within_keys + ['result_type', 'fold'])
    cross = cross.sort_values(cross_keys + ['fold'])
    within_metrics, cross_metrics = _with_metrics(within), _with_metrics(cross)
    pooled_metrics = within_metrics[within_metrics['result_type'] == 'oof_pooled']
    within_summary = pooled_metrics[within_keys + METRICS].copy()
    within_summary['valid_pixels'] = pooled_metrics[CM_COLUMNS].sum(axis=1).astype(np.int64)
    within_summary = within_summary.reset_index(drop=True)
    within_stats = _fold_stats(within_metrics[within_metrics['result_type'] == 'fold'], within_keys,
                               ['corn_f1', 'soybean_f1', 'oa'])
    cross_per_fold = cross_metrics[cross_keys + ['fold', 'corn_f1', 'soybean_f1', 'other_f1']].copy()
    cross_summary = _fold_stats(cross_metrics, cross_keys, ['corn_f1', 'soybean_f1'])
    difference = cross_summary.rename(columns={column: f'cross_{column}' for column in cross_summary
                                               if column not in cross_keys})
    baseline = within_summary[within_keys + ['corn_f1', 'soybean_f1']].rename(
        columns={'corn_f1': 'within_corn_f1', 'soybean_f1': 'within_soybean_f1'})
    difference = difference.merge(baseline, on=within_keys, how='left', validate='many_to_one')
    columns = list(cross_keys)
    for crop in ('corn', 'soybean'):
        difference[f'{crop}_f1_difference'] = difference[f'within_{crop}_f1'] - difference[f'cross_{crop}_f1_mean']
        columns += [f'within_{crop}_f1', f'cross_{crop}_f1_mean', f'cross_{crop}_f1_std', f'{crop}_f1_difference']
    difference = difference[columns]
    products = [within_metrics, cross_metrics, within_summary, within_stats,
                cross_per_fold, cross_summary, difference]
    return dict(zip(TABLE_PATHS, products))


def _file_record(path, root):
    path = Path(path).resolve()
    try:
        name = path.relative_to(root).as_posix()
    except ValueError:
        name = path.as_posix()
    return {'path': name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'bytes': path.stat().st_size}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1],
                        help='Repository root; inputs are only its two results/raw CM CSVs')
    args = parser.parse_args(argv)
    root = args.root.resolve()
    destinations = [root / relative for relative in (*TABLE_PATHS, MANIFEST)]
    inputs = [_file_record(root / relative, root) for relative in (WITHIN_RAW, CROSS_RAW)]
    script = _file_record(Path(__file__), root)
    existing = [path for path in destinations if path.exists()]
    if len(existing) == len(destinations):
        manifest = json.loads((root / MANIFEST).read_text(encoding='utf-8'))
        unchanged = manifest.get('inputs') == inputs and manifest.get('script') == script
        records = manifest.get('outputs', [])
        unchanged = unchanged and {row['path'] for row in records} == set(TABLE_PATHS)
        for row in records:
            unchanged = unchanged and _file_record(root / row['path'], root) == {
                key: row[key] for key in ('path', 'sha256', 'bytes')}
        if unchanged:
            print('Verified: existing raw-scale products match inputs, script and output hashes; no files written.')
            return
    if existing:
        raise FileExistsError('Refusing to overwrite changed or incomplete products; archive verified history first: '
                              + ', '.join(str(path) for path in existing))
    within = pd.read_csv(root / WITHIN_RAW, float_precision='round_trip')
    cross = pd.read_csv(root / CROSS_RAW, float_precision='round_trip')
    tables = build_tables(within, cross)
    if inputs != [_file_record(root / relative, root) for relative in (WITHIN_RAW, CROSS_RAW)]:
        raise RuntimeError('Raw inputs changed during calculation; no products written')
    outputs = []
    for relative, table in tables.items():
        destination = root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        # Exclusive creation preserves historical outputs, including races after preflight.
        with destination.open('x', encoding='utf-8', newline='') as handle:
            table.to_csv(handle, index=False, float_format='%.17g', lineterminator='\n')
        outputs.append({**_file_record(destination, root), 'rows': len(table)})
    manifest = {
        'data_status': 'derived', 'scale': 'raw_0_1',
        'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'class_order': list(CLASS_ORDER), 'std_ddof': 1,
        'within_baseline': 'F1 calculated from sum of five test-fold CMs',
        'cross_aggregation': 'arithmetic mean and sample standard deviation of five full-target F1 values',
        'difference_formula': 'same-model target-site pooled F1 minus five-prediction cross-site mean F1',
        'difference_range': [-1, 1], 'scaling_factor': 1,
        'float_format': '%.17g', 'csv_reader_float_precision': 'round_trip',
        'presentation': 'raw-scale F1, F1 standard deviations and differences displayed to 2 decimals; stored values are not rounded for display',
        'inputs': inputs, 'script': script, 'outputs': outputs,
    }
    with (root / MANIFEST).open('x', encoding='utf-8', newline='') as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write('\n')
    print(f'Wrote {len(tables)} validated derived CSVs and {MANIFEST}; legacy files unchanged.')


if __name__ == '__main__':
    main()

"""Reference-only preparation for common numerical grades; never chooses grades."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from explore_sec33_reference_patch_types import sha

ROOT = Path(__file__).resolve().parents[1]
NAME = 'sec33_indicator_grading_preparation'
PROC = ROOT / 'results/processed' / NAME
SUM = ROOT / 'results/summary' / NAME
BASE = ROOT / 'results/processed/sec33_reference_patch_types'
OLD = ROOT / 'results/summary/sec33_reference_patch_types'
K4 = ROOT / 'results/summary/sec33_k4_sensitivity'
SITES = {'iw_2023': 'A', 'iw2_2023': 'B', 'ida_2023': 'C', 'il_2023': 'D'}
CROPS = ['corn', 'soybean']
METRICS = ['AREA', 'SHAPE', 'ENN']
UNITS = {'AREA': 'ha', 'SHAPE': 'dimensionless', 'ENN': 'm',
         'GYRATE': 'm', 'CONTIG': 'dimensionless'}
QUANTILES = {'q05': .05, 'q10': .10, 'q25': .25, 'median': .5,
             'q75': .75, 'q90': .90, 'q95': .95, 'q99': .99}
INPUTS = {}
CHECKS = []


def read(path):
    path = Path(path)
    INPUTS[path.relative_to(ROOT).as_posix()] = sha(path)
    return pd.read_csv(path, float_precision='round_trip')


def check(name, ok, detail=''):
    CHECKS.append(dict(check=name, status='Verified' if ok else 'Not verified', detail=str(detail)))
    if not ok:
        raise ValueError(name + ': ' + str(detail))


def write(frame, name, processed=False):
    directory = PROC if processed else SUM
    path = directory / (name + '.csv')
    if path.exists():
        raise FileExistsError(path)
    frame.to_csv(path, index=False, float_format='%.17g', encoding='utf-8')


def valid_metric(frame, metric):
    values = frame[metric].to_numpy(float)
    return np.isfinite(values) & (values > 0)


def value_frequency(frame, metric):
    """Group exact saved values, without rounding or splitting tied observations."""
    valid = frame.loc[valid_metric(frame, metric)].copy()
    valid['singleton_count'] = valid.reference_pixels.eq(1).astype('int64')
    valid['singleton_pixels'] = np.where(valid.reference_pixels.eq(1), valid.reference_pixels, 0)
    valid['no_interior_count'] = valid.no_interior.astype('int64')
    valid['no_interior_pixels'] = np.where(valid.no_interior, valid.reference_pixels, 0)
    valid['edge_count'] = valid.touches_outer_edge.astype('int64')
    valid['edge_pixels'] = np.where(valid.touches_outer_edge, valid.reference_pixels, 0)
    freq = valid.groupby(metric, sort=True).agg(
        n_patches=('PID', 'size'), pixels=('reference_pixels', 'sum'),
        singleton_count=('singleton_count', 'sum'), singleton_pixels=('singleton_pixels', 'sum'),
        no_interior_count=('no_interior_count', 'sum'), no_interior_pixels=('no_interior_pixels', 'sum'),
        edge_count=('edge_count', 'sum'), edge_pixels=('edge_pixels', 'sum'),
        boundary_pixels=('boundary_pixels', 'sum'), interior_pixels=('interior_pixels', 'sum')
    ).reset_index().rename(columns={metric: 'value'})
    freq['cumulative_n_patches'] = freq.n_patches.cumsum()
    freq['cumulative_pixels'] = freq.pixels.cumsum()
    n = int(freq.n_patches.sum())
    pixels = int(freq.pixels.sum())
    freq['patch_share'] = freq.n_patches / n if n else np.nan
    freq['area_share'] = freq.pixels / pixels if pixels else np.nan
    freq['patch_cdf'] = freq.cumulative_n_patches / n if n else np.nan
    freq['area_cdf'] = freq.cumulative_pixels / pixels if pixels else np.nan
    freq['patch_rank'] = freq.n_patches.rank(ascending=False, method='first').astype('int64')
    freq['area_rank'] = freq.pixels.rank(ascending=False, method='first').astype('int64')
    return freq


def inverse_ecdf(values, weights, probabilities):
    """Smallest observed value whose cumulative positive integer weight reaches q."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights)
    probabilities = np.asarray(probabilities, dtype=float)
    if values.ndim != 1 or weights.shape != values.shape:
        raise ValueError('value/weight shape mismatch')
    if not np.isfinite(probabilities).all() or ((probabilities < 0) | (probabilities > 1)).any():
        raise ValueError('invalid quantile probabilities')
    if not np.issubdtype(weights.dtype, np.integer) or (weights <= 0).any():
        raise ValueError('weights must be positive integer reference counts')
    if not np.isfinite(values).all():
        raise ValueError('quantile inputs must be finite')
    if len(values) == 0:
        return np.full(probabilities.shape, np.nan)
    order = np.argsort(values, kind='stable')
    cumulative = weights[order].cumsum(dtype=np.int64)
    indices = np.searchsorted(cumulative, probabilities * cumulative[-1], side='left')
    return values[order][np.minimum(indices, len(values) - 1)]


def cdf_gap(first, second, column):
    """Descriptive maximum ECDF gap on the union of observed values; no P-value."""
    if first.empty or second.empty:
        return np.nan
    union = np.union1d(first.value, second.value)
    a = first.set_index('value')[column].reindex(union).ffill().fillna(0).to_numpy()
    b = second.set_index('value')[column].reindex(union).ffill().fillna(0).to_numpy()
    return float(np.max(np.abs(a - b)))


def domains(frame):
    yield 'all', 'all', 'all', frame
    for crop in CROPS:
        yield 'crop', 'all', crop, frame.loc[frame.crop.eq(crop)]
    for target in SITES:
        for crop in CROPS:
            yield 'site_crop', target, crop, frame.loc[frame.target.eq(target) & frame.crop.eq(crop)]


def counts_inventory(features):
    index = read(BASE / 'prediction_count_index.csv')
    keys = ['kind', 'model', 'source', 'target', 'fold']
    check('count index unique', not index.duplicated(keys).any())
    expected = {('within', m, t, t, 0) for m in ['convgru', 'unet3d', 'utae'] for t in SITES}
    expected |= {('cross', m, s, t, k) for m in ['convgru', 'unet3d', 'utae']
                 for s in SITES for t in SITES if s != t for k in range(1, 6)}
    check('192 index identities', set(index[keys].itertuples(index=False, name=None)) == expected)
    check('192 indexed count files present', all((BASE / file).is_file() for file in index.file))
    # Only one saved OOF count per site is needed for reference support and array-schema checks.
    rows = []
    for target in SITES:
        selected = index.loc[index.kind.eq('within') & index.model.eq('convgru') & index.target.eq(target)].iloc[0]
        path = BASE / selected.file
        INPUTS[path.relative_to(ROOT).as_posix()] = sha(path)
        check('sample count hash ' + target, INPUTS[path.relative_to(ROOT).as_posix()] == selected.sha256)
        f = features.loc[features.target.eq(target)]
        with np.load(path) as archive:
            counts = archive['patch_band_prediction_counts']
            check('PID axis ' + target, np.array_equal(archive['PID'], np.arange(counts.shape[0])))
            check('integer nonnegative counts ' + target,
                  np.issubdtype(counts.dtype, np.integer) and (counts >= 0).all())
            check('complete PID coverage ' + target,
                  set(f.PID) == set(range(1, counts.shape[0])) and counts[0].sum() == 0)
            check('saved count dimensions ' + target, counts.shape[1:] == (7, 3))
            by_pid = counts.sum(2, dtype=np.int64)
            linked = by_pid[f.PID.to_numpy(int)]
            check('sample reference pixels ' + target, np.array_equal(linked.sum(1), f.reference_pixels))
            check('sample near/interior/far support ' + target,
                  np.array_equal(linked[:, 0], f.boundary_pixels)
                  and np.array_equal(linked[:, 1:].sum(1), f.interior_pixels)
                  and np.array_equal(linked[:, 6], f.far_interior_pixels))
            rows.append(dict(target=target, site=SITES[target], sample_file=path.relative_to(ROOT).as_posix(),
                             sampled_kind='within', sampled_model='convgru', sampled_fold=0,
                             array_keys=';'.join(archive.files), array_shape=str(counts.shape),
                             all_class_patches=len(f), all_class_pixels=int(linked.sum()),
                             current_check='Verified', remaining_count_arrays='historical_only_not_reopened'))
    return pd.DataFrame(rows)


def prepare():
    if SUM.exists() or PROC.exists():
        raise FileExistsError('Use a new independent directory; existing preparation outputs are preserved.')
    features = read(BASE / 'reference_patch_features.csv')
    old_dist = read(OLD / 'feature_distributions.csv')
    k4_support = read(K4 / 'type_reference_support.csv')
    k2_support = read(OLD / 'type_reference_support.csv')
    grid = read(OLD / 'grid_inventory.csv')
    correlations = read(OLD / 'feature_correlations.csv')
    check('unique full reference identity', not features.duplicated(['target', 'PID']).any()
          and features.patch_uid.is_unique)
    check('sites and classes', set(features.target) == set(SITES) and set(features.crop) == {'corn', 'other', 'soybean'})
    check('positive integer reference support', np.issubdtype(features.reference_pixels.dtype, np.integer)
          and features.reference_pixels.gt(0).all())
    check('AREA matches saved pixel support', np.allclose(features.AREA, features.reference_pixels * .09, rtol=0, atol=1e-10))
    check('reference feature status', features.feature_status.eq('valid').all() and features.missing_reason.isna().all())
    check('near plus interior and empty interior flag',
          features.boundary_pixels.add(features.interior_pixels).eq(features.reference_pixels).all()
          and features.no_interior.eq(features.interior_pixels.eq(0)).all())
    for row in grid.itertuples():
        f = features.loc[features.target.eq(row.target)]
        check('grid support ' + row.target, len(f) == row.patches
              and int(f.reference_pixels.sum()) == row.rows * row.cols
              and int(f.crop.isin(CROPS).sum()) == row.crop_patches)
    crops = features.loc[features.crop.isin(CROPS)]
    check('crop identity totals', len(crops) == 149234 and len(features) == 187372)
    old_lookup = old_dist.set_index(['domain', 'metric'])
    check('old distributions unique', old_lookup.index.is_unique)
    PROC.mkdir(parents=True)
    SUM.mkdir(parents=True)
    write(counts_inventory(features), 'count_reuse_schema')

    freq_frames, reading, supporting, concentrations = [], [], [], []
    freq_lookup = {}
    for domain, target, crop, f in domains(crops):
        shared = dict(domain=domain, target=target, site=SITES.get(target, 'all'), crop=crop)
        prior = k4_support.loc[k4_support.domain.eq(domain) & k4_support.target.eq(target) & k4_support.crop.eq(crop)]
        check('reused K4 support keys ' + str((domain, target, crop)),
              len(prior) == 4 and prior.spatial_type.nunique() == 4)
        total = {col: int(prior[col].sum()) for col in [
            'n_patches', 'pixels', 'singleton_count', 'boundary_pixels', 'interior_pixels',
            'far_interior_pixels', 'no_interior_patches', 'edge_patches', 'edge_pixels']}
        actual = dict(n_patches=len(f), pixels=int(f.reference_pixels.sum()),
                      singleton_count=int(f.reference_pixels.eq(1).sum()),
                      boundary_pixels=int(f.boundary_pixels.sum()), interior_pixels=int(f.interior_pixels.sum()),
                      far_interior_pixels=int(f.far_interior_pixels.sum()), no_interior_patches=int(f.no_interior.sum()),
                      edge_patches=int(f.touches_outer_edge.sum()),
                      edge_pixels=int(f.loc[f.touches_outer_edge, 'reference_pixels'].sum()))
        check('reused K4 support closure ' + str((domain, target, crop)), total == actual)
        no_interior_pixels = int(f.loc[f.no_interior, 'reference_pixels'].sum())
        supporting.append(dict(**shared, **total, area_ha=total['pixels'] * .09,
                               singleton_pixels=total['singleton_count'],
                               singleton_patch_share=total['singleton_count'] / total['n_patches'],
                               singleton_area_share=total['singleton_count'] / total['pixels'],
                               no_interior_patch_share=total['no_interior_patches'] / total['n_patches'],
                               no_interior_pixels=no_interior_pixels, no_interior_area_share=no_interior_pixels / total['pixels'],
                               edge_patch_share=total['edge_patches'] / total['n_patches'],
                               edge_area_share=total['edge_pixels'] / total['pixels'],
                               boundary_area_share=total['boundary_pixels'] / total['pixels'],
                               reused_counts_source=(K4 / 'type_reference_support.csv').relative_to(ROOT).as_posix(),
                               new_fields='no_interior_pixels;no_interior_area_share;explicit_pooled_shares'))
        for metric in METRICS:
            freq = value_frequency(f, metric)
            freq_lookup[(domain, target, crop, metric)] = freq
            valid = f.loc[valid_metric(f, metric)]
            nv, pv = len(valid), int(valid.reference_pixels.sum())
            check('frequency integer closure ' + str((domain, target, crop, metric)),
                  int(freq.n_patches.sum()) == nv and int(freq.pixels.sum()) == pv)
            check('frequency cumulative closure ' + str((domain, target, crop, metric)),
                  (freq.empty or (freq.patch_cdf.iloc[-1] == 1 and freq.area_cdf.iloc[-1] == 1))
                  and freq.value.is_unique and freq.value.is_monotonic_increasing)
            metadata = dict(**shared, metric=metric, unit=UNITS[metric], n_total=len(f), pixels_total=total['pixels'],
                            n_valid=nv, pixels_valid=pv, n_missing_or_invalid=len(f) - nv,
                            pixels_missing_or_invalid=total['pixels'] - pv, n_unique=len(freq))
            freq_frames.append(freq.assign(**metadata))
            top = freq.loc[freq.patch_rank.le(5) | freq.area_rank.le(5)].copy()
            concentrations.append(top.assign(**metadata))
            old_domain = 'all' if domain == 'all' else target + '/' + crop
            old_row = old_lookup.loc[(old_domain, metric)] if domain != 'crop' else None
            count_q = valid[metric].quantile(list(QUANTILES.values()), interpolation='linear').to_numpy()
            if old_row is not None:
                check('old quantiles rechecked ' + old_domain + '/' + metric,
                      old_row['n'] == len(f) and old_row.n_na == int(f[metric].isna().sum())
                      and np.allclose([old_row.minimum, old_row.q25, old_row['median'], old_row.q75, old_row.q95, old_row.maximum],
                                      valid[metric].quantile([0, .25, .5, .75, .95, 1]), rtol=0, atol=1e-12))
            for weighting in ['patch_equal', 'reference_pixel_area']:
                q = dict(zip(QUANTILES, count_q if weighting == 'patch_equal' else
                             inverse_ecdf(freq.value, freq.pixels.to_numpy(), list(QUANTILES.values()))))
                minimum = float(valid[metric].min()) if nv else np.nan
                maximum = float(valid[metric].max()) if nv else np.nan
                reused = weighting == 'patch_equal' and old_row is not None
                if reused:
                    minimum, maximum = old_row.minimum, old_row.maximum
                    for field in ['q25', 'median', 'q75', 'q95']:
                        q[field] = old_row[field]
                reading.append(dict(**metadata, weighting=weighting, minimum=minimum, maximum=maximum, **q,
                                    algorithm='linear_order_statistics' if weighting == 'patch_equal' else 'inverse_weighted_ecdf',
                                    reused_fields='minimum;q25;median;q75;q95;maximum' if reused else '',
                                    reused_source=(OLD / 'feature_distributions.csv').relative_to(ROOT).as_posix() if reused else '',
                                    new_fields='q05;q10;q90;q99;frequency_diagnostics' if reused else 'all_distribution_fields',
                                    patch_area_cdf_gap=cdf_gap(freq, freq.assign(area_cdf=freq.patch_cdf), 'area_cdf'),
                                    current_status='Verified' if nv else 'Not verified'))
    frequencies = pd.concat(freq_frames, ignore_index=True)
    distribution = pd.DataFrame(reading)
    write(frequencies, 'value_frequency_cumulative', processed=True)
    write(pd.concat(concentrations, ignore_index=True), 'concentrated_values')
    write(distribution, 'indicator_distribution_reading')
    write(pd.DataFrame(supporting), 'reference_support_reading')

    pairs = []
    strata = [(t, c) for t in SITES for c in CROPS]
    for metric in METRICS:
        for (ta, ca), (tb, cb) in combinations(strata, 2):
            a = freq_lookup[('site_crop', ta, ca, metric)]
            b = freq_lookup[('site_crop', tb, cb, metric)]
            low, high = max(a.value.min(), b.value.min()), min(a.value.max(), b.value.max())
            ra = distribution.query('domain == "site_crop" and weighting == "reference_pixel_area"')
            aa = ra.loc[ra.target.eq(ta) & ra.crop.eq(ca) & ra.metric.eq(metric)].iloc[0]
            bb = ra.loc[ra.target.eq(tb) & ra.crop.eq(cb) & ra.metric.eq(metric)].iloc[0]
            overlap_a = a.loc[a.value.between(low, high)]
            overlap_b = b.loc[b.value.between(low, high)]
            pairs.append(dict(metric=metric, unit=UNITS[metric], target_a=ta, site_a=SITES[ta], crop_a=ca,
                              target_b=tb, site_b=SITES[tb], crop_b=cb,
                              comparison='within_site_crops' if ta == tb else 'within_crop_sites' if ca == cb else 'other_strata',
                              range_overlap_low=low, range_overlap_high=high, has_range_overlap=low <= high,
                              range_patch_coverage_a=overlap_a.n_patches.sum() / a.n_patches.sum(),
                              range_patch_coverage_b=overlap_b.n_patches.sum() / b.n_patches.sum(),
                              range_area_coverage_a=overlap_a.pixels.sum() / a.pixels.sum(),
                              range_area_coverage_b=overlap_b.pixels.sum() / b.pixels.sum(),
                              max_patch_cdf_gap=cdf_gap(a, b, 'patch_cdf'), max_area_cdf_gap=cdf_gap(a, b, 'area_cdf'),
                              area_weighted_q05_q95_overlap_low=max(aa.q05, bb.q05),
                              area_weighted_q05_q95_overlap_high=min(aa.q95, bb.q95)))
    write(pd.DataFrame(pairs), 'stratum_distribution_overlap')

    # Common reference-only diagnostic intervals are ECDF coverage slices, not proposed grades.
    intervals = []
    for metric in METRICS:
        pooled = distribution.loc[distribution.domain.eq('all') & distribution.metric.eq(metric)
                                  & distribution.weighting.eq('reference_pixel_area')].iloc[0]
        uppers = sorted(set(pooled[['q05', 'q25', 'median', 'q75', 'q95', 'maximum']].to_numpy(float)))
        for i, upper in enumerate(uppers):
            lower = pooled.minimum if i == 0 else uppers[i - 1]
            for domain, target, crop, f in domains(crops):
                valid = f.loc[valid_metric(f, metric)]
                selected = valid.loc[(valid[metric].ge(lower) if i == 0 else valid[metric].gt(lower)) & valid[metric].le(upper)]
                n, pixels = len(selected), int(selected.reference_pixels.sum())
                intervals.append(dict(domain=domain, target=target, site=SITES.get(target, 'all'), crop=crop,
                                      metric=metric, unit=UNITS[metric], interval_id=i + 1,
                                      lower=lower, upper=upper, lower_inclusive=i == 0, upper_inclusive=True,
                                      n_patches=n, pixels=pixels, area_ha=pixels * .09,
                                      patch_share=n / len(valid) if len(valid) else np.nan,
                                      area_share=pixels / valid.reference_pixels.sum() if len(valid) else np.nan,
                                      singleton_count=int(selected.reference_pixels.eq(1).sum()),
                                      no_interior_count=int(selected.no_interior.sum()),
                                      edge_count=int(selected.touches_outer_edge.sum()),
                                      purpose='pooled_area_ecdf_diagnostic_not_frozen_grades'))
    interval_frame = pd.DataFrame(intervals)
    for key, f in interval_frame.groupby(['domain', 'target', 'crop', 'metric'], sort=False):
        source = freq_lookup[key]
        check('diagnostic interval closure ' + str(key),
              int(f.n_patches.sum()) == int(source.n_patches.sum()) and int(f.pixels.sum()) == int(source.pixels.sum()))
    write(interval_frame, 'diagnostic_value_intervals')

    reused = old_dist.copy()
    reused['source_file'] = (OLD / 'feature_distributions.csv').relative_to(ROOT).as_posix()
    reused['statistical_object'] = 'whole_reference_crop_patch'
    reused['weighting'] = 'patch_equal'
    reused['algorithm'] = 'linear_order_statistics'
    reused['unit'] = reused.metric.map(UNITS)
    write(reused, 'reused_indicator_distributions')
    cor = correlations.assign(source_file=(OLD / 'feature_correlations.csv').relative_to(ROOT).as_posix(),
                              origin='reused_not_recomputed')
    write(cor, 'reused_indicator_correlations')
    k2 = k2_support.copy()
    k2['spatial_type'] = 'K2-T' + k2.spatial_type.astype(str)
    k2['domain'] = 'site_crop'
    k2['source_file'] = (OLD / 'type_reference_support.csv').relative_to(ROOT).as_posix()
    k2['scheme'] = 'K2'
    k4 = k4_support.assign(scheme='K4', source_file=(K4 / 'type_reference_support.csv').relative_to(ROOT).as_posix())
    write(pd.concat([k2, k4], ignore_index=True), 'reused_type_reference_support')
    all_classes = features.groupby(['target', 'site', 'crop'], sort=False).agg(
        n_patches=('PID', 'size'), pixels=('reference_pixels', 'sum'),
        boundary_pixels=('boundary_pixels', 'sum'), interior_pixels=('interior_pixels', 'sum'),
        far_interior_pixels=('far_interior_pixels', 'sum')).reset_index()
    all_classes['area_ha'] = all_classes.pixels * .09
    write(all_classes, 'all_class_reference_support')
    write(pd.DataFrame(CHECKS), 'verification_checks')
    info = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
                head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                data_status='derived / exploratory', current_reference_statistics='Verified',
                inputs=INPUTS, script_sha256=sha(__file__),
                counts_scope='192 index records checked; 4 OOF arrays reopened; remaining 188 not re-audited',
                history_distance_generation='Partially verified; not rerun', fragstats_rerun=False,
                clustering_rerun=False, grades_chosen=False, figures_created=False,
                counts=dict(all_class_patches=len(features), crop_patches=len(crops), crop_pixels=int(crops.reference_pixels.sum()),
                            frequency_rows=len(frequencies), distribution_rows=len(distribution), checks=len(CHECKS)))
    (SUM / 'run_manifest.json').write_text(json.dumps(info, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(info['counts'], indent=2))
    print(distribution.loc[distribution.domain.eq('all'), ['metric', 'weighting', 'q25', 'median', 'q75', 'q95']].to_string(index=False))


def audit():
    """Read back delivery tables and independently check joins and ECDF inequalities."""
    if (SUM / 'delivery_checks.csv').exists():
        raise FileExistsError('Delivery checks already preserved.')
    run = json.loads((SUM / 'run_manifest.json').read_text(encoding='utf-8'))
    for relative, expected in run['inputs'].items():
        check('unchanged input ' + relative, sha(ROOT / relative) == expected)
    frequency = read(PROC / 'value_frequency_cumulative.csv')
    distribution = read(SUM / 'indicator_distribution_reading.csv')
    support = read(SUM / 'reference_support_reading.csv')
    intervals = read(SUM / 'diagnostic_value_intervals.csv')
    overlap = read(SUM / 'stratum_distribution_overlap.csv')
    check('distribution dimensions', len(distribution) == 66 and not distribution.duplicated(
        ['domain', 'target', 'crop', 'metric', 'weighting']).any())
    check('overlap dimensions', len(overlap) == 84 and not overlap.duplicated(
        ['metric', 'target_a', 'crop_a', 'target_b', 'crop_b']).any())
    check('complete support domains', len(support) == 11 and not support.duplicated(['domain', 'target', 'crop']).any())
    check('no current missing inputs', distribution.n_missing_or_invalid.eq(0).all()
          and distribution.pixels_missing_or_invalid.eq(0).all())
    check('all-class reference closure', read(SUM / 'all_class_reference_support.csv').groupby('target').pixels.sum().eq(6553600).all())
    for key, values in frequency.groupby(['domain', 'target', 'crop', 'metric'], sort=False):
        selected = distribution.loc[(distribution[['domain', 'target', 'crop', 'metric']] == key).all(axis=1)]
        n, pixels = int(values.n_patches.sum()), int(values.pixels.sum())
        check('serialized frequency denominator ' + str(key), len(selected) == 2
              and selected.n_valid.eq(n).all() and selected.pixels_valid.eq(pixels).all()
              and values.n_patches.gt(0).all() and values.pixels.gt(0).all())
        check('serialized cdf ' + str(key), values.value.is_unique and values.value.is_monotonic_increasing
              and np.allclose(values.patch_cdf, values.n_patches.cumsum() / n, rtol=0, atol=1e-15)
              and np.allclose(values.area_cdf, values.pixels.cumsum() / pixels, rtol=0, atol=1e-15))
        weighted = selected.loc[selected.weighting.eq('reference_pixel_area')].iloc[0]
        for field, probability in QUANTILES.items():
            # Verify the defining inequality rather than repeat the production quantile function.
            before = int(values.loc[values.value.lt(weighted[field]), 'pixels'].sum())
            through = int(values.loc[values.value.le(weighted[field]), 'pixels'].sum())
            check('weighted ECDF inequality ' + str(key) + '/' + field,
                  before < probability * pixels <= through and values.value.eq(weighted[field]).any())
        d, t, c, metric = key
        group = intervals.loc[intervals.domain.eq(d) & intervals.target.eq(t)
                              & intervals.crop.eq(c) & intervals.metric.eq(metric)].sort_values('interval_id')
        allocated = np.zeros(len(values), dtype=np.int8)
        for row in group.itertuples():
            mask = ((values.value.ge(row.lower) if row.lower_inclusive else values.value.gt(row.lower))
                    & values.value.le(row.upper)).to_numpy()
            allocated += mask
            check('serialized interval support ' + str(key) + '/' + str(row.interval_id),
                  int(values.loc[mask, 'n_patches'].sum()) == row.n_patches
                  and int(values.loc[mask, 'pixels'].sum()) == row.pixels)
        check('no interval duplication or omission ' + str(key), (allocated == 1).all())
    for stem, source in [('reused_indicator_distributions', OLD / 'feature_distributions.csv'),
                         ('reused_indicator_correlations', OLD / 'feature_correlations.csv')]:
        original = read(source)
        copied = read(SUM / (stem + '.csv'))
        check('reused fields unchanged ' + stem, copied[original.columns].equals(original))
    type_support = read(SUM / 'reused_type_reference_support.csv')
    for scheme in ['K2', 'K4']:
        rows = type_support.loc[type_support.scheme.eq(scheme) & type_support.domain.eq('site_crop')]
        total = rows.groupby(['target', 'crop'])[['n_patches', 'pixels']].sum().sort_index()
        reference = support.loc[support.domain.eq('site_crop')].set_index(['target', 'crop'])[['n_patches', 'pixels']].sort_index()
        check('reused ' + scheme + ' total count/area closure', np.array_equal(total, reference))
    for filename in ['existing_gap_inventory.csv', 'results_use_index.csv', 'indicator_availability.csv']:
        check('readable review table ' + filename, not read(SUM / filename).empty)
    check('no grade assignments or figures', not list(PROC.glob('*assign*'))
          and not any(p.suffix.lower() in {'.png', '.pdf', '.svg'} for p in SUM.rglob('*')))
    write(pd.DataFrame(CHECKS), 'delivery_checks')
    print('Delivery checks:', len(CHECKS), 'Verified')


def finalize():
    path = SUM / 'delivery_manifest.json'
    if path.exists():
        raise FileExistsError(path)
    run = json.loads((SUM / 'run_manifest.json').read_text(encoding='utf-8'))
    for relative, expected in run['inputs'].items():
        if sha(ROOT / relative) != expected:
            raise ValueError('Input changed: ' + relative)
    paths = [p for directory in [PROC, SUM] for p in directory.rglob('*') if p.is_file()]
    paths += [Path(__file__), ROOT / 'scripts/test/test_sec33_indicator_grading.py',
              ROOT / 'plan/tasks/2026-10-09-sec33-indicator-grading-preparation.md']
    manifest = dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
                    input_hash_recheck='Verified', inputs=run['inputs'],
                    files={p.relative_to(ROOT).as_posix(): sha(p) for p in paths})
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('Final input and delivery hashes:', len(manifest['inputs']), len(manifest['files']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    stages = parser.add_mutually_exclusive_group()
    stages.add_argument('--audit', action='store_true', help='Check saved tables; preserve an independent delivery check file.')
    stages.add_argument('--finalize', action='store_true', help='Seal hashes after documentation and tests; never overwrite a prior seal.')
    args = parser.parse_args()
    if args.audit:
        audit()
    elif args.finalize:
        finalize()
    else:
        prepare()

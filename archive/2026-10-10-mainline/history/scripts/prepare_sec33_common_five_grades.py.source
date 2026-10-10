"""Reference-only common five-grade candidates; no prediction errors are read."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal, ROUND_FLOOR
import json
from pathlib import Path
import subprocess

import numpy as np
import pandas as pd

from explore_sec33_reference_patch_types import sha
from prepare_sec33_indicator_grading import inverse_ecdf

ROOT = Path(__file__).resolve().parents[1]
NAME = 'sec33_common_five_grades'
PROC = ROOT / 'results/processed' / NAME
SUM = ROOT / 'results/summary' / NAME
BASE = ROOT / 'results/processed/sec33_reference_patch_types'
PREP = ROOT / 'results/summary/sec33_indicator_grading_preparation'
FREQ = ROOT / 'results/processed/sec33_indicator_grading_preparation/value_frequency_cumulative.csv'
SITES = {'iw_2023': 'A', 'iw2_2023': 'B', 'ida_2023': 'C', 'il_2023': 'D'}
CROPS = ['corn', 'soybean']
LABELS = dict(enumerate(['Ⅰ', 'Ⅱ', 'Ⅲ', 'Ⅳ', 'Ⅴ'], 1))
STATUS = 'pending_author_review_not_frozen'
SCHEMES = ['recommended', 'area_ecdf_alternative']
SHAPE_CUTS = [1.3, 1.6, 2.0, 2.5]
COUNT_FIELDS = ['n_patches', 'pixels', 'singleton_count', 'no_interior_patches',
                'with_interior_patches', 'edge_patches', 'edge_pixels',
                'boundary_pixels', 'interior_pixels', 'far_interior_pixels']
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
    path = (PROC if processed else SUM) / (name + '.csv')
    if path.exists():
        raise FileExistsError(path)
    frame.to_csv(path, index=False, float_format='%.17g', encoding='utf-8')


def write_json(data, path):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def pixel_cuts(area_cuts):
    return [int((Decimal(str(value)) / Decimal('0.09')).to_integral_value(rounding=ROUND_FLOOR))
            for value in area_cuts]


def classify(values, cuts, reverse=False, minimum=0, integer=False):
    """Zero is an invalid sentinel, never a grade; equal cut values stay together."""
    values = np.asarray(values, dtype=float)
    cuts = np.asarray(cuts, dtype=float)
    if cuts.shape != (4,) or not np.isfinite(cuts).all() or not (np.diff(cuts) > 0).all():
        raise ValueError('four strictly increasing finite cuts required')
    valid = np.isfinite(values) & (values >= minimum if minimum > 0 else values > 0)
    if integer:
        valid &= values == np.floor(values)
    result = np.zeros(values.shape, dtype=np.int8)
    asc = np.searchsorted(cuts, values[valid], side='left')
    result[valid] = 5 - asc if reverse else 1 + asc
    return result


def assign(frame, metric, cuts):
    if metric == 'AREA':
        grades = classify(frame.reference_pixels, cuts, minimum=1, integer=True)
        valid_area = np.isfinite(frame.AREA) & (frame.AREA > 0)
        agrees = np.isclose(frame.AREA, frame.reference_pixels * .09, atol=1e-12, rtol=0)
        grades[~(valid_area & agrees).to_numpy()] = 0
    elif metric == 'SHAPE':
        grades = classify(frame.SHAPE, cuts, reverse=True, minimum=1)
    else:
        raise ValueError(metric)
    return grades


def domains(frame):
    yield 'all', 'all', 'all', 'all', frame
    for target, site in SITES.items():
        for crop in CROPS:
            yield 'site_crop', target, site, crop, frame.loc[frame.target.eq(target) & frame.crop.eq(crop)]


def reference_counts(frame):
    return dict(n_patches=len(frame), pixels=int(frame.reference_pixels.sum()),
                singleton_count=int(frame.reference_pixels.eq(1).sum()),
                no_interior_patches=int(frame.interior_pixels.eq(0).sum()),
                with_interior_patches=int(frame.interior_pixels.gt(0).sum()),
                edge_patches=int(frame.touches_outer_edge.sum()),
                edge_pixels=int(frame.loc[frame.touches_outer_edge, 'reference_pixels'].sum()),
                boundary_pixels=int(frame.boundary_pixels.sum()),
                interior_pixels=int(frame.interior_pixels.sum()),
                far_interior_pixels=int(frame.far_interior_pixels.sum()))


def support_rows(frame, grades):
    frame = frame.copy()
    frame['grade_number'] = grades
    rows = []
    for domain, target, site, crop, f in domains(frame):
        valid = f.loc[f.grade_number.gt(0)]
        for grade in range(1, 6):
            z = f.loc[f.grade_number.eq(grade)]
            counts = reference_counts(z)
            rows.append(dict(domain=domain, target=target, site=site, crop=crop,
                             grade_number=grade, grade=LABELS[grade], **counts,
                             area_ha=counts['pixels'] * .09,
                             domain_n_patches=len(f), domain_pixels=int(f.reference_pixels.sum()),
                             valid_n_patches=len(valid), valid_pixels=int(valid.reference_pixels.sum()),
                             patch_share=counts['n_patches'] / len(f) if len(f) else np.nan,
                             area_share=counts['pixels'] / f.reference_pixels.sum() if len(f) else np.nan,
                             boundary_share=counts['boundary_pixels'] / counts['pixels'] if counts['pixels'] else np.nan,
                             support_status='has_reference_support' if len(z) else 'zero_reference_support',
                             scheme_status=STATUS))
    return rows


def definitions(config):
    rows = []
    for scheme in SCHEMES:
        for metric in ['AREA', 'SHAPE']:
            cuts = config['schemes'][scheme][metric]['raw_cuts_ascending']
            edges = ([0] if metric == 'AREA' else [1]) + cuts + [None]
            pcut = config['schemes'][scheme]['AREA']['pixel_cuts_ascending']
            for grade in range(1, 6):
                asc = grade - 1 if metric == 'AREA' else 5 - grade
                lower, upper = edges[asc:asc + 2]
                row = dict(scheme=scheme, metric=metric, grade_number=grade, grade=LABELS[grade],
                           spatial_meaning=('面积从较小到较大' if metric == 'AREA' else '形状从较不规则到较规则'),
                           raw_lower=lower, raw_upper=upper,
                           lower_inclusive=metric == 'SHAPE' and asc == 0,
                           upper_inclusive=upper is not None, upper_unbounded=upper is None,
                           unit='ha' if metric == 'AREA' else 'dimensionless',
                           value_direction='increasing' if metric == 'AREA' else 'decreasing',
                           pixel_min_inclusive=(1 if asc == 0 else pcut[asc - 1] + 1) if metric == 'AREA' else None,
                           pixel_max_inclusive=(pcut[asc] if asc < 4 else None) if metric == 'AREA' else None,
                           attainable_upper_ha=(pcut[asc] * .09 if asc < 4 else None) if metric == 'AREA' else None,
                           cut_basis=config['schemes'][scheme][metric]['basis'], scheme_status=STATUS)
                rows.append(row)
    return pd.DataFrame(rows)


def coverage_tables(support):
    wide, diagnosis = [], []
    sub = support.loc[support.domain.eq('site_crop')]
    for (scheme, metric, grade), z in sub.groupby(['scheme', 'metric', 'grade_number'], sort=False):
        row = dict(scheme=scheme, metric=metric, grade_number=grade, grade=LABELS[grade])
        for x in z.itertuples():
            prefix = x.site + '_' + x.crop
            for field in ['n_patches', 'pixels', 'patch_share', 'area_share']:
                row[prefix + '_' + field] = getattr(x, field)
        wide.append(row)
        by_site = z.groupby('site').pixels.sum()
        total = int(z.pixels.sum())
        min_row = z.loc[z.n_patches.idxmin()]
        max_row = z.loc[z.n_patches.idxmax()]
        largest = z.loc[z.pixels.idxmax()]
        diagnosis.append(dict(scheme=scheme, metric=metric, grade_number=grade, grade=LABELS[grade],
                              pooled_n_patches=int(z.n_patches.sum()), pooled_pixels=total,
                              empty_strata=int(z.n_patches.eq(0).sum()),
                              minimum_stratum_n_patches=int(min_row.n_patches),
                              minimum_count_stratum=min_row.site + '_' + min_row.crop,
                              maximum_stratum_n_patches=int(max_row.n_patches),
                              maximum_count_stratum=max_row.site + '_' + max_row.crop,
                              minimum_stratum_area_share=float(z.area_share.min()),
                              maximum_stratum_area_share=float(z.area_share.max()),
                              largest_stratum=largest.site + '_' + largest.crop,
                              largest_stratum_share_of_grade_pixels=int(largest.pixels) / total if total else np.nan,
                              largest_site=by_site.idxmax(),
                              largest_site_share_of_grade_pixels=int(by_site.max()) / total if total else np.nan))
    return pd.DataFrame(wide), pd.DataFrame(diagnosis)


def validate_reference(features, old_support):
    check('unique target PID and patch_uid', not features.duplicated(['target', 'PID']).any()
          and features.patch_uid.is_unique)
    check('four targets three classes', set(features.target) == set(SITES)
          and set(features.crop) == {'corn', 'soybean', 'other'})
    check('site mapping', features.site.eq(features.target.map(SITES)).all())
    for field in ['PID', 'reference_pixels', 'boundary_pixels', 'interior_pixels', 'far_interior_pixels']:
        check('integer support ' + field, np.issubdtype(features[field].dtype, np.integer)
              and features[field].ge(0).all())
    check('positive identity and reference support', features.PID.gt(0).all() and features.reference_pixels.gt(0).all())
    for field in ['no_interior', 'touches_outer_edge']:
        check('boolean marker ' + field, pd.api.types.is_bool_dtype(features[field]))
    check('boundary plus interior equals total', features.boundary_pixels.add(features.interior_pixels).eq(features.reference_pixels).all())
    check('far interior subset', features.far_interior_pixels.le(features.interior_pixels).all())
    check('no interior flag', features.no_interior.eq(features.interior_pixels.eq(0)).all())
    crops = features.loc[features.crop.isin(CROPS)].copy()
    for domain, target, _, crop, f in domains(crops):
        old = old_support.loc[old_support.domain.eq(domain) & old_support.target.eq(target) & old_support.crop.eq(crop)]
        check('one prior reference total ' + domain + target + crop, len(old) == 1)
        current = reference_counts(f)
        fields = set(COUNT_FIELDS) & set(old.columns)
        check('prior saved support ' + domain + target + crop,
              all(current[field] == int(old.iloc[0][field]) for field in fields))
    return crops


def prepare():
    if SUM.exists() or PROC.exists():
        raise FileExistsError('Independent outputs already exist; use --audit, never overwrite.')
    features = read(BASE / 'reference_patch_features.csv')
    freq = read(FREQ)
    old_support = read(PREP / 'reference_support_reading.csv')
    read(PREP / 'indicator_distribution_reading.csv')
    index = read(BASE / 'prediction_count_index.csv')
    crops = validate_reference(features, old_support)
    check('saved frequency unique identities', not freq.duplicated(['domain', 'target', 'crop', 'metric', 'value']).any())
    pooled_area = freq.loc[freq.domain.eq('all') & freq.metric.eq('AREA')]
    alt_area = inverse_ecdf(pooled_area.value, pooled_area.pixels.to_numpy(), [.2, .4, .6, .8]).tolist()
    config = dict(result_kind='derived_exploratory', scheme_status=STATUS,
                  analysis_unit='full_reference_8_neighbor_connected_crop_patch',
                  identity=['target', 'PID'], pixel_area_ha=.09,
                  grade_labels=LABELS, prediction_errors_used_for_cut_selection=False,
                  schemes={}, ENN='descriptive_only_no_five_grade_proposal')
    for scheme, area in [('recommended', [1, 10, 50, 150]), ('area_ecdf_alternative', alt_area)]:
        config['schemes'][scheme] = dict(
            AREA=dict(raw_cuts_ascending=area, pixel_cuts_ascending=pixel_cuts(area),
                      basis=('reference_distribution_small_patch_detail_and_readable_area_intervals' if scheme == 'recommended'
                             else 'pooled_reference_pixel_weighted_ecdf_q20_q40_q60_q80')),
            SHAPE=dict(raw_cuts_ascending=SHAPE_CUTS, reverse_grade=True,
                       basis='readable_cuts_near_pooled_reference_area_ecdf_quintiles_not_equal_area_bins'))
    assignment_columns = ['target', 'site', 'crop', 'PID', 'patch_uid', 'AREA', 'SHAPE', 'ENN',
                          'reference_pixels', 'boundary_pixels', 'interior_pixels', 'far_interior_pixels',
                          'no_interior', 'touches_outer_edge']
    assignment = crops[assignment_columns].copy()
    assignment['singleton'] = crops.reference_pixels.eq(1)
    supports, excluded, invalid = [], [], []
    for scheme in SCHEMES:
        for metric in ['AREA', 'SHAPE']:
            cuts = config['schemes'][scheme][metric]['pixel_cuts_ascending' if metric == 'AREA' else 'raw_cuts_ascending']
            grades = assign(crops, metric, cuts)
            column = metric + '_' + scheme
            assignment[column + '_number'] = pd.array(np.where(grades == 0, np.nan, grades), dtype='Int8')
            assignment[column + '_grade'] = pd.Series(grades, index=crops.index).map(LABELS)
            assignment[column + '_status'] = np.where(grades > 0, 'valid', 'missing_or_invalid_metric')
            supports.extend(dict(scheme=scheme, metric=metric, **row) for row in support_rows(crops, grades))
            excluded.extend(dict(scheme=scheme, metric=metric, domain=d, target=t, site=s, crop=c,
                                 excluded_n_patches=len(f), excluded_pixels=int(f.reference_pixels.sum()))
                            for d, t, s, c, f in domains(crops.loc[grades == 0]))
            for row in crops.loc[grades == 0].itertuples():
                invalid.append(dict(scheme=scheme, metric=metric, target=row.target, crop=row.crop, PID=row.PID,
                                    value=getattr(row, metric), reference_pixels=row.reference_pixels,
                                    missing_reason='nonfinite_nonpositive_below_physical_minimum_or_area_pixel_disagreement'))
            for d, t, _, c, f in domains(crops):
                oldfreq = freq.loc[freq.domain.eq(d) & freq.target.eq(t) & freq.crop.eq(c) & freq.metric.eq(metric)]
                check('saved frequency reference total ' + scheme + metric + d + t + c,
                      int(oldfreq.n_patches.sum()) == len(f) and int(oldfreq.pixels.sum()) == int(f.reference_pixels.sum()))
    support = pd.DataFrame(supports)
    cover, diagnosis = coverage_tables(support)
    definition = definitions(config)
    quantiles, enn = [], []
    for d, t, s, c, _ in domains(crops):
        for metric in ['AREA', 'SHAPE', 'ENN']:
            z = freq.loc[freq.domain.eq(d) & freq.target.eq(t) & freq.crop.eq(c) & freq.metric.eq(metric)]
            for weighting, field in [('patch_count_ecdf', 'n_patches'), ('reference_pixel_area', 'pixels')]:
                values = inverse_ecdf(z.value, z[field].to_numpy(), [.2, .4, .6, .8])
                quantiles.extend(dict(domain=d, target=t, site=s, crop=c, metric=metric,
                                      weighting=weighting, probability=q, value=v, source=FREQ.relative_to(ROOT).as_posix())
                                 for q, v in zip([.2, .4, .6, .8], values))
            if metric == 'ENN':
                sixty = z.loc[z.value.eq(60)]
                n, p = int(z.n_patches.sum()), int(z.pixels.sum())
                n60, p60 = int(sixty.n_patches.sum()), int(sixty.pixels.sum())
                enn.append(dict(domain=d, target=t, site=s, crop=c, n_unique=len(z),
                                minimum=z.value.min(), maximum=z.value.max(), n_total=n, pixels_total=p,
                                at_60m_n_patches=n60, at_60m_pixels=p60,
                                at_60m_patch_share=n60 / n, at_60m_area_share=p60 / p,
                                above_60m_n_patches=n - n60, above_60m_pixels=p - p60,
                                pixel_q20_q40_q60_q80=';'.join(str(v) for v in values),
                                grade_recommendation='descriptive_only_no_forced_five_grades'))
    small = freq.loc[freq.metric.eq('AREA') & freq.domain.isin(['all', 'site_crop']) & freq.value.le(13.77)].copy()
    small['source'] = FREQ.relative_to(ROOT).as_posix()
    small['current_action'] = 'reuse_exact_saved_frequency_not_new_raw_measurement'
    small_intervals = []
    bins = [0, 1, 4, 11, 33, 55, 111, 153, None]
    for d, t, s, c, f in domains(crops):
        for number, (lo, hi) in enumerate(zip(bins[:-1], bins[1:]), 1):
            mask = f.reference_pixels.gt(lo)
            if hi is not None:
                mask &= f.reference_pixels.le(hi)
            counts = reference_counts(f.loc[mask])
            small_intervals.append(dict(domain=d, target=t, site=s, crop=c, diagnostic_interval=number,
                                        pixel_lower_exclusive=lo, pixel_upper_inclusive=hi,
                                        area_lower_exclusive_ha=lo * .09,
                                        area_upper_inclusive_ha=hi * .09 if hi is not None else None,
                                        **counts, patch_share=counts['n_patches'] / len(f),
                                        area_share=counts['pixels'] / f.reference_pixels.sum(),
                                        purpose='small_value_reference_diagnostic_not_grades'))
    inventory = []
    for (target, crop), f in features.groupby(['target', 'crop']):
        inventory.append(dict(target=target, site=SITES[target], crop=crop, **reference_counts(f),
                              grading_scope='crop_five_grade_candidates' if crop in CROPS else 'ungraded_retained_reference_class'))
    check('index interface 192 records', len(index) == 192 and not index.duplicated(['kind', 'model', 'source', 'target', 'fold']).any())
    check('index interface 12 within 180 cross', index.kind.eq('within').sum() == 12 and index.kind.eq('cross').sum() == 180)
    PROC.mkdir(parents=True)
    SUM.mkdir(parents=True)
    write_json(config, SUM / 'candidate_config.json')
    write(assignment, 'patch_grade_assignments', processed=True)
    write(definition, 'grade_definitions')
    write(support, 'grade_support')
    write(cover, 'five_grade_coverage_comparison')
    write(diagnosis, 'coverage_diagnostics')
    write(pd.DataFrame(excluded), 'excluded_reference_support')
    write(pd.DataFrame(invalid, columns=['scheme', 'metric', 'target', 'crop', 'PID', 'value', 'reference_pixels', 'missing_reason']), 'invalid_metric_records', processed=True)
    write(pd.DataFrame(quantiles), 'cutpoint_reference_quantiles')
    write(pd.DataFrame(enn), 'enn_concentration_diagnostic')
    write(small, 'area_small_value_frequency')
    write(pd.DataFrame(small_intervals), 'area_small_interval_support')
    write(pd.DataFrame(inventory), 'all_class_reference_inventory')
    write(pd.DataFrame(CHECKS), 'production_checks')
    write_json(dict(created_utc=datetime.now(timezone.utc).isoformat(),
                    baseline_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                    inputs=INPUTS, script_sha256=sha(Path(__file__)),
                    reused_helper_sha256=sha(ROOT / 'scripts/prepare_sec33_indicator_grading.py'),
                    hash_helper_sha256=sha(ROOT / 'scripts/explore_sec33_reference_patch_types.py'),
                    command='python -B scripts/prepare_sec33_common_five_grades.py',
                    scheme_status=STATUS, result_kind='derived_exploratory',
                    predictions_reopened=0, distance_or_fragstats_recomputed=False), SUM / 'run_manifest.json')
    print(f'Prepared {len(assignment)} crop identities, {len(support)} support rows; {len(CHECKS)} checks.')


def audit():
    features = read(BASE / 'reference_patch_features.csv')
    crops = features.loc[features.crop.isin(CROPS)]
    assignment = read(PROC / 'patch_grade_assignments.csv')
    support = read(SUM / 'grade_support.csv')
    definition = read(SUM / 'grade_definitions.csv')
    exclusions = read(SUM / 'excluded_reference_support.csv')
    freq = read(FREQ)
    check('saved assignments unique complete keys', not assignment.duplicated(['target', 'PID']).any()
          and set(assignment[['target', 'PID']].itertuples(index=False, name=None)) ==
          set(crops[['target', 'PID']].itertuples(index=False, name=None)))
    linked = crops.merge(assignment, on=['target', 'PID'], suffixes=('_ref', ''), validate='one_to_one')
    for field in ['crop', 'patch_uid', 'AREA', 'SHAPE', 'reference_pixels', 'boundary_pixels',
                  'interior_pixels', 'far_interior_pixels', 'no_interior', 'touches_outer_edge']:
        check('saved source field ' + field, linked[field].eq(linked[field + '_ref']).all())
    check('support keys and expected size', len(support) == 180 and not support.duplicated(
        ['scheme', 'metric', 'domain', 'target', 'crop', 'grade_number']).any())
    check('definitions expected size', len(definition) == 20)
    for scheme in SCHEMES:
        for metric in ['AREA', 'SHAPE']:
            column = metric + '_' + scheme + '_number'
            grades = linked[column]
            good = linked[metric].notna() & (linked[metric] > 0)
            check('all current finite values assigned ' + scheme + metric, grades.notna().eq(good).all())
            observed = pd.DataFrame(dict(value=linked[metric], grade=grades))
            check('identical values one grade ' + scheme + metric, observed.groupby('value').grade.nunique().le(1).all())
            ordered = observed.dropna().sort_values('value').grade.to_numpy()
            check('grade direction ' + scheme + metric, (np.diff(ordered) >= 0).all() if metric == 'AREA' else (np.diff(ordered) <= 0).all())
            masks = []
            defs = definition.loc[definition.scheme.eq(scheme) & definition.metric.eq(metric)]
            for row in defs.itertuples():
                if metric == 'AREA':
                    mask = linked.reference_pixels.ge(row.pixel_min_inclusive)
                    if not row.upper_unbounded:
                        mask &= linked.reference_pixels.le(row.pixel_max_inclusive)
                else:
                    mask = linked.SHAPE.ge(row.raw_lower) if row.lower_inclusive else linked.SHAPE.gt(row.raw_lower)
                    if not row.upper_unbounded:
                        mask &= linked.SHAPE.le(row.raw_upper)
                masks.append(mask.to_numpy())
                check('saved definition actual membership ' + scheme + metric + str(row.grade_number),
                      np.array_equal(mask, grades.eq(row.grade_number)))
            check('five masks mutually exclusive complete ' + scheme + metric, np.equal(np.stack(masks).sum(0), 1).all())
            for d, t, _, c, f in domains(linked):
                z = support.loc[support.scheme.eq(scheme) & support.metric.eq(metric) & support.domain.eq(d)
                                & support.target.eq(t) & support.crop.eq(c)]
                totals = reference_counts(f)
                check('saved grade count closure ' + scheme + metric + d + t + c,
                      len(z) == 5 and all(int(z[field].sum()) == totals[field] for field in COUNT_FIELDS))
                for row in z.itertuples():
                    actual = reference_counts(f.loc[f[column].eq(row.grade_number)])
                    check('saved exact grade support ' + scheme + metric + d + t + c + str(row.grade_number),
                          all(getattr(row, field) == actual[field] for field in COUNT_FIELDS)
                          and row.domain_n_patches == len(f) and row.domain_pixels == int(f.reference_pixels.sum())
                          and np.isclose(row.patch_share, actual['n_patches'] / len(f), rtol=0, atol=1e-15)
                          and np.isclose(row.area_share, actual['pixels'] / f.reference_pixels.sum(), rtol=0, atol=1e-15))
                oldfreq = freq.loc[freq.domain.eq(d) & freq.target.eq(t) & freq.crop.eq(c) & freq.metric.eq(metric)]
                for row in defs.itertuples():
                    if metric == 'AREA':
                        pixels = np.rint(oldfreq.value / .09).astype('int64')
                        mask = pixels.ge(row.pixel_min_inclusive)
                        if not row.upper_unbounded:
                            mask &= pixels.le(row.pixel_max_inclusive)
                    else:
                        mask = oldfreq.value.ge(row.raw_lower) if row.lower_inclusive else oldfreq.value.gt(row.raw_lower)
                        if not row.upper_unbounded:
                            mask &= oldfreq.value.le(row.raw_upper)
                    actual = z.loc[z.grade_number.eq(row.grade_number)].iloc[0]
                    check('reuse frequency independent grade support ' + scheme + metric + d + t + c + str(row.grade_number),
                          int(oldfreq.loc[mask, 'n_patches'].sum()) == actual.n_patches
                          and int(oldfreq.loc[mask, 'pixels'].sum()) == actual.pixels)
            pooled = support.loc[support.scheme.eq(scheme) & support.metric.eq(metric) & support.domain.eq('all')]
            strata = support.loc[support.scheme.eq(scheme) & support.metric.eq(metric) & support.domain.eq('site_crop')]
            for grade in range(1, 6):
                a = pooled.loc[pooled.grade_number.eq(grade)].iloc[0]
                b = strata.loc[strata.grade_number.eq(grade)]
                check('eight strata recover pooled ' + scheme + metric + str(grade),
                      len(b) == 8 and all(int(b[field].sum()) == a[field] for field in COUNT_FIELDS))
    check('no current exclusions', exclusions.excluded_n_patches.eq(0).all() and exclusions.excluded_pixels.eq(0).all())
    cover = read(SUM / 'five_grade_coverage_comparison.csv')
    for row in support.loc[support.domain.eq('site_crop')].itertuples():
        z = cover.loc[cover.scheme.eq(row.scheme) & cover.metric.eq(row.metric) & cover.grade_number.eq(row.grade_number)]
        check('coverage reading matches support ' + row.scheme + row.metric + row.site + row.crop + str(row.grade_number),
              len(z) == 1 and all(z.iloc[0][row.site + '_' + row.crop + '_' + field] == getattr(row, field)
                                 for field in ['n_patches', 'pixels', 'patch_share', 'area_share']))
    small = read(SUM / 'area_small_interval_support.csv')
    for d, t, _, c, f in domains(crops):
        z = small.loc[small.domain.eq(d) & small.target.eq(t) & small.crop.eq(c)]
        total = reference_counts(f)
        check('small diagnostics exhaustive count closure ' + d + t + c,
              len(z) == 8 and all(int(z[field].sum()) == total[field] for field in COUNT_FIELDS))
    write(pd.DataFrame(CHECKS), 'delivery_checks')
    print(f'Audited saved tables: {len(CHECKS)} checks.')


def finalize():
    if (SUM / 'delivery_manifest.json').exists() or (SUM / 'reference_diagnostic_checks.csv').exists():
        raise FileExistsError('Final verification already exists; never overwrite.')
    manifest_path = SUM / 'run_manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for path, expected in manifest['inputs'].items():
        check('unchanged input ' + path, sha(ROOT / path) == expected)
    features = read(BASE / 'reference_patch_features.csv')
    crops = features.loc[features.crop.isin(CROPS)]
    freq = read(FREQ)
    inventory = read(SUM / 'all_class_reference_inventory.csv')
    check('all class inventory unique complete', len(inventory) == 12
          and not inventory.duplicated(['target', 'crop']).any())
    for (target, crop), f in features.groupby(['target', 'crop']):
        z = inventory.loc[inventory.target.eq(target) & inventory.crop.eq(crop)]
        actual = reference_counts(f)
        check('all class inventory exact ' + target + crop, len(z) == 1
              and all(int(z.iloc[0][field]) == actual[field] for field in COUNT_FIELDS))
    for target in SITES:
        check('full label reference total ' + target, int(inventory.loc[inventory.target.eq(target), 'pixels'].sum()) == 2560 ** 2)
    small = read(SUM / 'area_small_value_frequency.csv')
    expected = freq.loc[freq.metric.eq('AREA') & freq.domain.isin(['all', 'site_crop']) & freq.value.le(13.77)].reset_index(drop=True)
    check('exact small frequency reused without renormalization', small[expected.columns].reset_index(drop=True).equals(expected))
    intervals = read(SUM / 'area_small_interval_support.csv')
    for d, t, _, c, f in domains(crops):
        z = intervals.loc[intervals.domain.eq(d) & intervals.target.eq(t) & intervals.crop.eq(c)]
        for row in z.itertuples():
            mask = f.reference_pixels.gt(row.pixel_lower_exclusive)
            if pd.notna(row.pixel_upper_inclusive):
                mask &= f.reference_pixels.le(row.pixel_upper_inclusive)
            actual = reference_counts(f.loc[mask])
            check('exact small interval ' + d + t + c + str(row.diagnostic_interval),
                  all(getattr(row, field) == actual[field] for field in COUNT_FIELDS)
                  and np.isclose(row.patch_share, actual['n_patches'] / len(f), atol=1e-15, rtol=0)
                  and np.isclose(row.area_share, actual['pixels'] / f.reference_pixels.sum(), atol=1e-15, rtol=0))
    quantiles = read(SUM / 'cutpoint_reference_quantiles.csv')
    keys = ['domain', 'target', 'crop', 'metric', 'weighting', 'probability']
    check('reference quantile complete unique keys', len(quantiles) == 216 and not quantiles.duplicated(keys).any())
    for row in quantiles.itertuples():
        z = freq.loc[freq.domain.eq(row.domain) & freq.target.eq(row.target) & freq.crop.eq(row.crop) & freq.metric.eq(row.metric)]
        field = 'pixels' if row.weighting == 'reference_pixel_area' else 'n_patches'
        below = int(z.loc[z.value.lt(row.value), field].sum())
        through = int(z.loc[z.value.le(row.value), field].sum())
        threshold = row.probability * int(z[field].sum())
        check('quantile observed value left inverse ' + row.domain + row.target + row.crop + row.metric + row.weighting + str(row.probability),
              z.value.eq(row.value).any() and below < threshold <= through)
    enn = read(SUM / 'enn_concentration_diagnostic.csv')
    check('ENN diagnostic complete keys', len(enn) == 9 and not enn.duplicated(['domain', 'target', 'crop']).any())
    for row in enn.itertuples():
        z = freq.loc[freq.domain.eq(row.domain) & freq.target.eq(row.target) & freq.crop.eq(row.crop) & freq.metric.eq('ENN')]
        sixty = z.loc[z.value.eq(60)]
        q = quantiles.loc[quantiles.domain.eq(row.domain) & quantiles.target.eq(row.target) & quantiles.crop.eq(row.crop)
                          & quantiles.metric.eq('ENN') & quantiles.weighting.eq('reference_pixel_area')].sort_values('probability')
        check('ENN exact concentration ' + row.domain + row.target + row.crop,
              row.n_unique == len(z) and row.minimum == z.value.min() and row.maximum == z.value.max()
              and row.n_total == int(z.n_patches.sum()) and row.pixels_total == int(z.pixels.sum())
              and row.at_60m_n_patches == int(sixty.n_patches.sum()) and row.at_60m_pixels == int(sixty.pixels.sum())
              and row.above_60m_n_patches + row.at_60m_n_patches == row.n_total
              and row.above_60m_pixels + row.at_60m_pixels == row.pixels_total
              and np.isclose(row.at_60m_area_share, row.at_60m_pixels / row.pixels_total, atol=1e-15, rtol=0)
              and np.isclose(row.at_60m_patch_share, row.at_60m_n_patches / row.n_total, atol=1e-15, rtol=0)
              and np.array_equal([float(v) for v in row.pixel_q20_q40_q60_q80.split(';')], q.value))
    support = read(SUM / 'grade_support.csv')
    diagnosis = read(SUM / 'coverage_diagnostics.csv')
    _, expected = coverage_tables(support)
    check('coverage diagnostics exact saved values', diagnosis.equals(expected))
    config = json.loads((SUM / 'candidate_config.json').read_text(encoding='utf-8'))
    pooled_area = quantiles.loc[quantiles.domain.eq('all') & quantiles.metric.eq('AREA')
                               & quantiles.weighting.eq('reference_pixel_area')].sort_values('probability').value.tolist()
    check('alternative configuration from reference quantiles', config['schemes']['area_ecdf_alternative']['AREA']['raw_cuts_ascending'] == pooled_area)
    assignment = read(PROC / 'patch_grade_assignments.csv')
    for scheme in SCHEMES:
        for metric in ['AREA', 'SHAPE']:
            prefix = metric + '_' + scheme
            check('saved grade labels and validity ' + prefix,
                  assignment[prefix + '_number'].map(LABELS).eq(assignment[prefix + '_grade']).all()
                  and assignment[prefix + '_status'].eq('valid').all())
    check('candidate explicitly not frozen', config['scheme_status'] == STATUS
          and support.scheme_status.eq(STATUS).all()
          and config['prediction_errors_used_for_cut_selection'] is False)
    write(pd.DataFrame(CHECKS), 'reference_diagnostic_checks')
    paths = [p for folder in [SUM, PROC] for p in folder.iterdir() if p.is_file()]
    paths += [Path(__file__), ROOT / 'scripts/test/test_sec33_common_five_grades.py',
              ROOT / 'scripts/prepare_sec33_indicator_grading.py', ROOT / 'scripts/explore_sec33_reference_patch_types.py',
              ROOT / 'plan/tasks/2026-10-10-sec33-common-five-grades.md']
    hashes = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    write_json(dict(finalized_utc=datetime.now(timezone.utc).isoformat(), inputs=manifest['inputs'],
                    files_sha256=hashes, self_hash_excluded=True, scheme_status=STATUS), SUM / 'delivery_manifest.json')
    print(f'Finalized {len(hashes)} file hashes; {len(CHECKS)} reference diagnostic checks; {len(manifest["inputs"])} inputs unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--audit', action='store_true')
    group.add_argument('--finalize', action='store_true')
    args = parser.parse_args()
    (audit if args.audit else finalize if args.finalize else prepare)()

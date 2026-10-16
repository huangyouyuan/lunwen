"""Reuse integer counts for full-site AREA x SHAPE x boundary/interior analysis.

No training, inference, landscape-index calculation or raster modification.
Outputs are created exclusively; existing products must first be preserved.
"""
from pathlib import Path
import hashlib
import itertools
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/summary/sec31_joint_boundary'
REF = ROOT / 'results/processed/sec33_reference_patch_types'
OLD = ROOT / 'results/summary/spatial_error_conditions'
AREA = ['<10', '10-<50', '50-<100', '100-<200', '200-<500', '>=500']
SHAPE = ['1-<1.5', '1.5-<2', '2-<3', '>=3']
A_EDGES = [0, 10, 50, 100, 200, 500, np.inf]
S_EDGES = [1, 1.5, 2, 3, np.inf]
KEY = ['target', 'crop', 'group']
INPUTS, CHECKS = {}, []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(path):
    INPUTS[Path(path).relative_to(ROOT).as_posix()] = sha(path)


def read(path):
    record(path)
    return pd.read_csv(path, float_precision='round_trip')


def check(name, condition):
    CHECKS.append(dict(check=name, status='Verified' if condition else 'Not verified'))
    if not condition:
        raise ValueError(name)


def ratio(n, d):
    n, d = np.broadcast_arrays(np.asarray(n, float), np.asarray(d, float))
    return np.divide(n, d, out=np.full(n.shape, np.nan), where=d != 0)


def bin_index(values, edges):
    values = np.asarray(values, float)
    if not np.isfinite(values).all() or (values < edges[0]).any():
        raise ValueError('Invalid full-patch attribute')
    return np.searchsorted(edges, values, side='right') - 1


def save(df, name):
    path = OUT / name
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        df.to_csv(stream, index=False, float_format='%.17g', lineterminator='\n')
    return path


def compare_models(metrics, baseline, other):
    keys = KEY + ['position']
    cols = keys + ['reference_pixels', 'fn', 'whole_fn', 'whole_crop_pixels',
                   'omission_rate', 'group_reference_pixels', 'patch_count', 'site']
    a = metrics[metrics.model.eq(baseline)][cols].set_index(keys).sort_index()
    b = metrics[metrics.model.eq(other)][cols].set_index(keys).sort_index()
    if not a.index.equals(b.index) or not np.array_equal(a.reference_pixels, b.reference_pixels):
        raise ValueError('Model reference supports differ')
    r = a[['site', 'patch_count', 'group_reference_pixels', 'reference_pixels', 'whole_crop_pixels']].copy()
    r['baseline_model'], r['comparison_model'] = baseline, other
    r['fn_baseline'], r['fn_comparison'] = a.fn, b.fn
    r['omission_rate_baseline'], r['omission_rate_comparison'] = a.omission_rate, b.omission_rate
    r['rate_reduction_pp'] = 100 * (a.omission_rate - b.omission_rate)
    r['net_fewer_pixels'] = a.fn - b.fn
    r['whole_net_fewer_pixels'] = a.whole_fn - b.whole_fn
    r['net_reduction_share'] = ratio(r.net_fewer_pixels, r.whole_net_fewer_pixels)
    r['whole_rate_contribution_pp'] = 100 * ratio(r.net_fewer_pixels, a.whole_crop_pixels)
    r['direction'] = np.select([r.net_fewer_pixels.gt(0), r.net_fewer_pixels.lt(0)],
                               ['fewer_omissions', 'more_omissions'], default='equal')
    return r.reset_index()


def verify_patch_counts(metrics):
    """Independent rebuild from explicit PID-indexed saved integer cubes."""
    features = read(REF / 'reference_patch_features.csv')
    index = read(REF / 'prediction_count_index.csv')
    index = index[index.kind.eq('within')]
    check('12 within-site prediction identities', len(index) == 12 and
          index.source.eq(index.target).all() and index.fold.eq(0).all())
    for run in index.itertuples():
        path = REF / run.file
        record(path)
        check(f'{run.target}/{run.model} saved-count SHA256', sha(path) == run.sha256)
        with np.load(path) as z:
            pid = z['PID']
            counts = z['patch_band_prediction_counts'].astype(np.int64)
        f = features[features.target.eq(run.target)].set_index('PID')
        check(f'{run.target}/{run.model} unique PID', f.index.is_unique and len(np.unique(pid)) == len(pid))
        use = np.isin(pid, f.index)
        check(f'{run.target}/{run.model} unmatched PID is zero background',
              np.array_equal(pid[~use], [0]) and not counts[~use].any())
        f, counts = f.loc[pid[use]].copy(), counts[use]
        check(f'{run.target}/{run.model} full-patch support',
              np.array_equal(counts.sum(axis=(1, 2)), f.reference_pixels))
        for crop, true in [('corn', 0), ('soybean', 2)]:
            use = f.crop.eq(crop).to_numpy()
            fc, cc = f[use].copy(), counts[use]
            aa, ss = bin_index(fc.AREA, A_EDGES), bin_index(fc.SHAPE, S_EDGES)
            groups = [AREA[a] + '|' + SHAPE[s] for a, s in zip(aa, ss)]
            for position, sl in [('boundary', slice(0, 1)), ('interior', slice(1, 7))]:
                n = cc[:, sl, :].sum(axis=(1, 2))
                fn = n - cc[:, sl, true].sum(axis=1)
                actual = pd.DataFrame(dict(group=groups, reference_pixels=n, fn=fn)).groupby('group').sum()
                expected = metrics[metrics.target.eq(run.target) & metrics.model.eq(run.model) &
                                   metrics.crop.eq(crop) & metrics.position.eq(position)].set_index('group')
                actual = actual.reindex(expected.index, fill_value=0)
                check(f'{run.target}/{run.model}/{crop}/{position} independent integers',
                      np.array_equal(actual[['reference_pixels', 'fn']], expected[['reference_pixels', 'fn']]))


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    names = ['reference_support.csv', 'within_position_metrics.csv', 'within_joint_metrics.csv',
             'within_site_position_metrics.csv', 'small_area_by_shape.csv', 'model_comparisons.csv',
             'verification_checks.csv', 'manifest.json']
    if any((OUT / n).exists() for n in names):
        raise FileExistsError('Preserve existing products before regenerating')
    support = read(OLD / 'reference_group_support.csv')
    old = read(OLD / 'within_group_metrics.csv')
    bins = read(ROOT / 'results/summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv')
    bins['group'] = [AREA[a] + '|' + SHAPE[s] for a, s in zip(bins.area_bin_order, bins.shape_bin_order)]
    joint = support[support.scheme.eq('area_shape')].copy()
    j = joint.merge(bins, on=KEY, suffixes=('_old', ''), validate='one_to_one')
    check('192 joint combinations match figure2 reference and patch counts', len(j) == 192 and
          j.reference_pixels.eq(j.reference_pixels_old).all() and j.patch_count.eq(j.patch_count_old).all())
    d = old[old.scheme.eq('area_shape_distance')].copy()
    d[['group', 'distance']] = d.group.str.rsplit('|', n=1, expand=True)
    check('complete 1728 joint-distance rows', len(d) == 1728)
    check('identical reference pixels across models',
          d.groupby(KEY + ['distance']).reference_pixels.nunique().eq(1).all())
    d['position'] = np.where(d.distance.eq('0<d<=1'), 'boundary', 'interior')
    m = d.groupby(KEY + ['site', 'model', 'position'], as_index=False)[['reference_pixels', 'fn']].sum()
    check('1152 joint-position model rows', len(m) == 1152)
    c = m[m.model.eq('convgru')].pivot(index=KEY, columns='position', values='reference_pixels').reset_index()
    r = bins[KEY + ['site', 'area_bin_order', 'shape_bin_order', 'area_bin', 'shape_bin',
                    'patch_count', 'reference_pixels', 'area_ha']].merge(c, on=KEY, validate='one_to_one')
    r = r.rename(columns={'boundary': 'boundary_reference_pixels', 'interior': 'interior_reference_pixels'})
    r['whole_crop_pixels'] = r.groupby(['target', 'crop']).reference_pixels.transform('sum')
    r['area_share'] = ratio(r.reference_pixels, r.whole_crop_pixels)
    r['boundary_share'] = ratio(r.boundary_reference_pixels, r.reference_pixels)
    check('reference boundary plus entire interior closes',
          r.reference_pixels.eq(r.boundary_reference_pixels + r.interior_reference_pixels).all())
    m = m.merge(r.drop(columns=['site']).rename(columns={'reference_pixels': 'group_reference_pixels',
                  'area_share': 'group_area_share'}), on=KEY, validate='many_to_one')
    whole = old[old.scheme.eq('all')][['target', 'crop', 'model', 'fn']].rename(columns={'fn': 'whole_fn'})
    m = m.merge(whole, on=['target', 'crop', 'model'], validate='many_to_one')
    m['position_area_share'] = ratio(m.reference_pixels, m.whole_crop_pixels)
    m['position_share_in_group'] = ratio(m.reference_pixels, m.group_reference_pixels)
    m['omission_rate'] = ratio(m.fn, m.reference_pixels)
    m['error_share'] = ratio(m.fn, m.whole_fn)
    verify_patch_counts(m)
    keys = ['target', 'site', 'crop', 'model', 'group']
    g = m.groupby(keys, as_index=False)[['reference_pixels', 'fn']].sum()
    g = g.merge(r.drop(columns='site').rename(columns={'reference_pixels': 'group_reference_pixels'}),
                on=KEY, validate='many_to_one').merge(whole, on=['target', 'crop', 'model'], validate='many_to_one')
    g['omission_rate'], g['error_share'] = ratio(g.fn, g.reference_pixels), ratio(g.fn, g.whole_fn)
    prev = old[old.scheme.eq('area_shape')].set_index(KEY + ['model']).sort_index()
    curr = g.set_index(KEY + ['model']).sort_index()
    check('joint FN and reference counts close to existing tables',
          curr.index.equals(prev.index) and np.array_equal(curr[['reference_pixels', 'fn']], prev[['reference_pixels', 'fn']]))
    wholekeys = ['target', 'site', 'crop', 'model', 'position']
    w = m.groupby(wholekeys, as_index=False)[['reference_pixels', 'fn']].sum().merge(
        whole, on=['target', 'crop', 'model'], validate='many_to_one')
    totals = r.groupby(['target', 'crop'], as_index=False).reference_pixels.sum().rename(columns={'reference_pixels': 'whole_crop_pixels'})
    w = w.merge(totals, on=['target', 'crop'], validate='many_to_one')
    w['area_share'], w['omission_rate'], w['error_share'] = ratio(w.reference_pixels, w.whole_crop_pixels), ratio(w.fn, w.reference_pixels), ratio(w.fn, w.whole_fn)
    s = m[m.area_bin_order.lt(2)].groupby(wholekeys + ['shape_bin_order', 'shape_bin'], as_index=False)[['reference_pixels', 'fn']].sum()
    s = s.merge(whole, on=['target', 'crop', 'model'], validate='many_to_one').merge(totals, on=['target', 'crop'], validate='many_to_one')
    s['area_share'], s['omission_rate'], s['error_share'] = ratio(s.reference_pixels, s.whole_crop_pixels), ratio(s.fn, s.reference_pixels), ratio(s.fn, s.whole_fn)
    contrasts = pd.concat([compare_models(m, a, b) for a, b in
                          [('convgru', 'unet3d'), ('convgru', 'utae'), ('unet3d', 'utae')]], ignore_index=True)
    for identity, x in contrasts.groupby(['target', 'crop', 'baseline_model', 'comparison_model']):
        check(f'{identity} signed net differences close', x.net_fewer_pixels.sum() == x.whole_net_fewer_pixels.iloc[0])
        check(f'{identity} signed contribution closes', np.isclose(x.net_reduction_share.sum(), 1) if x.whole_net_fewer_pixels.iloc[0] else x.net_reduction_share.isna().all())
    products = []
    for df, name in zip([r, m, g, w, s, contrasts, pd.DataFrame(CHECKS)], names[:-1]):
        products.append(save(df, name))
    manifest = dict(date='2026-10-17', data_status='derived', verification='Verified',
        scope='Saved integer counts and same-reference joint-position aggregation; raw raster and figure verification recorded separately.',
        area_bins=AREA, shape_bins=SHAPE, boundary='saved band0; independently verified <=30m full-reference class edges',
        interior='all saved bands1:7; every non-boundary reference crop pixel',
        input_sha256=INPUTS, script_sha256=sha(Path(__file__)),
        output_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in products})
    with (OUT / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write('\n')
    print(f'Verified {len(CHECKS)} checks; wrote {len(r)} support, {len(m)} position and {len(contrasts)} signed comparison rows.')


if __name__ == '__main__':
    main()

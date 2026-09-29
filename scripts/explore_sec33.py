#!/usr/bin/env python3
"""3.3 derived/exploratory results; never edits manuscript or original inputs.

Run prepare first to freeze feature-only grouping, then analyze.
External paths may be overridden for another Windows/WSL checkout.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROC = ROOT / 'results/processed/sec33_exploration'
SUM = ROOT / 'results/summary/sec33_exploration'
SITES = {'iw': 'A', 'iw2': 'B', 'ida': 'C', 'il': 'D'}
MODELS = ['convgru', 'unet3d', 'utae']
CLASSES = ['corn', 'other', 'soybean']
CROPS = ['corn', 'soybean']
METRICS = ['ED', 'AREA_MN', 'AI']
CM = [f'cm_{i}{j}' for i in range(3) for j in range(3)]
GK = ['target', 'metric', 'crop', 'group']
INPUTS: dict[str, dict] = {}
CHECKS: list[dict] = []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def register(path, role):
    path = Path(path).resolve()
    win = path.as_posix()
    wsl = '/mnt/' + win[0].lower() + win[2:] if len(win) > 1 and win[1] == ':' else win
    INPUTS[win] = dict(windows_path=win, wsl_path=wsl, sha256=sha(path),
                       bytes=path.stat().st_size, role=role)
    return path


def read(path, role='external derived input'):
    return pd.read_csv(register(path, role))


def save(df, path):
    out = df.copy()
    out['data_status'] = 'derived'
    out['analysis_status'] = 'exploratory'
    path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(path, index=False, encoding='utf-8', float_format='%.12g', na_rep='NA')


def check(name, condition, detail=''):
    if not bool(condition):
        raise ValueError(f'{name}: {detail}')
    CHECKS.append(dict(check=name, result='Verified', detail=detail))


def unique(df, keys, n, label):
    check(label + ' rows/keys', len(df) == n and not df.duplicated(keys).any(), f'{n} rows; {keys}')


def split_values(values):
    """Right-closed terciles; identical values never split; NA is separate."""
    x = np.asarray(values, dtype=float)
    finite = np.isfinite(x)
    out = np.full(len(x), 'missing', dtype=object)
    if not finite.any():
        return out, [], [], 'no_finite_values'
    q = np.quantile(x[finite], [1 / 3, 2 / 3], method='linear')
    cuts = sorted(set(float(v) for v in q if v < x[finite].max()))
    reason = []
    if len(set(q)) < 2:
        reason.append('duplicate_quantiles')
    if any(q >= x[finite].max()):
        reason.append('cut_at_maximum')
    bins = np.searchsorted(cuts, x[finite], side='left')
    used = sorted(set(bins))
    if len(used) < len(cuts) + 1:
        reason.append('empty_interval')
        cuts = [float(x[finite][bins == b].max()) for b in used[:-1]]
        bins = np.searchsorted(cuts, x[finite], side='left')
    names = {1: ['all'], 2: ['low', 'high'], 3: ['low', 'mid', 'high']}[len(set(bins))]
    out[finite] = np.asarray(names)[bins]
    return out, q.tolist(), cuts, ';'.join(reason) or 'none'


def features(args):
    f = read(args.patch_dir / 'patch_spatial_features.csv')
    unique(f, ['patch_uid'], 1600, 'feature')
    check('sites', set(f.site) == set(SITES))
    check('400 original patches/site', f.groupby('site').patch_id.apply(lambda x: set(x) == set(range(400))).all())
    check('patch grid', ((f.row == f.patch_id // 20) & (f.col == f.patch_id % 20)).all())
    check('dataset/uid', (f.dataset_id == f.site + '_2023').all() and
          (f.patch_uid == f.dataset_id + '__p' + f.patch_id.map(lambda x: f'{x:04d}')).all())
    check('pixel totals', (f[[c + '_pixels' for c in CLASSES]].sum(axis=1) == f.valid_pixels).all()
          and (f.valid_pixels == 128 * 128).all())
    for c in CLASSES:
        check(c + ' presence', (f[c + '_class_present'] == (f[c + '_pixels'] > 0)).all())
        check(c + ' ratio', np.allclose(f[c + '_ratio'], f[c + '_pixels'] / f.valid_pixels, atol=5.1e-11, rtol=0))
    check('ED finite nonnegative', (np.isfinite(f.ED) & (f.ED >= 0)).all())
    # Cross-check named columns and class IDs against canonical FRAGSTATS exports.
    land = read(args.frag_dir / '标签切片景观级指标.csv')
    cls = read(args.frag_dir / '标签切片类别级指标.csv')
    unique(land, ['patch_uid'], 1600, 'landscape export')
    unique(cls, ['patch_uid', 'class_id'], 4800, 'class export')
    check('FRAGSTATS class identity', (cls.class_id.map({1: 'corn', 2: 'other', 3: 'soybean'}) == cls.class_name).all())
    check('patch ED export', np.array_equal(f.set_index('patch_uid').ED.sort_index(), land.set_index('patch_uid').ed_reported.sort_index()))
    for c in CLASSES:
        src = cls[cls.class_name == c].set_index('patch_uid').reindex(f.patch_uid)
        check(c + ' pixels export', np.array_equal(f[c + '_pixels'], src.class_pixels))
        for metric, col in [('AREA_MN', 'area_mn_reported'), ('AI', 'ai_reported')]:
            values = f[c + '_' + metric]
            check(c + ' ' + metric + ' export', np.allclose(values, src[col], equal_nan=True, atol=0, rtol=0))
            check(c + ' ' + metric + ' range', ((values.dropna() > 0) if metric == 'AREA_MN' else values.dropna().between(0, 100)).all())
            check(c + ' absent ' + metric, values[~f[c + '_class_present']].isna().all())
        check(c + ' AI defined flag', (f[c + '_AI_defined'] == np.isfinite(f[c + '_AI'])).all())
    return f


def make_groups(f):
    assignments, thresholds = [], []
    for site in SITES:
        site_f = f[f.site == site].sort_values('patch_id')
        for metric, crop in itertools.product(METRICS, CROPS):
            values = site_f['ED' if metric == 'ED' else crop + '_' + metric]
            group, q, cuts, reason = split_values(values)
            reasons = np.full(len(values), '', dtype=object)
            missing = group == 'missing'
            absent = ~site_f[crop + '_class_present'].to_numpy()
            reasons[missing & absent] = 'class_absent'
            reasons[missing & ~absent] = 'present_but_' + metric + '_undefined'
            a = site_f[['patch_uid', 'patch_id', 'valid_pixels'] + [c + '_pixels' for c in CLASSES]].copy()
            a = a.assign(target=site + '_2023', target_code=SITES[site], metric=metric,
                         crop=crop, feature_value=values.to_numpy(), group=group, missing_reason=reasons)
            assignments.append(a)
            thresholds.append(dict(target=site + '_2023', target_code=SITES[site], metric=metric,
                                   crop=crop, q1=q[0] if q else np.nan, q2=q[1] if q else np.nan,
                                   actual_cuts=json.dumps(cuts), merge_reason=reason,
                                   finite_count=int(np.isfinite(values).sum()), missing_count=int(missing.sum())))
    a = pd.concat(assignments, ignore_index=True)
    for target, x in a[a.metric == 'ED'].groupby('target'):
        check('ED same for both crops ' + target,
              x.pivot(index='patch_uid', columns='crop', values='group').nunique(axis=1).eq(1).all())
    stats = a.groupby(GK, sort=True).agg(feature_min=('feature_value', 'min'), feature_max=('feature_value', 'max'),
        patches=('patch_uid', 'size'), valid_pixels=('valid_pixels', 'sum'),
        **{c + '_pixels': (c + '_pixels', 'sum') for c in CLASSES}).reset_index()
    for c in CLASSES:
        stats[c + '_ratio'] = stats[c + '_pixels'] / stats.valid_pixels
    return a, pd.DataFrame(thresholds), stats


def prepare(args):
    a, t, s = make_groups(features(args))
    save(a, PROC / 'patch_groups.csv')
    save(t, PROC / 'group_thresholds.csv')
    save(s, SUM / 'group_composition.csv')
    lock = dict(data_status='derived', analysis_status='exploratory',
                note='Only feature inputs were read; model outcomes have not been loaded.',
                protocol_sha256=sha(ROOT / 'plan/sec33-exploration-protocol.md'),
                feature_inputs=list(INPUTS.values()),
                grouping_files={p.name: sha(p) for p in [PROC / 'patch_groups.csv', PROC / 'group_thresholds.csv']})
    (PROC / 'grouping_lock.json').write_text(json.dumps(lock, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('Prepared and frozen 24 feature/crop/site schemes, 9600 patch assignments.')


def metrics(cm, crop):
    cm = np.asarray(cm, dtype=np.int64).reshape(3, 3)
    i = CLASSES.index(crop)
    truth, pred, tp = int(cm[i].sum()), int(cm[:, i].sum()), int(cm[i, i])
    den = truth + pred
    return dict(f1=2 * tp / den if den else np.nan, true_pixels=truth, predicted_pixels=pred,
                false_positive_pixels=pred - tp, false_negative_pixels=truth - tp,
                f1_status='defined' if den else 'no_true_or_predicted_class')


def dr(base, cross):
    return 100 * (base - cross) / base if np.isfinite(base) and base > 0 and np.isfinite(cross) else np.nan


def load_outcomes(args, f):
    run = args.patch_dir / 'Patch级空间底表运行记录.json'
    metadata = json.loads(register(run, 'historical provenance; not rerun').read_text(encoding='utf-8-sig'))
    check('CM label mapping in provenance', metadata['class_mapping'] == {'0': 'corn', '1': 'other', '2': 'soybean'})
    w = read(args.patch_dir / 'within_patch_oof.csv').rename(columns={'dataset_id': 'target'})
    c = read(args.patch_dir / 'cross_patch_fold.csv').drop(columns=['source', 'target']).rename(
        columns={'source_dataset_id': 'source', 'target_dataset_id': 'target', 'source_fold': 'fold'})
    unique(w, ['model', 'target', 'patch_uid'], 4800, 'within')
    unique(c, ['model', 'source', 'target', 'fold', 'patch_uid'], 72000, 'cross')
    for d, keys, n, label in [(w, ['model', 'target'], 12, 'within'), (c, ['model', 'source', 'target', 'fold'], 180, 'cross')]:
        sizes = d.groupby(keys).size()
        check(label + ' coverage', len(sizes) == n and sizes.eq(400).all() and set(d.model) == set(MODELS))
        check(label + ' CM integers', np.isfinite(d[CM]).all().all() and (d[CM] >= 0).all().all() and (d[CM] % 1 == 0).all().all())
        z = d.merge(f[['patch_uid', 'dataset_id'] + [k + '_pixels' for k in CLASSES]], on='patch_uid', validate='many_to_one')
        check(label + ' target identity', len(z) == len(d) and (z.target == z.dataset_id).all())
        for i, crop in enumerate(CLASSES):
            check(label + ' true row ' + crop, (z[[f'cm_{i}{j}' for j in range(3)]].sum(axis=1) == z[crop + '_pixels']).all())
        check(label + ' pixel/error totals', d[CM].sum(axis=1).eq(d.valid_pixels).all() and
              (d.valid_pixels - d[['cm_00', 'cm_11', 'cm_22']].sum(axis=1)).eq(d.error_pixels).all())
    expected = set(itertools.product(MODELS, [x + '_2023' for x in SITES], [x + '_2023' for x in SITES], range(1, 6)))
    expected = {x for x in expected if x[1] != x[2]}
    check('all directed paths/folds', set(map(tuple, c[['model', 'source', 'target', 'fold']].drop_duplicates().to_numpy())) == expected)
    old = read(args.patch_dir / 'cross_patch_summary.csv', 'legacy error-rate summary; QC only')
    unique(old, ['model', 'source_dataset_id', 'target_dataset_id', 'patch_uid'], 14400, 'legacy patch summary')
    check('legacy five checkpoints', old.n_checkpoints.eq(5).all())
    return w, c


def aggregate(d, a, cross):
    keys = (['model', 'source', 'fold'] if cross else ['model']) + GK
    joined = d.merge(a[['patch_uid', 'target', 'metric', 'crop', 'group']], on=['patch_uid', 'target'], validate='many_to_many')
    check('assignment expansion ' + str(cross), len(joined) == 6 * len(d))
    return joined.groupby(keys, sort=True)[CM].sum().reset_index()


def closure(grouped, raw, keys, kind):
    out = []
    base = raw.set_index(keys)[CM].sort_index().astype('int64')
    for (metric, crop), x in grouped.groupby(['metric', 'crop']):
        total = x.groupby(keys)[CM].sum().sort_index().astype('int64')
        check(f'{kind} closure {metric} {crop}', total.equals(base))
        for idx in base.index:
            out.append(dict(kind=kind, metric=metric, crop=crop, **dict(zip(keys, idx)),
                            max_absolute_cm_difference=0, result='Verified'))
    return out


def full_reference(w, c):
    rw = read(ROOT / 'results/raw/within_site_confusion_matrices.csv', 'repository raw CM')
    rc = read(ROOT / 'results/raw/cross_site_confusion_matrices.csv', 'repository raw CM')
    wp = rw[rw.result_type == 'oof_pooled'].copy()
    for d, base, keys, name in [(w, wp, ['model', 'target'], 'within'), (c, rc, ['model', 'source', 'target', 'fold'], 'cross')]:
        total = d.groupby(keys)[CM].sum().sort_index().astype('int64')
        check(name + ' patch CM to raw', total.equals(base.set_index(keys)[CM].sort_index().astype('int64')))
    wf = rw[rw.result_type == 'fold'].copy()
    check('within patch experiment-fold CM to raw',
          w.groupby(['model', 'target', 'experiment_fold'])[CM].sum().rename_axis(['model', 'target', 'fold']).sort_index().astype('int64').equals(
          wf.set_index(['model', 'target', 'fold'])[CM].sort_index().astype('int64')))
    sw = read(ROOT / 'results/summary/within_site_crop_f1.csv', 'authoritative rounded summary').set_index(['model', 'target'])
    sc = read(ROOT / 'results/summary/cross_site_crop_f1_summary.csv', 'authoritative rounded summary').set_index(['model', 'source', 'target'])
    sf = read(ROOT / 'results/summary/cross_site_crop_f1_per_fold.csv', 'authoritative rounded summary').set_index(['model', 'source', 'target', 'fold'])
    sd = read(ROOT / 'results/summary/crop_f1_relative_degradation_36paths.csv', 'authoritative rounded-summary DR').set_index(['model', 'source', 'target'])
    rows, folds = [], []
    bases = {}
    for _, r in wp.iterrows():
        for crop in CROPS:
            v = metrics(r[CM], crop)['f1']; bases[r.model, r.target, crop] = v
            old = sw.loc[(r.model, r.target), crop + '_f1']
            rows.append(dict(kind='within_f1', model=r.model, target=r.target, crop=crop, recomputed=v, existing=old, tolerance=5.1e-7))
    for _, r in rc.iterrows():
        for crop in CROPS:
            v = metrics(r[CM], crop)['f1']
            folds.append(dict(model=r.model, source=r.source, target=r.target, fold=int(r.fold), crop=crop, f1=v))
            rows.append(dict(kind='cross_fold_f1', model=r.model, source=r.source, target=r.target, fold=r.fold, crop=crop,
                             recomputed=v, existing=sf.loc[(r.model, r.source, r.target, r.fold), crop + '_f1'], tolerance=5.1e-7))
    full = []
    for (model, source, target, crop), x in pd.DataFrame(folds).groupby(['model', 'source', 'target', 'crop']):
        mean, std = x.f1.mean(), x.f1.std(ddof=1); b = bases[model, target, crop]
        record = dict(model=model, source=source, target=target, crop=crop, within_f1=b, cross_f1_mean=mean, cross_f1_std=std, dr_pct=dr(b, mean))
        full.append(record)
        for stat, v in [('mean', mean), ('std', std)]:
            rows.append(dict(kind='cross_' + stat, model=model, source=source, target=target, crop=crop,
                             recomputed=v, existing=sc.loc[(model, source, target), crop + '_f1_' + stat], tolerance=5.1e-7))
        # Existing DR uses six-decimal F1 exports; propagate both rounding errors.
        rounded_b = sw.loc[(model, target), crop + '_f1']
        tol = 100 * (5.1e-7 / b + abs(mean) * 5.1e-7 / (b * rounded_b)) + 5.1e-7
        rows.append(dict(kind='dr_pct', model=model, source=source, target=target, crop=crop,
                         recomputed=dr(b, mean), existing=sd.loc[(model, source, target), crop + '_relative_loss_pct'], tolerance=tol))
    checks = pd.DataFrame(rows)
    checks['absolute_difference'] = abs(checks.recomputed - checks.existing)
    checks['result'] = np.where(checks.absolute_difference <= checks.tolerance, 'Verified', 'Not verified')
    save(checks, SUM / 'full_site_reference_checks.csv')
    check('all full-site F1/DR references', checks.result.eq('Verified').all(), str(checks.groupby('kind').absolute_difference.max().to_dict()))
    save(pd.DataFrame(full), SUM / 'full_site_f1_dr.csv')
    return wp, rc


def score_groups(wg, cg):
    wr, cr = [], []
    for _, row in wg.iterrows():
        wr.append({**row[['model'] + GK].to_dict(), **metrics(row[CM], row.crop)})
    within = pd.DataFrame(wr)
    lookup = within.set_index(['model'] + GK)
    for _, row in cg.iterrows():
        rec = {**row[['model', 'source', 'fold'] + GK].to_dict(), **metrics(row[CM], row.crop)}
        b = lookup.loc[tuple(row[['model'] + GK]), 'f1']
        rec.update(within_f1=b, dr_pct=dr(b, rec['f1']))
        cr.append(rec)
    cross = pd.DataFrame(cr)
    summaries = []
    for key, x in cross.groupby(['model', 'source'] + GK):
        check('five grouped predictions', len(x) == 5 and set(x.fold) == set(range(1, 6)))
        b = x.within_f1.iloc[0]
        good = x.f1.notna().all()
        mean = x.f1.mean() if good else np.nan
        status = 'defined' if good and np.isfinite(b) and b > 0 else ('invalid_within_baseline' if not np.isfinite(b) or b <= 0 else 'incomplete_five_predictions')
        r = dict(zip(['model', 'source'] + GK, key))
        r.update(within_f1=b, cross_f1_mean=mean, cross_f1_std=x.f1.std(ddof=1) if good else np.nan,
                 dr_pct=dr(b, mean), dr_std_pct=x.dr_pct.std(ddof=1) if status == 'defined' else np.nan,
                 n_predictions=5, n_defined_f1=int(x.f1.notna().sum()), status=status,
                 true_pixels=int(x.true_pixels.iloc[0]),
                 false_positive_pixels_mean=x.false_positive_pixels.mean())
        summaries.append(r)
    save(within, SUM / 'within_group_f1.csv')
    save(cross, SUM / 'cross_group_per_fold.csv')
    summary = pd.DataFrame(summaries)
    save(summary, SUM / 'group_f1_dr.csv')
    return summary


def comparisons(summary, args, f):
    contrasts = []
    for key, x in summary.groupby(['model', 'source', 'target', 'metric', 'crop']):
        r = dict(zip(['model', 'source', 'target', 'metric', 'crop'], key))
        x = x.set_index('group')
        for group in ['low', 'mid', 'high']:
            for field in ['within_f1', 'cross_f1_mean', 'dr_pct']:
                r[group + '_' + field] = x.loc[group, field] if group in x.index else np.nan
        delta = r['high_dr_pct'] - r['low_dr_pct']
        r.update(high_minus_low_dr_pct=delta, direction='invalid' if not np.isfinite(delta) else 'high_larger' if delta > 1e-10 else 'low_larger' if delta < -1e-10 else 'tie')
        contrasts.append(r)
    save(pd.DataFrame(contrasts), SUM / 'low_high_contrasts.csv')
    land = read(args.frag_dir / '完整标签景观级指标.csv')
    cls = read(args.frag_dir / '完整标签类别级指标.csv')
    unique(land, ['dataset_id'], 4, 'full landscape')
    unique(cls, ['dataset_id', 'class_id'], 12, 'full class')
    check('full class IDs', (cls.class_id.map({1: 'corn', 2: 'other', 3: 'soybean'}) == cls.class_name).all())
    check('full versus patch true pixel counts', cls.set_index(['dataset_id', 'class_name']).class_pixels.sort_index().equals(
        f.groupby('dataset_id')[[c + '_pixels' for c in CLASSES]].sum().rename(columns={c + '_pixels': c for c in CLASSES}).rename_axis(columns='class_name').stack().sort_index().rename('class_pixels')))
    site_rows = []
    for _, row in cls[cls.class_name.isin(CROPS)].iterrows():
        site_rows.append(dict(site=row.dataset_id, crop=row.class_name,
            ED=float(land.set_index('dataset_id').loc[row.dataset_id, 'ed_reported']),
            AREA_MN=row.area_mn_reported, AI=row.ai_reported, PD=row.pd_reported,
            crop_ratio=row.class_pixels / 6553600))
    site = pd.DataFrame(site_rows)
    save(site, SUM / 'site_features.csv')
    idx = site.set_index(['site', 'crop'])
    diffs = []
    for source, target in itertools.permutations([x + '_2023' for x in SITES], 2):
        for crop, feature in itertools.product(CROPS, ['ED', 'AREA_MN', 'AI', 'crop_ratio']):
            s, t = idx.loc[(source, crop), feature], idx.loc[(target, crop), feature]
            diffs.append(dict(source=source, target=target, crop=crop, site_feature=feature, source_value=s, target_value=t, signed_source_minus_target=s-t, absolute_difference=abs(s-t)))
    diffs = pd.DataFrame(diffs)
    save(diffs, SUM / 'source_target_feature_differences.csv')
    lookup = diffs.set_index(['source', 'target', 'crop', 'site_feature']).absolute_difference
    pairs = []
    for key, x in summary.groupby(['model'] + GK):
        model, target, metric, crop, group = key
        check('three sources same target/group', len(x) == 3 and x.source.nunique() == 3)
        for (_, a), (_, b) in itertools.combinations(x.sort_values('source').iterrows(), 2):
            for feature in ['ED', 'AREA_MN', 'AI', 'crop_ratio']:
                da, db = lookup[a.source, target, crop, feature], lookup[b.source, target, crop, feature]
                fa, fb = a.cross_f1_mean, b.cross_f1_mean
                if not np.isfinite([da, db, fa, fb]).all():
                    outcome = 'invalid'
                elif abs(da-db) <= 1e-10 or abs(fa-fb) <= 1e-10:
                    outcome = 'tie'
                else:
                    outcome = 'consistent' if (da-db)*(fa-fb) < 0 else 'opposite'
                pairs.append(dict(zip(['model'] + GK, key), site_feature=feature,
                    source_a=a.source, source_b=b.source, distance_a=da, distance_b=db,
                    cross_f1_a=fa, cross_f1_b=fb, outcome=outcome))
    pairs = pd.DataFrame(pairs)
    save(pairs, SUM / 'source_pair_comparisons.csv')
    save(pairs.groupby(['model', 'metric', 'crop', 'group', 'site_feature', 'outcome']).size().rename('descriptive_count').reset_index(), SUM / 'source_pair_counts.csv')
    ranks = []
    for site_name, crop in itertools.product(SITES, CROPS):
        z = f.loc[f.site == site_name, [crop + '_AREA_MN', crop + '_AI']].dropna()
        ranks.append(dict(target=site_name + '_2023', crop=crop, n=len(z),
            spearman_rank_r=z.rank(method='average').corr().iloc[0, 1], note='descriptive; no p value'))
    save(pd.DataFrame(ranks), SUM / 'area_ai_rank_redundancy.csv')


def analyze(args):
    lock = json.loads((PROC / 'grouping_lock.json').read_text(encoding='utf-8'))
    check('frozen protocol', lock['protocol_sha256'] == sha(ROOT / 'plan/sec33-exploration-protocol.md'))
    for name, digest in lock['grouping_files'].items():
        check('frozen grouping ' + name, sha(PROC / name) == digest)
    for row in lock['feature_inputs']:
        path = Path(row['windows_path']) if platform.system() == 'Windows' else Path(row['wsl_path'])
        check('frozen feature input ' + path.name, sha(path) == row['sha256'])
    f = features(args)
    a = read(PROC / 'patch_groups.csv', 'frozen feature-only assignments')
    w, c = load_outcomes(args, f)
    wp, rc = full_reference(w, c)
    wg, cg = aggregate(w, a, False), aggregate(c, a, True)
    closed = closure(wg, wp, ['model', 'target'], 'within') + closure(cg, rc, ['model', 'source', 'target', 'fold'], 'cross')
    save(wg, PROC / 'within_group_cm.csv')
    save(cg, PROC / 'cross_group_fold_cm.csv')
    save(pd.DataFrame(closed), SUM / 'cm_closure_checks.csv')
    summary = score_groups(wg, cg)
    comparisons(summary, args, f)
    save(pd.DataFrame(CHECKS), SUM / 'checks.csv')
    manifest = dict(data_status='derived', analysis_status='exploratory', pipeline_status='Verified',
        spatial_metrics_status='Partially verified',
        spatial_metrics_limit='Compared named canonical CSV exports; label GeoTIFF metrics not recomputed in this run.',
        python=platform.python_version(), pandas=pd.__version__, numpy=np.__version__,
        script_sha256=sha(__file__), protocol_sha256=lock['protocol_sha256'],
        inputs=list(INPUTS.values()), output_sha256={str(p.relative_to(ROOT)): sha(p) for d in [PROC, SUM] for p in sorted(d.glob('*.csv'))})
    (SUM / 'run_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Verified: {len(closed)} CM closure records; {len(summary)} grouped path/crop results. Spatial metrics: Partially verified.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['prepare', 'analyze'])
    parser.add_argument('--patch-dir', type=Path, default=Path('D:/cross_site_all_20260916/paper_tables/Patch级空间误差底表'))
    parser.add_argument('--frag-dir', type=Path, default=Path('D:/label/fragstats_results'))
    args = parser.parse_args()
    PROC.mkdir(parents=True, exist_ok=True); SUM.mkdir(parents=True, exist_ok=True)
    (prepare if args.stage == 'prepare' else analyze)(args)


if __name__ == '__main__':
    main()

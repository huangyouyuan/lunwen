#!/usr/bin/env python3
"""AREA_MN exploration with raw-scale F1 differences; immutable historical inputs.

python -B scripts/explore_sec33_f1_raw_scale.py --check-only
python -B scripts/explore_sec33_f1_raw_scale.py
No training, inference, spatial-metric recomputation, manuscript edit or cleanup.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

from explore_sec33 import metrics, split_values

ROOT = Path(__file__).resolve().parents[1]
OLD_PROC = 'results/processed/sec33_exploration'
OLD_SUM = 'results/summary/sec33_exploration'
PROC = 'results/processed/sec33_f1_raw_scale'
SUM = 'results/summary/sec33_f1_raw_scale'
SITES = ('iw_2023', 'iw2_2023', 'ida_2023', 'il_2023')
CODES = dict(zip(SITES, 'ABCD'))
MODELS = ('convgru', 'unet3d', 'utae')
CROPS = ('corn', 'soybean')
CLASSES = ('corn', 'other', 'soybean')
CM = [f'cm_{i}{j}' for i in range(3) for j in range(3)]
GK = ['target', 'crop', 'group']
WK = ['model'] + GK
PK = ['model', 'source'] + GK
ORDERED = ('low', 'mid', 'high')
FIELDS = ('within_f1', 'cross_f1_mean', 'delta_f1')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not bool(condition):
        raise ValueError(message)


def strict_five(frame, baseline):
    """Five distinct source models are mandatory, even if a score is undefined."""
    require(len(frame) == 5 and set(frame.fold) == {1, 2, 3, 4, 5}, 'five distinct predictions required')
    values = frame.sort_values('fold').f1.to_numpy(dtype=float)
    good = np.isfinite(values).all()
    mean = float(values.mean()) if good else np.nan
    valid_base = bool(np.isfinite(baseline))
    delta = baseline - mean if valid_base and good else np.nan
    return dict(within_f1=baseline, cross_f1_mean=mean,
                cross_f1_std=float(values.std(ddof=1)) if good else np.nan,
                cross_f1_min=float(values.min()) if good else np.nan,
                cross_f1_max=float(values.max()) if good else np.nan,
                delta_f1=delta,
                delta_f1_min=baseline-float(values.max()) if valid_base and good else np.nan,
                delta_f1_max=baseline-float(values.min()) if valid_base and good else np.nan,
                n_predictions=5, n_defined_f1=int(np.isfinite(values).sum()),
                within_status='defined' if valid_base else 'undefined_within_f1',
                cross_status='defined' if good else 'incomplete_five_defined_f1',
                delta_status=('defined' if valid_base and good else
                              'undefined_within_f1' if not valid_base else 'incomplete_five_defined_f1'))


def validate_target_patches(frame, features, cross):
    keys = ['model', 'source', 'target', 'fold'] if cross else ['model', 'target']
    expected = {(m, s, t, k) for m in MODELS for s in SITES for t in SITES if s != t for k in range(1, 6)} if cross else {(m, t) for m in MODELS for t in SITES}
    require(not frame.duplicated(keys + ['patch_uid']).any(), 'duplicate outcome patch key')
    require(set(frame[keys].itertuples(index=False, name=None)) == expected, 'outcome experiment identity/coverage')
    feature_sets = features.groupby('dataset_id').patch_uid.agg(set).to_dict()
    for key, g in frame.groupby(keys):
        target = key[2] if cross else key[1]
        require(len(g) == 400 and set(g.patch_uid) == feature_sets[target], f'target patch set mismatch: {key}')
    counts = frame[CM].to_numpy(dtype=float)
    require(np.isfinite(counts).all() and (counts >= 0).all() and (counts == np.floor(counts)).all(), 'CM must be nonnegative integers')
    cols = ['patch_uid', 'dataset_id', 'patch_id'] + [c + '_pixels' for c in CLASSES]
    z = frame.merge(features[cols], on='patch_uid', how='left', validate='many_to_one', suffixes=('', '_feature'))
    require((z.target == z.dataset_id).all(), 'target identity mismatch')
    require((z.patch_id == z.patch_id_feature).all(), 'patch index mismatch')
    for i, crop in enumerate(CLASSES):
        require((z[[f'cm_{i}{j}' for j in range(3)]].sum(axis=1) == z[crop + '_pixels']).all(), 'reference row support mismatch: ' + crop)
    require(frame[CM].sum(axis=1).eq(16384).all() and frame.valid_pixels.eq(16384).all(), 'patch pixel total mismatch')
    require((frame.valid_pixels - frame[['cm_00', 'cm_11', 'cm_22']].sum(axis=1)).eq(frame.error_pixels).all(), 'error pixel mismatch')


class Run:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.inputs = {}
        self.checks = []
        self.tables = {}

    def record(self, path):
        p = Path(path).resolve()
        require(p.exists(), f'missing required input: {p}')
        self.inputs[p.as_posix()] = dict(path=p.as_posix(), sha256=sha(p), bytes=p.stat().st_size)
        return p

    def read(self, path):
        return pd.read_csv(self.record(path), float_precision='round_trip')

    def check(self, name, condition, detail=''):
        require(condition, name + ': ' + str(detail))
        self.checks.append(dict(check=name, result='Verified', detail=str(detail)))

    def table(self, name, data, processed=False):
        data = data.copy()
        data['data_status'] = 'derived'
        data['analysis_status'] = 'exploratory'
        self.tables[f'{PROC if processed else SUM}/{name}.csv'] = data

    def equal_cm(self, name, actual, expected, keys):
        self.check(name + ' unique', not actual.duplicated(keys).any() and not expected.duplicated(keys).any())
        a = actual.set_index(keys)[CM].sort_index().astype('int64')
        b = expected.set_index(keys)[CM].sort_index().astype('int64')
        self.check(name, a.equals(b), f'{len(a)} integer matrices')

    def build(self):
        root = self.root
        old = json.loads(self.record(root / OLD_SUM / 'run_manifest.json').read_text(encoding='utf-8'))
        lock = json.loads(self.record(root / OLD_PROC / 'grouping_lock.json').read_text(encoding='utf-8'))
        self.check('frozen protocol hash', sha(self.record(root / 'plan/sec33-exploration-protocol.md')) == lock['protocol_sha256'])
        for name, digest in lock['grouping_files'].items():
            self.check('frozen assignment hash ' + name, sha(self.record(root / OLD_PROC / name)) == digest)
        paths = {Path(v['windows_path']).name: Path(v['windows_path']) for v in old['inputs']}
        required = {'patch_spatial_features.csv', 'within_patch_oof.csv', 'cross_patch_fold.csv',
                    '标签切片景观级指标.csv', '标签切片类别级指标.csv', '完整标签景观级指标.csv', '完整标签类别级指标.csv', 'Patch级空间底表运行记录.json'}
        for v in old['inputs']:
            if Path(v['windows_path']).name in required:
                self.check('historical input hash ' + Path(v['windows_path']).name,
                           sha(self.record(v['windows_path'])) == v['sha256'])
        for rel, digest in old['output_sha256'].items():
            if Path(rel).name in {'within_group_cm.csv', 'cross_group_fold_cm.csv', 'site_features.csv', 'source_target_feature_differences.csv'}:
                self.check('historical product hash ' + Path(rel).name, sha(self.record(root / rel)) == digest)

        f = self.read(paths['patch_spatial_features.csv'])
        self.check('1600 unique feature patches', len(f) == 1600 and not f.patch_uid.duplicated().any())
        self.check('feature dataset identity', set(f.dataset_id) == set(SITES) and (f.dataset_id == f.site + '_2023').all() and (f.patch_uid == f.dataset_id + '__p' + f.patch_id.map(lambda v: f'{v:04d}')).all())
        self.check('feature grid and pixels', ((f.row == f.patch_id // 20) & (f.col == f.patch_id % 20)).all() and f.valid_pixels.eq(16384).all() and f[[c + '_pixels' for c in CLASSES]].sum(axis=1).eq(f.valid_pixels).all())
        for target, z in f.groupby('dataset_id'):
            self.check('400 patches ' + target, set(z.patch_id) == set(range(400)))
        land = self.read(paths['标签切片景观级指标.csv']).set_index('patch_uid').reindex(f.patch_uid)
        cls = self.read(paths['标签切片类别级指标.csv'])
        self.check('canonical class IDs', (cls.class_id.map({1: 'corn', 2: 'other', 3: 'soybean'}) == cls.class_name).all())
        self.check('canonical ED', np.array_equal(f.ED.to_numpy(), land.ed_reported.to_numpy()))
        for crop in CLASSES:
            z = cls[cls.class_name == crop].set_index('patch_uid').reindex(f.patch_uid)
            self.check('canonical pixels ' + crop, np.array_equal(f[crop + '_pixels'], z.class_pixels))
            for metric, column in [('AREA_MN', 'area_mn_reported'), ('AI', 'ai_reported')]:
                self.check('canonical feature ' + crop + metric, np.allclose(f[crop+'_'+metric], z[column], atol=0, rtol=0, equal_nan=True))

        a = self.read(root / OLD_PROC / 'patch_groups.csv').query("metric == 'AREA_MN'").copy()
        thresholds = self.read(root / OLD_PROC / 'group_thresholds.csv').query("metric == 'AREA_MN'").copy()
        self.check('AREA assignment coverage', len(a) == 3200 and not a.duplicated(['target', 'crop', 'patch_uid']).any() and set(a.crop) == set(CROPS))
        feature_idx = f.set_index('patch_uid')
        for (target, crop), z in a.groupby(['target', 'crop']):
            self.check('assignment target set ' + target + crop, set(z.patch_uid) == set(f.loc[f.dataset_id == target, 'patch_uid']))
            actual = feature_idx.loc[z.patch_uid, crop + '_AREA_MN'].to_numpy()
            labels, q, cuts, reason = split_values(actual)
            self.check('frozen labels from original features ' + target + crop, np.array_equal(labels, z.group.to_numpy()))
            self.check('stored features rounding ' + target + crop, np.allclose(actual, z.feature_value, rtol=1e-11, atol=1e-10, equal_nan=True))
            threshold = thresholds[(thresholds.target == target) & (thresholds.crop == crop)]
            self.check('threshold identity ' + target + crop, len(threshold) == 1)
            t = threshold.iloc[0]
            self.check('threshold values ' + target + crop, np.allclose(q, [t.q1, t.q2], rtol=1e-11, atol=1e-10) and np.array_equal(cuts, json.loads(t.actual_cuts)) and reason == t.merge_reason)
            for c in CLASSES:
                self.check('assignment support ' + target + crop + c, np.array_equal(z[c+'_pixels'], feature_idx.loc[z.patch_uid, c+'_pixels']))
            a.loc[z.index, 'feature_value'] = actual
        composition = []
        for key, z in a.groupby(GK, sort=True):
            target, crop, group = key
            original = feature_idx.loc[z.patch_uid]
            vals = original[crop + '_AREA_MN']
            t = thresholds[(thresholds.target == target) & (thresholds.crop == crop)].iloc[0]
            cuts = json.loads(t.actual_cuts)
            r = dict(zip(GK, key), target_code=CODES[target], metric='AREA_MN', unit='ha',
                     q1=t.q1, q2=t.q2, actual_cuts=t.actual_cuts, merge_reason=t.merge_reason,
                     patches=len(z), valid_pixels=int(original.valid_pixels.sum()),
                     feature_min=vals.min(), feature_median=vals.median() if vals.notna().any() else np.nan, feature_max=vals.max(),
                     lower_bound=cuts[0] if group == 'mid' else cuts[-1] if group == 'high' else np.nan,
                     upper_bound=cuts[0] if group == 'low' else cuts[-1] if group == 'mid' else np.nan,
                     interval_rule='right_closed' if group != 'missing' else 'not_ordered',
                     missing_reason=';'.join(sorted(z.missing_reason.dropna().unique())),
                     patch_set_sha256=hashlib.sha256('\n'.join(sorted(z.patch_uid)).encode()).hexdigest())
            for c in CLASSES:
                r[c + '_pixels'] = int(original[c + '_pixels'].sum())
                r[c + '_ratio'] = r[c + '_pixels'] / r['valid_pixels']
            for label, values in [('ED', original.ED), ('AI', original[crop + '_AI'])]:
                r.update({label+'_min': values.min(), label+'_median': values.median() if values.notna().any() else np.nan, label+'_max': values.max(), label+'_n_defined': int(values.notna().sum())})
            composition.append(r)
        composition = pd.DataFrame(composition)
        self.check('28 AREA groups', len(composition) == 28 and composition.group.eq('missing').sum() == 4)
        self.table('group_features', composition)

        meta = json.loads(paths['Patch级空间底表运行记录.json'].read_text(encoding='utf-8-sig'))
        self.check('CM class mapping', meta['class_mapping'] == {'0': 'corn', '1': 'other', '2': 'soybean'})
        w = self.read(paths['within_patch_oof.csv']).rename(columns={'dataset_id': 'target'})
        c = self.read(paths['cross_patch_fold.csv']).drop(columns=['source', 'target']).rename(columns={'source_dataset_id':'source', 'target_dataset_id':'target', 'source_fold':'fold'})
        for d, cross in [(w, False), (c, True)]:
            validate_target_patches(d, f, cross)
            self.check('outcome identity, target sets, integer CM and row supports ' + str(cross), True, len(d))
        assignments = a[['patch_uid'] + GK]
        wg = w.merge(assignments, on=['patch_uid','target'], validate='many_to_many').groupby(WK)[CM].sum().reset_index()
        cg = c.merge(assignments, on=['patch_uid','target'], validate='many_to_many').groupby(PK+['fold'])[CM].sum().reset_index()
        oldw = self.read(root / OLD_PROC / 'within_group_cm.csv').query("metric == 'AREA_MN'")
        oldc = self.read(root / OLD_PROC / 'cross_group_fold_cm.csv').query("metric == 'AREA_MN'")
        self.equal_cm('patch to frozen within group CM', wg, oldw, WK)
        self.equal_cm('patch to frozen cross group CM', cg, oldc, PK+['fold'])
        self.table('within_group_cm', wg, True)
        self.table('cross_group_fold_cm', cg, True)
        raww = self.read(root / 'results/raw/within_site_confusion_matrices.csv')
        rawc = self.read(root / 'results/raw/cross_site_confusion_matrices.csv')
        self.equal_cm('OOF experiment fold to raw', w.groupby(['model','target','experiment_fold'])[CM].sum().reset_index().rename(columns={'experiment_fold':'fold'}), raww[raww.result_type == 'fold'], ['model','target','fold'])
        closure = []
        restored = {}
        for label, groups, raw, keys in [('within', wg, raww[raww.result_type == 'oof_pooled'], ['model','target']), ('cross', cg, rawc, ['model','source','target','fold'])]:
            for crop in CROPS:
                total = groups[groups.crop == crop].groupby(keys)[CM].sum().reset_index()
                self.equal_cm(label+' closure including missing '+crop, total, raw, keys)
                for rec in total[keys].to_dict('records'):
                    closure.append(dict(kind=label, crop=crop, **rec, max_absolute_cm_difference=0, result='Verified'))
                restored[label] = total
        self.table('cm_closure_checks', pd.DataFrame(closure))
        self.full_reference(restored['within'], restored['cross'])

        within = pd.DataFrame([{**r[WK].to_dict(), **metrics(r[CM], r.crop)} for _, r in wg.iterrows()])
        lookup = within.set_index(WK).f1
        cross_rows = []
        for _, r in cg.iterrows():
            score = metrics(r[CM], r.crop)
            baseline = lookup.loc[tuple(r[WK])]
            cross_rows.append({**r[PK+['fold']].to_dict(), **score, 'within_f1':baseline,
                               'delta_f1':baseline-score['f1'] if np.isfinite(baseline) and np.isfinite(score['f1']) else np.nan})
        cross = pd.DataFrame(cross_rows)
        rows = []
        for key, z in cross.groupby(PK):
            r = dict(zip(PK, key), **strict_five(z, z.within_f1.iloc[0]))
            r.update(true_pixels=int(z.true_pixels.iloc[0]), false_positive_pixels_mean=z.false_positive_pixels.mean(), false_negative_pixels_mean=z.false_negative_pixels.mean())
            rows.append(r)
        main = pd.DataFrame(rows).merge(composition[GK+['patches','patch_set_sha256']], on=GK, validate='many_to_one')
        self.check('main counts and unique keys', len(main) == 252 and len(within) == 84 and len(cross) == 1260 and not main.duplicated(PK).any())
        self.check('216 ordered + 36 missing results', main.group.isin(ORDERED).sum() == 216 and main.group.eq('missing').sum() == 36)
        self.table('within_group_f1', within)
        self.table('cross_group_per_prediction', cross)
        self.table('group_f1_difference', main)
        self.comparisons(main, composition, f, paths)
        issues = []
        for kind, frame, keycols, field in [('within',within,WK,'f1'), ('cross',cross,PK+['fold'],'f1'), ('summary',main,PK,'delta_f1')]:
            for _, r in frame.iterrows():
                reasons = []
                if r.group == 'missing': reasons.append('missing_feature_group_kept_for_closure')
                if not np.isfinite(r[field]): reasons.append('undefined_'+field)
                if kind != 'summary' and r.f1 == 0: reasons.append('defined_zero_f1')
                if kind != 'within' and np.isfinite(r.delta_f1) and r.delta_f1 < 0: reasons.append('negative_delta_f1')
                if reasons:
                    issues.append(dict(kind=kind, **r[keycols].to_dict(), value=r[field], reasons=';'.join(reasons)))
        self.table('exceptions', pd.DataFrame(issues))
        self.table('checks', pd.DataFrame(self.checks))
        return self

    def full_reference(self, w, c):
        root = self.root
        sw = self.read(root/'results/summary/f1_raw_scale/within_site_crop_f1.csv').set_index(['model','target'])
        sf = self.read(root/'results/summary/f1_raw_scale/cross_site_crop_f1_per_fold.csv').set_index(['model','source','target','fold'])
        ss = self.read(root/'results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv').set_index(['model','source','target'])
        sd = self.read(root/'results/summary/f1_raw_scale/crop_f1_difference_36paths.csv').set_index(['model','source','target'])
        audits, folds, rows, bases = [], [], [], {}
        def compare(kind, value, reference, **keys):
            error = abs(value-reference)
            audits.append(dict(kind=kind, **keys, recomputed=value, existing=reference, absolute_difference=error, tolerance=1e-12, result='Verified' if error <= 1e-12 else 'Not verified'))
        for _, r in w.iterrows():
            for crop in CROPS:
                v = metrics(r[CM], crop)['f1']
                bases[r.model,r.target,crop] = v
                compare('within_f1', v, sw.loc[(r.model,r.target),crop+'_f1'], model=r.model,target=r.target,crop=crop)
        for _, r in c.iterrows():
            for crop in CROPS:
                v = metrics(r[CM],crop)['f1']
                keys = dict(model=r.model,source=r.source,target=r.target,crop=crop,fold=int(r.fold))
                folds.append(dict(**keys,f1=v))
                compare('cross_prediction_f1', v, sf.loc[(r.model,r.source,r.target,r.fold),crop+'_f1'], **keys)
        for key,z in pd.DataFrame(folds).groupby(['model','source','target','crop']):
            model,source,target,crop = key
            values = strict_five(z,bases[model,target,crop])
            keys = dict(zip(['model','source','target','crop'], key))
            rows.append(dict(**keys,**values))
            for field,col in [('cross_f1_mean',crop+'_f1_mean'),('cross_f1_std',crop+'_f1_std')]:
                compare(field, values[field], ss.loc[(model,source,target),col], **keys)
            compare('delta_f1',values['delta_f1'],sd.loc[(model,source,target),crop+'_f1_difference'],**keys)
        self.check('current full-site F1 reference', all(r['result']=='Verified' for r in audits), f'{len(audits)} comparisons; max difference {max(r["absolute_difference"] for r in audits):.3g}')
        self.table('full_site_reference_checks',pd.DataFrame(audits))
        self.table('full_site_f1_difference',pd.DataFrame(rows))

    def comparisons(self, main, composition, features, paths):
        ordered = main[main.group.isin(ORDERED)]
        contrasts = []
        for key,z in ordered.groupby(['model','source','target','crop']):
            require(set(z.group)==set(ORDERED), 'ordered group coverage')
            x=z.set_index('group')
            r=dict(zip(['model','source','target','crop'],key))
            for field in FIELDS:
                for group in ORDERED: r[group+'_'+field]=x.loc[group,field]
                for left,right in [('low','mid'),('mid','high'),('low','high')]:
                    r[right+'_minus_'+left+'_'+field]=x.loc[right,field]-x.loc[left,field]
                vals=x.loc[list(ORDERED),field].to_numpy()
                r[field+'_trend']=trend(vals)
            require(abs(r['high_minus_low_delta_f1']-(r['high_minus_low_within_f1']-r['high_minus_low_cross_f1_mean'])) <= 1e-12,'difference decomposition')
            contrasts.append(r)
        self.table('group_contrasts',pd.DataFrame(contrasts))
        averaged=[]
        sources=[]
        pairs=[]
        for key,z in main.groupby(WK):
            model,target,crop,group=key
            self.check('three identical target conditions '+str(key), set(z.source)==set(SITES)-{target} and z.patch_set_sha256.nunique()==1 and z.within_f1.nunique(dropna=False)==1)
            base=z.within_f1.iloc[0]
            good=np.isfinite(z.cross_f1_mean).all()
            mean=float(z.cross_f1_mean.mean()) if good else np.nan
            averaged.append(dict(zip(WK,key),within_f1=base,cross_f1_mean=mean,delta_f1=base-mean if good and np.isfinite(base) else np.nan,n_sources=3,n_defined_sources=int(z.cross_f1_mean.notna().sum()),aggregation='equal_weight_three_sources'))
            if group not in ORDERED: continue
            rank=rank_string(z,'source','cross_f1_mean')
            r=dict(zip(WK,key),source_rank_cross_f1_desc=rank,source_f1_range=z.cross_f1_mean.max()-z.cross_f1_mean.min())
            for _,row in z.iterrows():
                r[row.source+'_cross_f1']=row.cross_f1_mean
                r[row.source+'_delta_f1']=row.delta_f1
            sources.append(r)
            for (_,a),(_,b) in itertools.combinations(z.sort_values('source').iterrows(),2):
                pairs.append(dict(zip(WK,key),source_a=a.source,source_b=b.source,cross_f1_a_minus_b=a.cross_f1_mean-b.cross_f1_mean,delta_a_minus_b=a.delta_f1-b.delta_f1))
        self.table('three_source_means',pd.DataFrame(averaged))
        source_table=pd.DataFrame(sources)
        self.table('source_comparisons',source_table)
        source_pairs=pd.DataFrame(pairs)
        self.check('source ranks reflect same difference', np.allclose(source_pairs.cross_f1_a_minus_b, -source_pairs.delta_a_minus_b,atol=1e-12,rtol=0))
        self.table('source_pair_differences',source_pairs)
        transitions=[]
        for key,z in source_table.groupby(['model','target','crop']):
            x=z.set_index('group')
            r=dict(zip(['model','target','crop'],key))
            for g in ORDERED:
                r[g+'_source_f1_range']=x.loc[g,'source_f1_range']
                r[g+'_source_rank']=x.loc[g,'source_rank_cross_f1_desc']
            r['high_minus_low_source_f1_range']=r['high_source_f1_range']-r['low_source_f1_range']
            r['source_rank_changes']=len({r[g+'_source_rank'] for g in ORDERED})>1
            r['range_trend']=trend([r[g+'_source_f1_range'] for g in ORDERED])
            transitions.append(r)
        self.table('source_group_changes',pd.DataFrame(transitions))
        models=[]
        model_pairs=[]
        for key,z in ordered.groupby(['source']+GK):
            self.check('three models same target group '+str(key),set(z.model)==set(MODELS) and z.patch_set_sha256.nunique()==1)
            x=z.set_index('model')
            r=dict(zip(['source']+GK,key),cross_f1_rank_desc=rank_string(z,'model','cross_f1_mean'),delta_rank_asc=rank_string(z,'model','delta_f1',False),cross_f1_range=z.cross_f1_mean.max()-z.cross_f1_mean.min(),delta_range=z.delta_f1.max()-z.delta_f1.min(),convgru_lowest_cross=bool(x.loc['convgru','cross_f1_mean']==z.cross_f1_mean.min()),convgru_smallest_delta=bool(x.loc['convgru','delta_f1']==z.delta_f1.min()))
            for m in MODELS:
                for field in FIELDS:r[m+'_'+field]=x.loc[m,field]
            models.append(r)
            for ma,mb in itertools.combinations(MODELS,2):
                model_pairs.append(dict(zip(['source']+GK,key),model_a=ma,model_b=mb,**{field+'_a_minus_b':x.loc[ma,field]-x.loc[mb,field] for field in FIELDS}))
        self.table('model_comparisons',pd.DataFrame(models))
        self.table('model_pair_differences',pd.DataFrame(model_pairs))
        comp_changes=[]
        for key,z in composition[composition.group.isin(ORDERED)].groupby(['target','crop']):
            x=z.set_index('group')
            r=dict(zip(['target','crop'],key))
            for field in [c+'_ratio' for c in CLASSES]+['feature_median','ED_median','AI_median']:
                for g in ORDERED:r[g+'_'+field]=x.loc[g,field]
                r['high_minus_low_'+field]=x.loc['high',field]-x.loc['low',field]
            comp_changes.append(r)
        self.table('composition_changes',pd.DataFrame(comp_changes))
        redundancy=[]
        for target,crop in itertools.product(SITES,CROPS):
            z=features.loc[features.dataset_id==target,[crop+'_AREA_MN',crop+'_AI']].dropna()
            redundancy.append(dict(target=target,crop=crop,n=len(z),spearman_rank_r=z.rank(method='average').corr().iloc[0,1]))
        self.table('area_ai_rank_redundancy',pd.DataFrame(redundancy))
        self.source_features(features,paths,ordered)

    def source_features(self,features,paths,ordered):
        land=self.read(paths['完整标签景观级指标.csv']).set_index('dataset_id')
        cls=self.read(paths['完整标签类别级指标.csv'])
        self.check('full-site class IDs', (cls.class_id.map({1:'corn',2:'other',3:'soybean'})==cls.class_name).all())
        totals=features.groupby('dataset_id')[[c+'_pixels' for c in CLASSES]].sum()
        rows=[]
        for _,r in cls.iterrows():
            self.check('full-site composition '+r.dataset_id+r.class_name, r.class_pixels==totals.loc[r.dataset_id,r.class_name+'_pixels'])
            if r.class_name not in CROPS:continue
            row=dict(site=r.dataset_id,crop=r.class_name,ED=land.loc[r.dataset_id,'ed_reported'],AREA_MN=r.area_mn_reported,AI=r.ai_reported)
            for crop in CLASSES:row[crop+'_ratio']=totals.loc[r.dataset_id,crop+'_pixels']/6553600
            rows.append(row)
        site=pd.DataFrame(rows)
        self.table('site_features',site)
        lookup=site.set_index(['site','crop'])
        fields=['ED','AREA_MN','AI','corn_ratio','soybean_ratio','other_ratio']
        diffs=[]
        for s,t in itertools.permutations(SITES,2):
            for crop,field in itertools.product(CROPS,fields):
                sv,tv=lookup.loc[(s,crop),field],lookup.loc[(t,crop),field]
                diffs.append(dict(source=s,target=t,crop=crop,site_feature=field,source_value=sv,target_value=tv,signed_source_minus_target=sv-tv,absolute_difference=abs(sv-tv)))
        diffs=pd.DataFrame(diffs)
        self.table('source_target_feature_differences',diffs)
        old=self.read(self.root/OLD_SUM/'source_target_feature_differences.csv')
        old['site_feature']=old.apply(lambda r:r.crop+'_ratio' if r.site_feature=='crop_ratio' else r.site_feature,axis=1)
        aligned=old.merge(diffs,on=['source','target','crop','site_feature'],suffixes=('_old','_new'),validate='one_to_one')
        self.check('legacy site differences within export precision', len(aligned)==len(old) and np.allclose(aligned.absolute_difference_old,aligned.absolute_difference_new,atol=1e-9,rtol=1e-10))
        idx=diffs.set_index(['source','target','crop','site_feature'])
        comparisons=[]
        for key,z in ordered.groupby(WK):
            model,target,crop,group=key
            for (_,a),(_,b) in itertools.combinations(z.sort_values('source').iterrows(),2):
                for field in fields:
                    da=idx.loc[(a.source,target,crop,field),'absolute_difference']
                    db=idx.loc[(b.source,target,crop,field),'absolute_difference']
                    fa,fb=a.cross_f1_mean,b.cross_f1_mean
                    outcome='invalid' if not np.isfinite([da,db,fa,fb]).all() else 'tie' if da==db or fa==fb else 'consistent' if (da-db)*(fa-fb)<0 else 'opposite'
                    comparisons.append(dict(zip(WK,key),source_a=a.source,source_b=b.source,site_feature=field,distance_a=da,distance_b=db,cross_f1_a=fa,cross_f1_b=fb,outcome=outcome))
        comparisons=pd.DataFrame(comparisons)
        self.table('source_feature_pair_comparisons',comparisons)
        self.table('source_feature_counts',comparisons.groupby(['target','crop','model','site_feature','outcome']).size().rename('descriptive_count').reset_index())


def trend(values):
    x=np.asarray(values,dtype=float)
    if not np.isfinite(x).all():return 'undefined'
    d=np.diff(x)
    return 'constant' if (d==0).all() else 'increasing' if (d>=0).all() else 'decreasing' if (d<=0).all() else 'nonmonotonic'


def rank_string(frame, identity, field, descending=True):
    if not np.isfinite(frame[field]).all():return 'undefined'
    groups=[]
    for _,z in frame.sort_values([field,identity],ascending=[not descending,True]).groupby(field,sort=False):
        groups.append('='.join(z[identity]))
    return '>'.join(groups) if descending else '<'.join(groups)


def protected_hashes(root):
    paths=[p for folder in [OLD_PROC,OLD_SUM,'sections','results/raw','results/summary/f1_raw_scale'] for p in (root/folder).glob('*') if p.is_file()]
    paths += [root/p for p in ['AGENTS.md','README.md','HANDOVER.md','plan/sec33-exploration-protocol.md','plan/experiment-protocol.md']]
    return {p.relative_to(root).as_posix():sha(p) for p in sorted(paths)}


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-only',action='store_true',help='Compute and check in memory; write nothing')
    args=parser.parse_args(argv)
    before=protected_hashes(ROOT)
    run=Run(ROOT).build()
    require(before==protected_hashes(ROOT),'protected inputs changed during run')
    for record in run.inputs.values():require(sha(record['path'])==record['sha256'],'input changed during calculation')
    print(json.dumps({'status':'Verified','checks':len(run.checks),'tables':{p:len(d) for p,d in run.tables.items()}},indent=2))
    if args.check_only:return
    manifest_path=ROOT/SUM/'run_manifest.json'
    script_record={'path':Path(__file__).resolve().as_posix(),'sha256':sha(__file__)}
    existing=[ROOT/p for p in run.tables if (ROOT/p).exists()]
    if manifest_path.exists():
        previous=json.loads(manifest_path.read_text(encoding='utf-8'))
        if previous['inputs']==list(run.inputs.values()) and previous['script']==script_record and set(previous['outputs'])==set(run.tables) and all((ROOT/p).exists() and sha(ROOT/p)==info['sha256'] for p,info in previous['outputs'].items()):
            print('Verified: existing products and manifest match; no files written.')
            return
    require(not existing and not manifest_path.exists(),'refusing to overwrite existing products; preserve and audit them first')
    outputs={}
    for rel,table in run.tables.items():
        dest=ROOT/rel
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('x',encoding='utf-8',newline='') as handle:
            table.to_csv(handle,index=False,float_format='%.17g',na_rep='NA',lineterminator='\n')
        outputs[rel]={'sha256':sha(dest),'rows':len(table)}
    manifest=dict(data_status='derived',analysis_status='exploratory',pipeline_status='Verified',spatial_metrics_status='Partially verified',spatial_metrics_limit='Existing feature tables checked against canonical exports; not recomputed from labels.',created_at_utc=datetime.now(timezone.utc).isoformat(),inputs=list(run.inputs.values()),script=script_record,outputs=outputs,protected_files=before,class_order=list(CLASSES),std_ddof=1,float_format='%.17g',csv_reader_float_precision='round_trip',difference='same-model same-target-group pooled OOF F1 minus mean of five separate cross F1 values',source_aggregation='equal weight of exactly three sources; no pooling of fifteen predictions',missing_policy='retain missing groups for closure; zero denominator NA; no restriction baseline>0',source_rank_identity='same baseline within model/target/group: cross F1 and delta rankings reverse, one finding',raw_directory_trace='exception-triggered only; no exception in this run',python_libraries={'numpy':np.__version__,'pandas':pd.__version__})
    with manifest_path.open('x',encoding='utf-8') as handle:json.dump(manifest,handle,ensure_ascii=False,indent=2)
    print('Saved new AREA_MN raw-scale exploration products; protected files unchanged.')


if __name__=='__main__':main()

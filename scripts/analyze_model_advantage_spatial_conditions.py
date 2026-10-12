"""Compare spatial omission advantages using saved counts; no inference/plots."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from sec33_metrics import BANDS, CLASSES, CM_COLS, RUN, SITE_LABELS, five_stats

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / 'results/processed/spatial_error_conditions'
OSUM = ROOT / 'results/summary/spatial_error_conditions'
REFINE = ROOT / 'results/processed/spatial_findings_refinement'
PROC = ROOT / 'results/processed/model_advantage_spatial_conditions'
OUT = ROOT / 'results/summary/model_advantage_spatial_conditions'
SNAPSHOT = PROC / 'prediction_identity_snapshot.json'
INDEX = ROOT / 'results/processed/sec33_reference_patch_types/prediction_count_index.csv'
AREA = ['<10', '10-<50', '50-<100', '100-<200', '200-<500', '>=500']
SHAPE = ['1-<1.5', '1.5-<2', '2-<3', '>=3']
DISTANCE = ['0<d<=1', '1<d<=6', 'd>6']
SMALL_TOTAL_RATE = 0.001  # 0.1 percentage point; not a significance threshold.
INPUTS, CHECKS, OUTPUTS = {}, [], []


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def register(path):
    INPUTS[Path(path).relative_to(ROOT).as_posix()] = sha(path)


def read(path):
    register(path)
    return pd.read_csv(path, float_precision='round_trip')


def save(frame, name, processed=False):
    path = (PROC if processed else OUT) / (name + '.csv')
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False, float_format='%.17g', lineterminator='\n')
    OUTPUTS.append(path)


def check(name, condition, detail=''):
    ok = bool(condition)
    CHECKS.append(dict(check=name, status='Verified' if ok else 'Not verified', detail=str(detail)))
    if not ok:
        raise ValueError(name + ': ' + str(detail))


def divide(a, b):
    a, b = np.broadcast_arrays(np.asarray(a, float), np.asarray(b, float))
    return np.divide(a, b, out=np.full(a.shape, np.nan), where=b != 0)


def summarize(frame, keys, values):
    rows = []
    for key, g in frame.groupby(keys, sort=True, dropna=False):
        if len(g) != 5 or set(g.fold) != {1, 2, 3, 4, 5}:
            raise ValueError(('five prediction identity', key))
        row = dict(zip(keys, key)) | {'n_predictions': 5}
        for v in values:
            row.update(five_stats(g[v], v))
        rows.append(row)
    return pd.DataFrame(rows)


def capture_provenance():
    if SNAPSHOT.exists():
        raise FileExistsError('Identity snapshot already exists; use the default read-only reuse.')
    index = pd.read_csv(INDEX)
    rows = []
    for r in index.itertuples(index=False):
        for fold in range(1, 6) if r.kind == 'within' else [r.fold]:
            base = Path(r.prediction_file).parent.parent / 'details' / f'fold_{fold}'
            jp, mp = base / 'test_patch_run.json', base / 'test_patch_metrics.csv'
            j = json.loads(jp.read_text(encoding='utf-8'))
            metadata = j if r.kind == 'within' else j['checkpoint_metadata']
            patches = pd.read_csv(mp, usecols=['patch_uid', 'fold_id']).sort_values('patch_uid')
            digest = hashlib.sha256(patches.to_csv(index=False, lineterminator='\n').encode()).hexdigest()
            rows.append(dict(kind=r.kind, model=r.model, source=r.source, target=r.target, fold=fold,
                recorded_model=j['model'], recorded_source=j['train_dataset_id'], recorded_target=j['eval_dataset_id'],
                experiment_fold=j['experiment_fold'], train_folds=metadata['train_folds'], val_fold=metadata['val_fold'],
                test_fold=metadata['test_fold'], checkpoint_fold=metadata.get('experiment_fold'),
                checkpoint=j['checkpoint'], checkpoint_sha256=metadata.get('checkpoint_sha256'),
                patch_count=len(patches), patch_uid_count=int(patches.patch_uid.nunique()),
                observed_patch_folds=sorted(map(int, patches.fold_id.unique())), membership_sha256=digest,
                aggregate_cm=j['aggregate_confusion_matrix'], source_json=str(jp), source_json_sha256=sha(jp),
                source_metrics=str(mp), source_metrics_sha256=sha(mp)))
    PROC.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(dict(data_status='derived_provenance_snapshot',
        captured_utc=datetime.now(timezone.utc).isoformat(), records=rows), ensure_ascii=False, indent=2)+'\n',
        encoding='utf-8', newline='\n')


def audit_identity(cm):
    register(SNAPSHOT)
    rows = json.loads(SNAPSHOT.read_text(encoding='utf-8'))['records']
    d = pd.DataFrame(rows)
    check('240 actual run identities', len(d) == 240 and not d.duplicated(RUN).any())
    check('run declared identities', d.model.eq(d.recorded_model).all() and d.source.eq(d.recorded_source).all()
          and d.target.eq(d.recorded_target).all() and d.fold.eq(d.experiment_fold).all()
          and d.fold.eq(d.checkpoint_fold).all())
    within = d[d.kind.eq('within')].set_index(['model', 'source', 'fold'])
    expected = [([1, 2, 3], 4, 5), ([2, 3, 4], 5, 1), ([3, 4, 5], 1, 2),
                ([4, 5, 1], 2, 3), ([5, 1, 2], 3, 4)]
    cms = cm.set_index(RUN)
    for (source, fold), g in d[d.kind.eq('within')].groupby(['source', 'fold']):
        check(f'model test membership {source} {fold}', len(g) == 3 and g.membership_sha256.nunique() == 1
              and g.patch_count.eq(80).all() and g.patch_uid_count.eq(80).all())
    for r in d.itertuples(index=False):
        check(f'split and membership {r.kind} {r.model} {r.source} {r.target} {r.fold}',
              (r.train_folds, r.val_fold, r.test_fold) == expected[r.fold-1] and
              r.observed_patch_folds == ([r.test_fold] if r.kind == 'within' else [1, 2, 3, 4, 5]))
        if r.kind == 'cross':
            w = within.loc[(r.model, r.source, r.fold)]
            check(f'source pairing {r.model} {r.source} {r.target} {r.fold}',
                  (r.train_folds, r.val_fold, r.test_fold) == (w.train_folds, w.val_fold, w.test_fold)
                  and r.patch_count == r.patch_uid_count == 400)
            truth = cms.loc[('cross', r.model, r.source, r.target, r.fold), CM_COLS].to_numpy(np.int64)
            check(f'run CM {r.model} {r.source} {r.target} {r.fold}',
                  np.array_equal(np.asarray(r.aggregate_cm).ravel(), truth))
    for (model, target), g in d[d.kind.eq('within')].groupby(['model', 'target']):
        check(f'within pooled CM {model} {target}', np.array_equal(np.stack(g.aggregate_cm).sum(axis=0).ravel(),
              cms.loc[('within', model, target, target, 0), CM_COLS].to_numpy(np.int64)))
    for target, g in d[d.kind.eq('cross')].groupby('target'):
        check(f'identical full target membership {target}', g.membership_sha256.nunique() == 1)
    out = d.drop(columns=['aggregate_cm']).copy()
    for col in ['train_folds', 'observed_patch_folds']:
        out[col] = out[col].map(lambda v: ','.join(map(str, v)))
    out['pairing_status'] = 'Verified'
    save(out, 'prediction_identity_audit')


def model_pairs(frame, dimensions, values):
    keys = ['kind', 'source', 'target', 'fold'] + dimensions
    base = frame[frame.model.eq('convgru')][keys+values]
    rows = []
    for model in ['utae', 'unet3d']:
        other = frame[frame.model.eq(model)][keys+values]
        m = base.merge(other, on=keys, validate='one_to_one', suffixes=('_convgru', '_other_model'))
        check(f'complete paired {model} {dimensions}', len(m) == len(base) == len(other))
        m['comparison_model'] = model
        rows.append(m)
    return pd.concat(rows, ignore_index=True)


def add_pair_baselines(pairs, dimensions, values):
    keys = ['comparison_model', 'target'] + dimensions
    baseline = pairs[pairs.kind.eq('within')][keys+values].rename(columns={v:'within_'+v for v in values})
    return pairs.merge(baseline, on=keys, validate='many_to_one')


def group_advantages(groups, whole):
    keep = ['all', 'distance', 'area_shape']
    cols = RUN+['crop', 'scheme', 'group', 'reference_pixels', 'patch_count', 'fn', 'to_other', 'to_other_crop']
    g = groups[groups.scheme.isin(keep)][cols].copy()
    three = g[g.scheme.eq('distance')].copy()
    three['scheme'] = 'distance_three'
    three['group'] = three.group.map(lambda v: v if v in ['0<d<=1', 'd>6'] else '1<d<=6')
    # A patch may touch several original bands; do not sum patch support across bands.
    three = three.groupby(RUN+['crop','scheme','group'], as_index=False)[['reference_pixels','fn','to_other','to_other_crop']].sum()
    three['patch_count'] = np.nan
    g = pd.concat([g, three], ignore_index=True)
    g['omission_rate'] = divide(g.fn, g.reference_pixels)
    g['to_other_rate'] = divide(g.to_other, g.reference_pixels)
    g['to_other_crop_rate'] = divide(g.to_other_crop, g.reference_pixels)
    linked = g[g.scheme.eq('all')].merge(whole[RUN+['crop','pixels','fn']], on=RUN+['crop'],
                                       validate='one_to_one', suffixes=('','_whole'))
    check('all groups recover independently verified whole crop', len(linked)==384 and
          linked.reference_pixels.eq(linked.pixels).all() and linked.fn.eq(linked.fn_whole).all())
    dimensions = ['crop', 'scheme', 'group']
    vals = ['reference_pixels', 'patch_count', 'fn', 'omission_rate', 'to_other', 'to_other_crop']
    p = model_pairs(g, dimensions, vals)
    check('paired reference supports equal', p.reference_pixels_convgru.eq(p.reference_pixels_other_model).all())
    p['reference_pixels'] = p.reference_pixels_convgru
    p['patch_count'] = p.patch_count_convgru
    p = p.drop(columns=['reference_pixels_convgru','reference_pixels_other_model','patch_count_convgru','patch_count_other_model'])
    p['net_fewer_pixels'] = p.fn_convgru-p.fn_other_model
    p['advantage'] = p.omission_rate_convgru-p.omission_rate_other_model
    p['net_to_other'] = p.to_other_convgru-p.to_other_other_model
    p['net_to_other_crop'] = p.to_other_crop_convgru-p.to_other_crop_other_model
    bvals = ['advantage','net_fewer_pixels','omission_rate_convgru','omission_rate_other_model']
    p = add_pair_baselines(p, dimensions, bvals)
    p['advantage_change'] = p.advantage-p.within_advantage
    for model in ['convgru','other_model']:
        p['error_increment_'+model] = p['omission_rate_'+model]-p['within_omission_rate_'+model]
    check('advantage change equals differential increments', np.allclose(p.advantage_change,
        p.error_increment_convgru-p.error_increment_other_model, equal_nan=True, atol=1e-14, rtol=0))
    wk = ['kind','comparison_model','source','target','fold','crop']
    totals = p[p.scheme.eq('all')][wk+['reference_pixels','net_fewer_pixels']].rename(
        columns={'reference_pixels':'whole_crop_pixels','net_fewer_pixels':'whole_net_fewer_pixels'})
    p = p.merge(totals, on=wk, validate='many_to_one')
    p['area_ha'] = p.reference_pixels*.09
    p['area_share'] = p.reference_pixels/p.whole_crop_pixels
    p['whole_rate_contribution'] = p.net_fewer_pixels/p.whole_crop_pixels
    p['contribution_status'] = np.where(abs(p.whole_net_fewer_pixels/p.whole_crop_pixels)<SMALL_TOTAL_RATE,
                                        'near_zero_total_do_not_rank','defined_signed_net_share')
    p['net_reduction_share'] = divide(p.net_fewer_pixels,p.whole_net_fewer_pixels)
    p.loc[p.contribution_status.eq('near_zero_total_do_not_rank'),'net_reduction_share'] = np.nan
    for (key, sub) in p.groupby(wk+['scheme']):
        check('group closure '+str(key), sub.reference_pixels.sum()==sub.whole_crop_pixels.iloc[0] and
              sub.net_fewer_pixels.sum()==sub.whole_net_fewer_pixels.iloc[0] and
              (sub.net_to_other+sub.net_to_other_crop).eq(sub.net_fewer_pixels).all())
    save(p,'group_advantage_per_prediction',True)
    save(p[p.kind.eq('within')],'within_group_advantages')
    values = ['omission_rate_convgru','omission_rate_other_model','advantage','advantage_change',
        'error_increment_convgru','error_increment_other_model','net_fewer_pixels','whole_rate_contribution',
        'net_reduction_share','net_to_other','net_to_other_crop']
    keys=['comparison_model','source','target']+dimensions
    cross=summarize(p[p.kind.eq('cross')],keys,values)
    fixed=['reference_pixels','patch_count','area_ha','area_share','whole_crop_pixels']+['within_'+v for v in bvals]
    cross=cross.merge(p[keys+fixed].drop_duplicates(),on=keys,validate='one_to_one')
    whole_net=cross[cross.scheme.eq('all')][['comparison_model','source','target','crop','net_fewer_pixels_mean']].rename(
        columns={'net_fewer_pixels_mean':'whole_net_fewer_pixels_mean'})
    cross=cross.merge(whole_net,on=['comparison_model','source','target','crop'],validate='many_to_one')
    cross['ratio_of_mean_net_reduction']=divide(cross.net_fewer_pixels_mean,cross.whole_net_fewer_pixels_mean)
    small=abs(cross.whole_net_fewer_pixels_mean/cross.whole_crop_pixels)<SMALL_TOTAL_RATE
    cross.loc[small,'ratio_of_mean_net_reduction']=np.nan
    cross['mean_contribution_status']=np.where(small,'near_zero_total_do_not_rank','defined_signed_net_share')
    save(cross,'cross_group_advantages')
    save(cross[cross.scheme.eq('all')],'cross_path_overview')
    modelcols=RUN+dimensions+['reference_pixels','fn','omission_rate']
    save(g[modelcols],'model_group_rates_per_prediction',True)
    return p,cross


def conditional_advantages(groups):
    x=groups[groups.scheme.eq('area_shape_distance')].copy()
    parts=x.group.str.split('|',expand=True)
    x['a']=parts[0].map(dict(zip(AREA,range(6))))
    x['s']=parts[1].map(dict(zip(SHAPE,range(4))))
    x['d']=parts[2].map(dict(zip(DISTANCE,range(3))))
    original_weights=read(OSUM/'conditional_support_weights.csv')
    allrates=[];allweights=[];allcoverage=[]
    for contrast,controls,armcol,cut in [('area_control_shape_distance','s','a',2),
                                       ('shape_control_area_distance','a','s',2)]:
        z=x.copy();z['arm']=(z[armcol]>=cut).astype(int);z['stratum']=z[controls]*3+z.d
        z=z.groupby(RUN+['crop','arm','stratum'],as_index=False)[['reference_pixels','patch_count','fn']].sum()
        ref=z[z.kind.eq('within')&z.model.eq('convgru')][['target','crop','arm','stratum','reference_pixels','patch_count']]
        for (target,crop),support in ref.groupby(['target','crop']):
            for rule in ['primary','all_supported']:
                old=original_weights[(original_weights.target==target)&(original_weights.crop==crop)&
                      (original_weights.contrast_name==contrast)&(original_weights.rule==rule)].copy()
                weights=[]
                for arm,side in [(0,'low'),(1,'high')]:
                    r=support[support.arm.eq(arm)].merge(old,on=['target','crop','stratum'],validate='one_to_one')
                    check(f'reuse conditional support {target} {crop} {contrast} {rule} {arm}',
                          r.reference_pixels.eq(r[side+'_pixels']).all() and r.patch_count.eq(r[side+'_patch_count']).all())
                    r['contrast_name']=contrast;r['arm']=arm;r['control_bin']=r.stratum//3
                    r['weight_distance_equal']=r.common_weight
                    mass=r.groupby('control_bin').common_weight.transform('sum')
                    included=r.reference_pixels.where(r.eligible,0)
                    control_pixels=included.groupby(r.control_bin).transform('sum')
                    r['weight_distance_native']=np.where(r.eligible,mass*divide(included,control_pixels),0)
                    check(f'same support outer weights {target} {crop} {contrast} {rule} {arm}',
                          abs(r.weight_distance_equal.sum()-1)<1e-12 and abs(r.weight_distance_native.sum()-1)<1e-12
                          and np.allclose(r.groupby('control_bin').weight_distance_equal.sum(),
                                          r.groupby('control_bin').weight_distance_native.sum(),atol=1e-14,rtol=0))
                    total=int(r.reference_pixels.sum());kept=int(r.loc[r.eligible,'reference_pixels'].sum())
                    allcoverage.append(dict(target=target,crop=crop,contrast_name=contrast,rule=rule,arm=arm,
                        total_pixels=total,retained_pixels=kept,excluded_pixels=total-kept,coverage=kept/total,
                        eligible_strata=int(r.eligible.sum()),total_strata=len(r)))
                    weights.append(r[['target','crop','contrast_name','rule','arm','stratum','control_bin','reference_pixels',
                        'patch_count','eligible','weight_distance_equal','weight_distance_native']])
                w=pd.concat(weights,ignore_index=True);allweights.append(w)
                zz=z[(z.target==target)&(z.crop==crop)].merge(w,on=['target','crop','arm','stratum'],validate='many_to_one',suffixes=('','_weight'))
                zz=zz[zz.eligible].copy()
                for mode in ['distance_native','distance_equal']:
                    zz['value']=zz.fn/zz.reference_pixels*zz['weight_'+mode]
                    rates=zz.groupby(RUN+['crop','arm'],as_index=False).value.sum()
                    rates['contrast_name']=contrast;rates['rule']=rule;rates['distance_mode']=mode
                    allrates.append(rates)
    rates=pd.concat(allrates,ignore_index=True).rename(columns={'value':'rate'})
    dims=['crop','contrast_name','rule','distance_mode','arm']
    p=model_pairs(rates,dims,['rate']);p['advantage']=p.rate_convgru-p.rate_other_model
    p=add_pair_baselines(p,dims,['rate_convgru','rate_other_model','advantage'])
    p['advantage_change']=p.advantage-p.within_advantage
    for model in ['convgru','other_model']:
        p['error_increment_'+model]=p['rate_'+model]-p['within_rate_'+model]
    save(rates,'conditional_model_rates_per_prediction',True)
    save(p,'conditional_advantage_per_prediction',True)
    keys=['kind','comparison_model','source','target','fold']+dims[:-1]
    lo=p[p.arm.eq(0)].set_index(keys);hi=p[p.arm.eq(1)].set_index(keys).loc[lo.index]
    contrast=lo.index.to_frame(index=False)
    for v in ['advantage','within_advantage','advantage_change']:
        contrast['low_'+v]=lo[v].values;contrast['high_'+v]=hi[v].values
        contrast['high_minus_low_'+v]=hi[v].values-lo[v].values
    save(contrast,'conditional_contrast_per_prediction',True)
    save(p[p.kind.eq('within')],'within_conditional_advantages')
    save(contrast[contrast.kind.eq('within')],'within_conditional_contrasts')
    cv=['rate_convgru','rate_other_model','advantage','advantage_change','error_increment_convgru','error_increment_other_model']
    save(summarize(p[p.kind.eq('cross')],['comparison_model','source','target']+dims,cv),'cross_conditional_advantages')
    vals=[c for c in contrast if c not in keys]
    save(summarize(contrast[contrast.kind.eq('cross')],['comparison_model','source','target']+dims[:-1],vals),
         'cross_conditional_contrasts')
    save(pd.concat(allweights,ignore_index=True),'same_support_weights')
    save(pd.DataFrame(allcoverage),'conditional_coverage')
    # Match existing adjusted results while calculating the model difference explicitly.
    old=read(OLD/'conditional_contrasts_per_prediction.csv')
    eq=rates[rates.distance_mode.eq('distance_equal')].pivot(index=RUN+['crop','contrast_name','rule'],columns='arm',values='rate')
    test=eq.reset_index().merge(old,on=RUN+['crop','contrast_name','rule'],validate='one_to_one')
    check('reproduce existing adjusted absolute rates',np.allclose(test[0],test.low_standard_rate,atol=1e-12,rtol=0)
          and np.allclose(test[1],test.high_standard_rate,atol=1e-12,rtol=0))
    return contrast


def refined_CD_bridge():
    f=read(REFINE/'standardized_rates_per_prediction.csv')
    f=f[(f.scheme=='a12d7')&(f.scope=='joint_CD')&(f.rule=='primary')].copy()
    vals=['low_omission','high_omission','gap_omission','delta_gap_omission']
    p=model_pairs(f,[],vals)
    p['low_advantage']=p.low_omission_convgru-p.low_omission_other_model
    p['high_advantage']=p.high_omission_convgru-p.high_omission_other_model
    p['high_minus_low_advantage']=p.high_advantage-p.low_advantage
    p=add_pair_baselines(p,[],['low_advantage','high_advantage','high_minus_low_advantage'])
    for v in ['low_advantage','high_advantage','high_minus_low_advantage']:
        p['change_'+v]=p[v]-p['within_'+v]
    check('CD model difference versus previous shape increments',np.allclose(p.change_high_minus_low_advantage,
        p.delta_gap_omission_convgru-p.delta_gap_omission_other_model,atol=1e-14,rtol=0))
    save(p,'refined_CD_bridge_per_prediction',True)
    save(summarize(p[p.kind.eq('cross')],['comparison_model','source','target'],
        ['low_advantage','high_advantage','high_minus_low_advantage','change_high_minus_low_advantage']), 'refined_CD_bridge')


def whole_context(whole,cm):
    for row in cm.itertuples(index=False):
        ident=tuple(getattr(row,k) for k in RUN)
        m=np.array([getattr(row,c) for c in CM_COLS]).reshape(3,3)
        truth=whole.set_index(RUN+['crop'])
        for c,crop in enumerate(CLASSES):
            r=truth.loc[ident+(crop,)]
            tp=m[c,c];fn=m[c,:].sum()-tp;fp=m[:,c].sum()-tp
            check('complete matrix and F1 '+str(ident+(crop,)),(r.tp,r.fn,r.fp)==(tp,fn,fp)
                  and abs(r.f1-2*tp/(2*tp+fn+fp))<1e-12)
    for kind,path,keys in [('within','within_site_crop_f1.csv',['model','target']),
                           ('cross','cross_site_crop_f1_per_fold.csv',['model','source','target','fold'])]:
        official=read(ROOT/'results/summary/f1_raw_scale'/path)
        w=whole[whole.kind.eq(kind)]
        for crop in ['corn','soybean']:
            t=w[w.crop.eq(crop)].merge(official,on=keys,validate='one_to_one')
            check('official F1 '+kind+crop,np.allclose(t.f1,t[crop+'_f1'],atol=1e-12,rtol=0))
    save(whole,'complete_class_context_per_prediction',True)
    crop=whole[whole.crop.isin(['corn','soybean'])]
    p=model_pairs(crop,['crop'],['f1','fn','fp','leakage','delta_f1'])
    p['f1_advantage']=p.f1_other_model-p.f1_convgru
    p['omission_advantage']=p.leakage_convgru-p.leakage_other_model
    p['fp_net_fewer']=p.fp_convgru-p.fp_other_model
    p=add_pair_baselines(p,['crop'],['f1_advantage','omission_advantage'])
    p['f1_advantage_change']=p.f1_advantage-p.within_f1_advantage
    save(p,'complete_model_comparison_per_prediction',True)
    save(summarize(p[p.kind.eq('cross')],['comparison_model','source','target','crop'],
        ['f1_convgru','f1_other_model','f1_advantage','f1_advantage_change','fp_net_fewer','delta_f1_convgru','delta_f1_other_model']),
        'complete_F1_comparisons')


def reading_table(p,cross,contrasts):
    rows=[]
    w=p[p.kind.eq('within')]
    for r in w[w.scheme.eq('all')].itertuples(index=False):
        ident=dict(target=r.target,crop=r.crop,comparison_model=r.comparison_model)
        sub=w[(w.target==r.target)&(w.crop==r.crop)&(w.comparison_model==r.comparison_model)]
        joint=sub[sub.scheme.eq('area_shape')].sort_values('net_fewer_pixels',ascending=False)
        top=joint.iloc[0];three=joint.head(3)
        bands=sub[sub.scheme.eq('distance_three')].set_index('group')
        paths=cross[(cross.target==r.target)&(cross.crop==r.crop)&(cross.comparison_model==r.comparison_model)&cross.scheme.eq('all')]
        row=ident|dict(site=SITE_LABELS[r.target],convgru_omission=r.omission_rate_convgru,
            other_omission=r.omission_rate_other_model,within_advantage=r.advantage,net_fewer_pixels=r.net_fewer_pixels,
            nearest_area_share=bands.loc['0<d<=1','area_share'],nearest_net_share=bands.loc['0<d<=1','net_reduction_share'],
            middle_net_share=bands.loc['1<d<=6','net_reduction_share'],far_net_share=bands.loc['d>6','net_reduction_share'],
            top_joint_group=top['group'],top_joint_area_share=top.area_share,top_joint_net_share=top.net_reduction_share,
            top3_joint_groups=';'.join(three.group),top3_joint_net_share=three.net_reduction_share.sum(),
            cross_positive_paths=int(paths.advantage_mean.gt(0).sum()),cross_all5_positive_paths=int(paths.advantage_positive.eq(5).sum()),
            cross_expanded_paths=int(paths.advantage_change_mean.gt(0).sum()),cross_reversed_paths=int(paths.advantage_mean.lt(0).sum()),
            cross_advantage_min=paths.advantage_mean.min(),cross_advantage_max=paths.advantage_mean.max())
        c=contrasts[(contrasts.kind=='within')&(contrasts.target==r.target)&(contrasts.crop==r.crop)&
                    (contrasts.comparison_model==r.comparison_model)&(contrasts.rule=='primary')]
        for name,short in [('area_control_shape_distance','area'),('shape_control_area_distance','shape')]:
            for mode in ['distance_native','distance_equal']:
                row[short+'_'+mode+'_gain_contrast']=float(c[(c.contrast_name==name)&(c.distance_mode==mode)].high_minus_low_advantage.iloc[0])
        rows.append(row)
    main=pd.DataFrame(rows).sort_values(['site','crop','comparison_model'])
    save(main,'main_reading_table')
    text=['# 模型漏分优势精简主表', '',
          '优势为ConvGRU漏分率减相应模型漏分率，单位为百分点；正值表示该模型少漏分。最近带份额的分母为全作物净减少量。联合格为本站净减少最多的一格，括号内为净减少份额。跨站范围为同目标三来源的五次均值范围。保持栏为“均值优势为正的来源数 / 五次优势均为正的来源数”，总来源数均为3。', '',
          '| 站点、作物 | 对照模型 | 本站优势/百分点 | 最近带净减少份额 | 最大贡献联合格：AREA/ha、SHAPE | 跨站优势范围/百分点 | 保持来源数 |',
          '|---|---|---:|---:|---|---:|---:|']
    for r in main.itertuples(index=False):
        crop={'corn':'玉米','soybean':'大豆'}[r.crop]
        model={'utae':'U-TAE','unet3d':'3D U-Net'}[r.comparison_model]
        text.append(f'| {r.site}{crop} | {model} | {r.within_advantage*100:.2f} | {r.nearest_net_share*100:.2f}% | '
                    f'{r.top_joint_group.replace("|", " / ")}（{r.top_joint_net_share*100:.2f}%） | '
                    f'{r.cross_advantage_min*100:+.2f}～{r.cross_advantage_max*100:+.2f} | '
                    f'{r.cross_positive_paths} / {r.cross_all5_positive_paths} |')
    text += ['', '各组参考支持、净像元、负贡献及五次结果见[完整本站表](within_group_advantages.csv)、[跨站路径表](cross_path_overview.csv)。同支持面积/形状对照与其它主表字段见[CSV](main_reading_table.csv)。本表仅为真实作物漏分比较，不代表完整F1优劣。', '']
    path=OUT/'main_reading_table.md';path.write_text('\n'.join(text),encoding='utf-8',newline='\n');OUTPUTS.append(path)
    top=w[w.scheme.eq('area_shape')].copy()
    top['net_rank']=top.groupby(['target','crop','comparison_model']).net_fewer_pixels.rank(method='min',ascending=False)
    save(top[top.net_rank.le(3)],'within_top_joint_cells')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--capture-provenance',action='store_true');args=parser.parse_args()
    if args.capture_provenance:capture_provenance()
    cm=read(ROOT/'results/processed/sec33_crop_spatial_context/whole_cm.csv')
    audit_identity(cm)
    groups=read(OLD/'group_metrics_per_prediction.csv')
    whole=read(OLD/'whole_crop_per_prediction.csv')
    whole_context(whole,cm)
    p,cross=group_advantages(groups,whole)
    contrasts=conditional_advantages(groups)
    refined_CD_bridge();reading_table(p,cross,contrasts)
    for path in ['legacy/manuscript/HLS-Crop/src/learning/distance_band_analysis.py',
                 'legacy/manuscript/HLS-Crop/train_semantic.py','legacy/manuscript/HLS-Crop/src/learning/batch_cross_site.py']:
        register(ROOT/path)
    save(pd.DataFrame(CHECKS),'verification_checks')
    config=dict(data_status='derived_exploratory',date_client='2026-10-13',advantage='ConvGRU omission minus comparison model omission',
        small_total_rate=SMALL_TOTAL_RATE,paired_by='same source training/validation/test split and target; not random initialization',
        area_bins=AREA,shape_bins=SHAPE,distance_bands=list(BANDS),conditional_distance_bands=DISTANCE,
        same_support_comparison='fixed eligible area/shape-distance cells and outer weights; vary only within-control distance weights',
        no_significance_or_causal_inference=True)
    cfg=OUT/'analysis_config.json';cfg.write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8',newline='\n');OUTPUTS.append(cfg)
    manifest=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs=INPUTS,outputs={p.relative_to(ROOT).as_posix():sha(p) for p in OUTPUTS},script_sha256=sha(__file__),
        verification='Verified',scope='saved count model comparisons, run pairing snapshot, common supports; no distance transform rerun')
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Saved {len(OUTPUTS)} result files; {len(CHECKS)} checks.',flush=True)


if __name__=='__main__':
    main()

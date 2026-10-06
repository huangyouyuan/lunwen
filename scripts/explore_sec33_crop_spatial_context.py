#!/usr/bin/env python3
"""Derived micro-spatial analysis; reads saved predictions, never runs inference.

Stages: prepare (feature-only rules and reference assets), count, analyze,
diagnose (independent closure and scientific contrasts), seal (delivery hashes).
Historical inputs and manuscript files are immutable. See task and dictionary.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from scipy.optimize import linear_sum_assignment

import explore_sec33_round3_distance as base
from calculate_crop_f1 import within_site_file

ROOT = Path(__file__).resolve().parents[1]
NAME = 'sec33_crop_spatial_context'
PROC = ROOT / 'results/processed' / NAME
SUM = ROOT / 'results/summary' / NAME
FIG = ROOT / 'figures/exploratory' / NAME
SITES, MODELS, CLASSES, BANDS = base.SITES, base.MODELS, base.CLASSES, base.BANDS
CM = base.CM
PAIRS = {'corn_other': (1, 0, 1), 'corn_soybean': (2, 0, 2), 'other_soybean': (4, 1, 2)}
RUNKEY = ['kind', 'model', 'source', 'target', 'fold']
INPUTS, CHECKS = {}, []


def require(ok, message):
    if not bool(ok):
        raise ValueError(message)


def record(path, role='input'):
    p = Path(path).resolve()
    h = hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    rec = dict(path=p.as_posix(), sha256=h.hexdigest(), bytes=p.stat().st_size, role=role)
    INPUTS[p.as_posix()] = rec
    return p


def read(path):
    return pd.read_csv(record(path), float_precision='round_trip', encoding='utf-8-sig')


def jread(path):
    return json.loads(record(path).read_text(encoding='utf-8-sig'))


def save(frame, name, processed=False):
    path = (PROC if processed else SUM) / (name + '.csv')
    base.write_csv(path, frame)


def check(name, ok, detail=''):
    CHECKS.append(dict(check=name, status='Verified' if ok else 'Not verified', detail=str(detail)))
    require(ok, name + ': ' + str(detail))


def finish(stage):
    SUM.mkdir(parents=True, exist_ok=True)
    save(pd.DataFrame(CHECKS), stage + '_checks')
    out = dict(created_at_utc=datetime.now(timezone.utc).isoformat(), data_status='derived',
               analysis_status='exploratory', distance_generation_status='Partially verified',
               distance_transform_rerun=False, stage=stage, inputs=list(INPUTS.values()))
    record(Path(__file__), 'script')
    out['inputs'] = list(INPUTS.values())
    (SUM / (stage + '_manifest.json')).write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def strict_stats(values, folds):
    a = np.asarray(values, dtype=float)
    require(len(a) == 5 and set(folds) == set(range(1, 6)), 'five explicit predictions required')
    good = np.isfinite(a)
    return dict(mean=float(a.mean()) if good.all() else np.nan,
                std=float(a.std(ddof=1)) if good.all() else np.nan,
                min=float(a.min()) if good.all() else np.nan,
                max=float(a.max()) if good.all() else np.nan, n_valid=int(good.sum()),
                n_positive=int((good & (a > 0)).sum()), n_negative=int((good & (a < 0)).sum()), n_zero=int((good & (a == 0)).sum()),
                direction=('not_calculable' if not good.all() else 'all_positive' if (a > 0).all()
                           else 'all_negative' if (a < 0).all() else 'all_zero' if (a == 0).all() else 'mixed'))


def class_metrics(cm, c):
    n, p, tp = int(cm[c].sum()), int(cm[:, c].sum()), int(cm[c, c])
    z = n + p
    return dict(pixels=n, predicted_pixels=p, tp=tp, fn=n-tp, fp=p-tp,
                f1=2*tp/z if z else np.nan, precision=tp/p if p else np.nan,
                recall=tp/n if n else np.nan, leakage=(n-tp)/n if n else np.nan,
                fn_component=(n-tp)/z if z else np.nan, fp_component=(p-tp)/z if z else np.nan)


def cm_of(row):
    return np.asarray([row[k] for k in CM], dtype=np.int64).reshape(3, 3)


def rows_cm(cm):
    return dict(zip(CM, np.asarray(cm).reshape(-1).astype(int)))


def matching(left, right, covariates, tolerances, logarithmic=False):
    """Max-cardinality one-to-one matches, then minimum feature distance; no outcomes."""
    left, right = left.sort_values('patch_id'), right.sort_values('patch_id')
    a, b = left[covariates].to_numpy(), right[covariates].to_numpy()
    dif = abs(np.log(a[:, None, :] / b[None, :, :])) if logarithmic else abs(a[:, None, :] - b[None, :, :])
    norm = dif / np.asarray(tolerances)
    eligible = np.isfinite(norm).all(2) & (norm <= 1).all(2)
    cost = np.where(eligible, norm.sum(2), 1e6)
    i, j = linear_sum_assignment(cost)
    keep = eligible[i, j]
    return left.iloc[i[keep]].reset_index(drop=True), right.iloc[j[keep]].reset_index(drop=True), int(eligible.sum())


def external_tables():
    m = jread(ROOT / 'results/summary/sec33_exploration/run_manifest.json')
    return {Path(x['windows_path']).name: Path(x['windows_path']) for x in m['inputs']}


def prepare():
    require(not (PROC / 'reference_iw_2023.npz').exists(), 'prepare already exists; reuse rather than overwrite')
    PROC.mkdir(parents=True, exist_ok=True)
    f = read(external_tables()['patch_spatial_features.csv']).sort_values(['dataset_id', 'patch_id'])
    check('feature identity', len(f) == 1600 and not f.patch_uid.duplicated().any())
    save(f, 'patch_features', True)
    groups = read(ROOT / 'results/processed/sec33_exploration/patch_groups.csv')
    groups = groups[groups.metric.eq('AREA_MN')].copy()
    save(groups, 'frozen_area_assignments', True)
    # Freeze both limited contrasts using reference features only, before counting errors.
    d = f[f.dataset_id.eq('il_2023') & f.soybean_AREA_MN.gt(0)].merge(
        groups[groups.target.eq('il_2023') & groups.crop.eq('soybean')][['patch_uid', 'group']],
        on='patch_uid', validate='one_to_one')
    qs = d.other_ratio.quantile([1/3, 2/3]).to_numpy()
    specs = [
        ('area_at_close_composition', d[d.group.eq('low')], d[d.group.eq('high')],
         ['corn_ratio','soybean_ratio'], [.05,.05], False, 'AREA_low', 'AREA_high'),
        ('composition_at_close_area', d[d.other_ratio <= qs[0]], d[d.other_ratio > qs[1]],
         ['soybean_AREA_MN'], [np.log(1.10)], True, 'other_low', 'other_high')]
    matches, rules, features = [], [], []
    for name, left, right, cov, tol, log, ln, rn in specs:
        a,b,candidates = matching(left,right,cov,tol,log)
        rules.append(dict(contrast=name,target='il_2023',crop='soybean',left_group=ln,right_group=rn,
                          left_candidates=len(left),right_candidates=len(right),eligible_pairs=candidates,
                          selected_pairs=len(a),covariates=';'.join(cov),tolerances=json.dumps(tol),
                          logarithmic=log,other_q1=qs[0],other_q2=qs[1],minimum_pairs=10))
        for i in range(len(a)):
            item=dict(contrast=name,pair_id=i,target='il_2023',left_patch_id=int(a.iloc[i].patch_id),
                      right_patch_id=int(b.iloc[i].patch_id),left_patch_uid=a.iloc[i].patch_uid,
                      right_patch_uid=b.iloc[i].patch_uid)
            for field in ['corn_ratio','soybean_ratio','other_ratio','soybean_AREA_MN','ED','soybean_AI']:
                item['left_'+field]=a.iloc[i][field];item['right_'+field]=b.iloc[i][field]
            matches.append(item)
        for side, z in [('left',a),('right',b)]:
            for field in ['corn_ratio','soybean_ratio','other_ratio','soybean_AREA_MN','ED','soybean_AI']:
                features.append(dict(contrast=name,side=side,feature=field,patches=len(z),
                                     min=z[field].min(),median=z[field].median(),max=z[field].max(),mean=z[field].mean()))
    save(pd.DataFrame(matches),'fixed_matches',True)
    save(pd.DataFrame(rules),'comparison_rules')
    save(pd.DataFrame(features),'matched_feature_distributions')
    groot = next(Path('G:/').glob('2560*'))
    summaries=[]; assets=[]
    for target in SITES:
        short=target.split('_')[0]; ds=groot/f'20{short}'/f'2023{short}shuju'
        meta=read(ds/'metadata.csv').sort_values('patch_id')
        check('reference metadata '+target, meta.patch_id.tolist()==list(range(400)) and meta.dataset_id.eq(target).all())
        check('grid '+target, (meta.tile_row==meta.patch_id//20).all() and (meta.tile_col==meta.patch_id%20).all()
              and (meta.x_offset_pixel==128*meta.tile_col).all() and (meta.y_offset_pixel==128*meta.tile_row).all()
              and meta.overlap.eq(0).all() and meta.crs_epsg.eq(5070).all())
        label=np.empty((400,128,128),np.uint8); pair=np.empty_like(label)
        for row in meta.itertuples():
            pid=int(row.patch_id)
            raw=np.load(record(ds/'ANNOTATIONS'/f'TARGET_{pid}.npy','reference label'),allow_pickle=False)
            boundary=np.load(record(ds/'BOUNDARIES'/f'BOUNDARY_{pid}.npy','existing direct boundary'),allow_pickle=False)
            bits=np.load(record(ds/'BOUNDARY_PAIRS'/f'BOUNDARY_PAIR_{pid}.npy','existing boundary type bitmask'),allow_pickle=False)
            require(raw.shape==(3,128,128) and raw.dtype==np.int16 and np.array_equal(raw[0],raw[1]) and np.array_equal(raw[0],raw[2]) and np.isin(raw,[1,2,3]).all(),f'label {target}/{pid}')
            require(bits.shape==(128,128) and bits.dtype==np.uint8 and (bits<=7).all() and np.array_equal(boundary,bits!=0), f'boundary bits {target}/{pid}')
            label[pid]=raw[0]-1;pair[pid]=bits
            require(int((bits>0).sum())==row.boundary_pixels,f'metadata boundary count {target}/{pid}')
            for name,(bit,_,_) in PAIRS.items():
                require(int(((bits&bit)>0).sum())==getattr(row,'boundary_'+name+'_pixels'),f'metadata type count {target}/{pid}/{name}')
        folder=within_site_file('convgru',short).parent
        exported=tifffile.imread(record(folder/'maps/reference.tif','exported reference'))-1
        full=label.reshape(20,20,128,128).transpose(0,2,1,3).reshape(2560,2560)
        check('exported label identity '+target,np.array_equal(exported,full))
        bandfull=np.load(record(folder/'details/reference_assets/distance_band_index.npy','existing seven bands'),allow_pickle=False)
        dist=np.load(record(folder/'details/reference_assets/class_boundary_distance_pixels.npy','existing distance; EDT not rerun'),allow_pickle=False)
        check('distance to band '+target,np.array_equal(np.searchsorted([1,2,3,4,5,6],dist,side='left'),bandfull))
        band=bandfull.reshape(20,128,20,128).transpose(0,2,1,3).reshape(400,128,128)
        # Validate bit semantics against full-label FOUR-neighbour edges; no new masks are used.
        fullpair=pair.reshape(20,20,128,128).transpose(0,2,1,3).reshape(2560,2560)
        expected=np.zeros_like(fullpair)
        for _,(bit,c1,c2) in PAIRS.items():
            hor=((full[:,:-1]==c1)&(full[:,1:]==c2))|((full[:,:-1]==c2)&(full[:,1:]==c1))
            ver=((full[:-1,:]==c1)&(full[1:,:]==c2))|((full[:-1,:]==c2)&(full[1:,:]==c1))
            expected[:,:-1]|=hor.astype('uint8')*bit;expected[:,1:]|=hor.astype('uint8')*bit
            expected[:-1,:]|=ver.astype('uint8')*bit;expected[1:,:]|=ver.astype('uint8')*bit
        check('existing boundary equals documented full-reference four-neighbours '+target,np.array_equal(expected,fullpair))
        counts=np.empty((400,7,8,3),np.int32)
        for pid in range(400):
            counts[pid]=np.bincount(((band[pid].astype('int32')*8+pair[pid])*3+label[pid]).ravel(),minlength=7*8*3).reshape(7,8,3)
            feature=f[(f.dataset_id==target)&(f.patch_id==pid)].iloc[0]
            require(np.array_equal(counts[pid].sum((0,1)),feature[[c+'_pixels' for c in CLASSES]].to_numpy(dtype=int)),f'feature reference identity {target}/{pid}')
        for bi,bn in enumerate(BANDS):
            for bit in range(8):
                for c,cn in enumerate(CLASSES):
                    n=counts[:,bi,bit,c]
                    summaries.append(dict(target=target,band=bn,bitmask=bit,true_class=cn,pixels=int(n.sum()),patches=int((n>0).sum()),
                                          class_total=int(counts[:,:,:,c].sum()),pixel_share=float(n.sum()/counts[:,:,:,c].sum())))
        np.savez_compressed(PROC/f'reference_{target}.npz',labels=label,pair_bits=pair,bands=band,
                            patch_id=np.arange(400),patch_uid=meta.patch_uid.to_numpy(dtype=str),fold_id=meta.fold_id.to_numpy(),support=counts)
        save(meta,'metadata_'+target,True)
        assets.append(dict(target=target,dataset_dir=ds.as_posix(),reference_folder=folder.as_posix(),
                           typed_pixels=int((pair!=0).sum()),multiple_type_pixels=int(np.isin(pair,[3,5,6,7]).sum()),
                           typed_outside_nearest=int(((pair!=0)&(band!=0)).sum()),nearest_without_type=int(((pair==0)&(band==0)).sum()),
                           segment_id_available=False,unknown_invalid_bits=0))
        print('reference prepared',target,flush=True)
    save(pd.DataFrame(summaries),'reference_type_band_support')
    save(pd.DataFrame(assets),'asset_inventory')
    finish('prepare')


def runs():
    for target,model in itertools.product(SITES,MODELS):
        yield 'within',model,target,target,within_site_file(model,target.split('_')[0]).parent
    for folder in sorted(Path('D:/cross_site_all_20260916').glob('*__*')):
        if not folder.is_dir():continue
        model,source=folder.name.split('__')[:2]
        if model not in MODELS:continue
        for target in SITES:
            if source!=target:yield 'cross',model,source,target,folder/target


def count_prediction(labels,predictions,bands,bits):
    require(labels.shape==predictions.shape==bands.shape==bits.shape,'joint array shape')
    require(np.isin(predictions,[0,1,2]).all(),'prediction class code')
    return np.bincount((((bands.astype('int32')*8+bits)*3+labels)*3+predictions).ravel(),minlength=7*8*9).reshape(7,8,3,3)


def count():
    require(not (PROC/'joint_counts_index.csv').exists(),'joint counts already complete; reuse for analyze')
    refs={t:np.load(record(PROC/f'reference_{t}.npz'),allow_pickle=False) for t in SITES}
    raww=base.cm_frame(read(ROOT/'results/raw/within_site_confusion_matrices.csv'),'within')
    raww=raww[raww.result_type.eq('oof_pooled')].set_index(['model','target'])
    rawc=base.cm_frame(read(ROOT/'results/raw/cross_site_confusion_matrices.csv'),'cross').set_index(['model','source','target','fold'])
    bw=read(ROOT/'results/processed/sec33_round3_distance/boundary_within_cm_reused.csv').set_index(['model','target','band'])
    bc=read(ROOT/'results/processed/sec33_round3_distance/boundary_cross_fold_cm_reused.csv').set_index(['model','source','target','fold','band'])
    tables=external_tables()
    pw=read(tables['within_patch_oof.csv']).set_index(['model','dataset_id','patch_id'])
    pc=read(tables['cross_patch_fold.csv']).set_index(['model','source_dataset_id','target_dataset_id','source_fold','patch_id'])
    index=[]; aggregate=[]; issues=[]
    for kind,model,source,target,folder in runs():
        ref=refs[target];lab=ref['labels'];band=ref['bands'];bits=ref['pair_bits']
        # Hash/read spatial contracts for every result identity, keeping historical fingerprints.
        contract=jread(folder/'details/reference_assets/reference_contract.json')
        check('spatial contract '+str(folder),contract['spatial_contract']['dataset_id']==target and contract['distance_algorithm_version']=='class_shared_edge_center_edt_v1')
        ar=tifffile.imread(record(folder/'maps/reference.tif'))-1
        rb=np.load(record(folder/'details/reference_assets/distance_band_index.npy'),allow_pickle=False)
        layout=lambda a:a.reshape(20,128,20,128).transpose(0,2,1,3).reshape(400,128,128)
        check('shared target label/band '+str(folder),np.array_equal(layout(ar),lab) and np.array_equal(layout(rb),band))
        pooled=np.zeros((400,7,8,3,3),np.int32);seen=set()
        for k in range(1,6):
            details=folder/'details'/f'fold_{k}'
            run=jread(details/'test_patch_run.json');csv=read(details/'test_patch_metrics.csv')
            pred=np.load(record(details/'test_patch_predictions.npz','saved prediction; no inference'),allow_pickle=False)
            ids=pred['patch_id'].astype(int);uid=pred['patch_uid']
            check('prediction identity '+str(details),run['model_name']==model and run['train_dataset_id']==source and run['eval_dataset_id']==target and run['experiment_fold']==k)
            require(len(set(ids))==len(ids) and set(ids)<=set(range(400)),'unique prediction ids')
            require(np.array_equal(uid,np.asarray([f'{target}__p{i:04d}' for i in ids])),'NPZ UID identity')
            require(np.array_equal(csv.patch_id,ids) and np.array_equal(csv.patch_uid,uid) and csv.rotation.eq(0).all(),'CSV/NPZ identity and rotation')
            require(np.array_equal(csv.fold_id.to_numpy(),ref['fold_id'][ids]),'metadata test-fold identity')
            require(csv.experiment_fold.eq(k).all(),'CSV experiment fold')
            if kind=='within':
                require(len(ids)==80 and not seen.intersection(ids) and set(ref['fold_id'][ids])=={run['test_fold']},'OOF coverage/test set')
                seen.update(ids)
            else:require(set(ids)==set(range(400)) and len(ids)==400,'cross full coverage')
            joint=np.zeros_like(pooled)
            csvcm=csv[[f'cm_gt_{i}_pred_{j}' for i in CLASSES for j in CLASSES]].to_numpy(dtype=np.int64).reshape(-1,3,3)
            for n,pid in enumerate(ids):
                joint[pid]=count_prediction(lab[pid],pred['predictions'][n],band[pid],bits[pid])
                cm=joint[pid].sum((0,1))
                require(np.array_equal(cm,csvcm[n]),f'prediction vs evaluator CM {details}/{pid}')
                expected=(pw.loc[(model,target,pid)] if kind=='within' else pc.loc[(model,source,target,k,pid)])
                require(np.array_equal(cm,np.asarray([expected[f'cm_{i}{j}'] for i in range(3) for j in range(3)]).reshape(3,3)),f'prediction vs prior patch table {details}/{pid}')
            if kind=='within':pooled+=joint
            else:emit_counts(joint,kind,model,source,target,k,rawc.loc[(model,source,target,k)],bc,index,aggregate,ref['support'])
        if kind=='within':
            require(seen==set(range(400)),'OOF each patch exactly once')
            emit_counts(pooled,kind,model,source,target,0,raww.loc[(model,target)],bw,index,aggregate,ref['support'])
        check('predictions and joint counts '+str(folder),True,'five saved predictions checked, patch CMs and integer closure')
        print('counted',kind,model,source,target,flush=True)
    require(len(index)==192,'12 within plus 180 cross')
    save(pd.DataFrame(index),'joint_counts_index',True)
    save(pd.DataFrame(aggregate),'type_band_cm',True)
    finish('count')


def emit_counts(joint,kind,model,source,target,k,raw,old,index,aggregate,support):
    require(np.array_equal(joint.sum(-1),support),'same reference support by type, band, patch and class')
    cm=joint.sum(0,dtype=np.int64)
    require(np.array_equal(cm.sum((0,1)),cm_of(raw)),'joint to raw whole-site closure')
    for b,bn in enumerate(BANDS):
        key=(model,target,bn) if kind=='within' else (model,source,target,k,bn)
        require(np.array_equal(cm[b].sum(0),cm_of(old.loc[key])),'type masks to old band CM closure')
        for mask in range(8):
            aggregate.append(dict(kind=kind,model=model,source=source,target=target,fold=k,band=bn,bitmask=mask,**rows_cm(cm[b,mask])))
    name=f'joint_{kind}_{model}_{source}_{target}_{k}.npz'
    path=PROC/name
    require(not path.exists(),f'count file exists: {path}; retain and inspect before reusing')
    np.savez_compressed(path,cm=joint,patch_id=np.arange(400))
    index.append(dict(kind=kind,model=model,source=source,target=target,fold=k,file=name))


def metric_tables(cms, condition):
    """Complete three-class CMs -> class metrics, six directions, matched baselines."""
    classes=[]; directions=[]
    for _,r in cms.iterrows():
        cm=cm_of(r);identity={k:r[k] for k in RUNKEY+condition}
        for c,cn in enumerate(CLASSES):
            met=class_metrics(cm,c)
            classes.append(identity|dict(crop=cn,**met))
            for j,jn in enumerate(CLASSES):
                if c==j:continue
                directions.append(identity|dict(true_class=cn,predicted_class=jn,pixels=met['pixels'],
                                                errors=int(cm[c,j]),rate=cm[c,j]/met['pixels'] if met['pixels'] else np.nan,
                                                f1_fn_component=cm[c,j]/(met['pixels']+met['predicted_pixels']) if met['pixels']+met['predicted_pixels'] else np.nan))
    cl=pd.DataFrame(classes);di=pd.DataFrame(directions)
    cl=add_baselines(cl,condition+['crop'],['f1','precision','recall','leakage','fn_component','fp_component'])
    di=add_baselines(di,condition+['true_class','predicted_class'],['rate','errors','f1_fn_component'])
    clsummary=summarize(cl,condition+['crop'],['f1','precision','recall','leakage','fn_component','fp_component'],f1=True)
    disummary=summarize(di,condition+['true_class','predicted_class'],['rate','errors','f1_fn_component'])
    return cl,di,clsummary,disummary


def add_baselines(frame,conditions,fields):
    key=['model','target']+conditions
    w=frame[frame.kind.eq('within')][key+fields].rename(columns={f:'within_'+f for f in fields})
    z=frame.merge(w,on=key,how='left',validate='many_to_one',indicator=True)
    require(z._merge.eq('both').all(),'missing target baseline')
    z=z.drop(columns='_merge')
    for field in fields:
        z['delta_'+field]=z['within_'+field]-z[field] if field=='f1' else z[field]-z['within_'+field]
        z[field+'_status']=np.where(np.isfinite(z[field]),'defined','undefined_denominator_or_value')
    return z


def summarize(frame,conditions,fields,f1=False):
    key=['model','target']+conditions
    w=frame[frame.kind.eq('within')].set_index(key)
    require(not w.index.duplicated().any(),'unique within condition')
    rows=[]
    for ids,g in frame[frame.kind.eq('cross')].groupby(['model','source','target']+conditions,dropna=False,sort=False):
        model,source,target,*cs=ids
        baseline=w.loc[(model,target,*cs)]
        row=dict(zip(['model','source','target']+conditions,ids))
        if 'pixels' in g:require(g.pixels.eq(baseline.pixels).all(),'same target condition support');row['pixels']=int(baseline.pixels)
        for field in fields:
            within=float(baseline[field]);val=g[field].to_numpy(float)
            a=strict_stats(val,g.fold);dval=within-val if field=='f1' and f1 else val-within
            ds=strict_stats(dval,g.fold)
            row.update({'within_'+field:within,'cross_'+field+'_mean':a['mean'],'cross_'+field+'_std':a['std'],
                        'delta_'+field:ds['mean'],'delta_'+field+'_std':ds['std'],
                        'n_valid_'+field:a['n_valid'],'delta_'+field+'_direction':ds['direction'],
                        field+'_status':'defined' if ds['n_valid']==5 else 'undefined_one_or_more_predictions_or_baseline',
                        'delta_'+field+'_n_positive':ds['n_positive'],'delta_'+field+'_n_negative':ds['n_negative']})
        row['n_predictions']=5;rows.append(row)
    return pd.DataFrame(rows)


def common_weights(support):
    """Seven-band weights reference-only; missing support excluded and coverage explicit."""
    n=np.asarray(support,dtype=float)
    require(n.shape==(2,7) and (n>=0).all(),'two crops by seven reference bands')
    shared=(n>0).all(0)
    sums=n[:,shared].sum(1);totals=n.sum(1)
    w=np.full(7,0.0)
    if shared.any():w[shared]=np.mean(n[:,shared]/sums[:,None],axis=0)
    return shared,w,np.divide(sums,totals,out=np.full(2,np.nan),where=totals>0)


def weight_value(rate,weight):
    select=weight>0
    if not select.any() or not np.isfinite(np.asarray(rate)[select]).all():return np.nan
    return float(np.sum(np.asarray(rate)[select]*weight[select]))


def analyze():
    joint=read(PROC/'type_band_cm.csv')
    whole=joint.groupby(RUNKEY,as_index=False)[CM].sum()
    cl,di,cs,ds=metric_tables(whole,[])
    save(whole,'whole_cm',True);save(cl,'whole_class_per_prediction',True);save(di,'whole_direction_per_prediction',True)
    save(cs,'whole_class_summary');save(ds,'whole_direction_summary')
    gaps=[]
    for key,g in cl[cl.crop.isin(['corn','soybean'])].groupby(RUNKEY):
        z=g.set_index('crop');a=z.loc['corn'];b=z.loc['soybean']
        gaps.append(dict(zip(RUNKEY,key))|dict(f1_gap=a.f1-b.f1,precision_gap=a.precision-b.precision,
                    recall_gap=a.recall-b.recall,leakage_gap=b.leakage-a.leakage,
                    fn_component_gap=b.fn_component-a.fn_component,fp_component_gap=b.fp_component-a.fp_component))
    gap=pd.DataFrame(gaps);gs=summarize(gap,[],['f1_gap','precision_gap','recall_gap','leakage_gap','fn_component_gap','fp_component_gap'])
    save(gap,'crop_gap_per_prediction',True);save(gs,'crop_gap_summary')
    for r in gs.itertuples():
        z=cs[(cs.model==r.model)&(cs.source==r.source)&(cs.target==r.target)].set_index('crop')
        check('crop F1 difference identity '+str((r.model,r.source,r.target)),abs(r.cross_f1_gap_mean-(r.within_f1_gap+z.loc['soybean','delta_f1']-z.loc['corn','delta_f1']))<1e-12)
        check('F1 crop gap FN plus FP '+str((r.model,r.source,r.target)),abs(r.cross_f1_gap_mean-r.cross_fn_component_gap_mean-r.cross_fp_component_gap_mean)<1e-12)
    current=read(ROOT/'results/summary/f1_raw_scale/within_site_crop_f1.csv').set_index(['model','target'])
    crosscurrent=read(ROOT/'results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv').set_index(['model','source','target'])
    for r in cs[cs.crop.isin(['corn','soybean'])].itertuples():
        check('current F1 '+str((r.model,r.source,r.target,r.crop)),abs(r.within_f1-current.loc[(r.model,r.target),r.crop+'_f1'])<1e-12 and abs(r.cross_f1_mean-crosscurrent.loc[(r.model,r.source,r.target),r.crop+'_f1_mean'])<1e-12 and abs(r.cross_f1_std-crosscurrent.loc[(r.model,r.source,r.target),r.crop+'_f1_std'])<1e-12)
    bandcm=joint.groupby(RUNKEY+['band'],as_index=False)[CM].sum()
    bcl,bdi,bcs,bds=metric_tables(bandcm,['band'])
    save(bcl,'distance_class_per_prediction',True);save(bdi,'distance_direction_per_prediction',True)
    save(bcs,'distance_class_summary');save(bds,'distance_direction_summary')
    analyze_types(joint,whole)
    analyze_weights(bcl)
    analyze_area_and_matches()
    finish('analyze')


def analyze_types(joint,whole):
    _,edi,_,eds=metric_tables(joint,['band','bitmask'])
    sup=read(SUM/'reference_type_band_support.csv')
    eds=eds.merge(sup,on=['target','band','bitmask','true_class'],suffixes=('','_reference'),validate='many_to_one')
    require(eds.pixels.eq(eds.pixels_reference).all(),'exclusive support equality')
    eds['net_added_errors']=eds.delta_errors
    eds['net_class_error_contribution']=eds.pixel_share*eds.delta_rate
    # Zero-support regions have zero count contribution, even though their conditional rate is NA.
    eds['net_class_error_contribution']=eds.net_added_errors/eds.class_total
    save(edi,'exclusive_type_direction_per_prediction',True);save(eds,'exclusive_type_direction_summary')
    # Inclusive original masks are kept distinct from the exclusive bit-combination closure table.
    types=[]
    for name,(bit,_,_) in PAIRS.items():
        z=joint[(joint.bitmask.astype(int)&bit)!=0].groupby(RUNKEY+['band'],as_index=False)[CM].sum()
        z['boundary_type']=name;types.append(z)
    types=pd.concat(types,ignore_index=True)
    _,di,_,ds=metric_tables(types,['boundary_type','band'])
    # All directed rates retained. Interpret only true classes that constitute this pair.
    for df in (di,ds):
        df['role']=[('to_opposite' if CLASSES.index(j) in PAIRS[t][1:] else 'to_third')
                    if CLASSES.index(c) in PAIRS[t][1:] else 'not_a_side'
                    for t,c,j in zip(df.boundary_type,df.true_class,df.predicted_class)]
    support=read(SUM/'reference_type_band_support.csv')
    refrows=[]
    for target in SITES:
        ref=np.load(record(PROC/f'reference_{target}.npz'),allow_pickle=False)['support']
        for name,(bit,_,_) in PAIRS.items():
            selected=ref[:,:,[(i&bit)!=0 for i in range(8)],:].sum(2)
            for b,bn in enumerate(BANDS):
                for c,cn in enumerate(CLASSES):
                    refrows.append(dict(target=target,boundary_type=name,band=bn,true_class=cn,
                                        reference_pixels=int(selected[:,b,c].sum()),patches=int((selected[:,b,c]>0).sum()),
                                        class_total=int(ref[:,:,:,c].sum()),pixel_share=float(selected[:,b,c].sum()/ref[:,:,:,c].sum())))
    refdf=pd.DataFrame(refrows)
    ds=ds.merge(refdf,on=['target','boundary_type','band','true_class'],validate='many_to_one')
    require(ds.pixels.eq(ds.reference_pixels).all(),'type reference support')
    ds['net_added_errors']=ds.delta_errors
    ds['net_class_error_contribution']=ds.pixel_share*ds.delta_rate
    save(di,'type_direction_per_prediction',True);save(ds,'type_direction_summary');save(refdf,'inclusive_type_reference_support')
    asym=[]
    for name,(_,c1,c2) in PAIRS.items():
        z=di[di.boundary_type.eq(name)&di.role.eq('to_opposite')]
        for ids,g in z.groupby(RUNKEY+['band']):
            r=g.set_index('true_class')
            # positive means the second named side has larger directed error.
            asym.append(dict(zip(RUNKEY+['band'],ids))|dict(boundary_type=name,
                        first_side=CLASSES[c1],second_side=CLASSES[c2],
                        rate_asymmetry=float(r.loc[CLASSES[c2],'rate']-r.loc[CLASSES[c1],'rate'])))
    asym=pd.DataFrame(asym)
    save(asym,'boundary_asymmetry_per_prediction',True)
    save(summarize(asym,['boundary_type','band','first_side','second_side'],['rate_asymmetry']),'boundary_asymmetry_summary')


def analyze_weights(bcl):
    reference=bcl[bcl.kind.eq('within')&bcl.model.eq(MODELS[0])]
    weighted=[];wr=[]
    for target in SITES:
        n=np.asarray([reference[(reference.target==target)&(reference.crop==c)].set_index('band').loc[list(BANDS),'pixels'].to_numpy() for c in ['corn','soybean']])
        shared,w,cov=common_weights(n)
        for b,bn in enumerate(BANDS):
            wr.append(dict(target=target,band=bn,corn_pixels=int(n[0,b]),soybean_pixels=int(n[1,b]),shared=shared[b],
                           corn_share=n[0,b]/n[0].sum(),soybean_share=n[1,b]/n[1].sum(),common_weight=w[b],
                           corn_coverage=cov[0],soybean_coverage=cov[1]))
        for ids,g in bcl[bcl.target.eq(target)&bcl.crop.isin(['corn','soybean'])].groupby(RUNKEY):
            for ci,c in enumerate(['corn','soybean']):
                r=g[g.crop.eq(c)].set_index('band').loc[list(BANDS)]
                e=r.leakage.to_numpy(float)
                own=n[ci]/n[ci].sum();ownshared=np.where(shared,n[ci],0);ownshared=ownshared/ownshared.sum() if ownshared.sum() else ownshared
                weighted.append(dict(zip(RUNKEY,ids))|dict(crop=c,coverage=cov[ci],
                         full_original=weight_value(e,own),shared_original=weight_value(e,ownshared),
                         common_weighted=weight_value(e,w)))
    weighted=add_baselines(pd.DataFrame(weighted),['crop'],['full_original','shared_original','common_weighted'])
    save(pd.DataFrame(wr),'distance_common_weights');save(weighted,'distance_weighted_per_prediction',True)
    summary=summarize(weighted,['crop'],['full_original','shared_original','common_weighted'])
    save(summary,'distance_weighted_summary')
    gaps=[]
    for ids,g in weighted.groupby(RUNKEY):
        r=g.set_index('crop')
        gaps.append(dict(zip(RUNKEY,ids))|{name+'_gap':r.loc['soybean',name]-r.loc['corn',name] for name in ['full_original','shared_original','common_weighted']})
    gaps=pd.DataFrame(gaps);gsummary=summarize(gaps,[],[v+'_gap' for v in ['full_original','shared_original','common_weighted']])
    def change(a,b):
        if not np.isfinite(a+b):return 'not_calculable'
        if a*b<0:return 'reversed'
        return 'shrunk' if abs(b)<abs(a) else 'expanded' if abs(b)>abs(a) else 'unchanged'
    for prefix in ['within','cross','delta']:
        suf='_mean' if prefix=='cross' else ''
        gsummary[prefix+'_adjustment_pattern']=[change(a,b) for a,b in zip(gsummary[prefix+'_shared_original_gap'+suf],gsummary[prefix+'_common_weighted_gap'+suf])]
    save(gaps,'weighted_crop_gap_per_prediction',True);save(gsummary,'weighted_crop_gap_summary')


def analyze_area_and_matches():
    index=read(PROC/'joint_counts_index.csv');groups=read(PROC/'frozen_area_assignments.csv');matches=read(PROC/'fixed_matches.csv')
    agrows=[];mcrows=[];locrows=[]
    for r in index.itertuples():
        arr=np.load(record(PROC/r.file),allow_pickle=False)['cm']
        identity={k:getattr(r,k) for k in RUNKEY}
        for (crop,group),z in groups[groups.target.eq(r.target)].groupby(['crop','group']):
            ids=z.patch_id.to_numpy(int);cm=arr[ids].sum((0,1,2),dtype=np.int64)
            agrows.append(identity|dict(grouping_crop=crop,group=group,**rows_cm(cm)))
        if r.target!='il_2023':continue
        for contrast,z in matches.groupby('contrast'):
            for side in ['left','right']:
                ids=z[side+'_patch_id'].to_numpy(int)
                cm=arr[ids].sum((0,1,2),dtype=np.int64)
                mcrows.append(identity|dict(contrast=contrast,side=side,**rows_cm(cm)))
                b=arr[ids].sum(0,dtype=np.int64)
                for bi,bn in enumerate(BANDS):
                    locrows.append(identity|dict(contrast=contrast,side=side,location='all_types',band=bn,**rows_cm(b[bi].sum(0))))
                    for name,(bit,_,_) in PAIRS.items():
                        locrows.append(identity|dict(contrast=contrast,side=side,location=name,band=bn,**rows_cm(b[bi,[(i&bit)!=0 for i in range(8)]].sum(0))))
    ag=pd.DataFrame(agrows);mc=pd.DataFrame(mcrows);loc=pd.DataFrame(locrows)
    # Frozen group CMs are checked against the previous round, including missing-class groups.
    for kind,file in [('within','within_group_cm.csv'),('cross','cross_group_fold_cm.csv')]:
        old=read(ROOT/'results/processed/sec33_f1_raw_scale'/file).rename(columns={'crop':'grouping_crop'})
        old=base.cm_frame(old,file);keys=['model','target','grouping_crop','group']+(['source','fold'] if kind=='cross' else [])
        a=ag[ag.kind.eq(kind)].set_index(keys)[CM].sort_index();b=old.set_index(keys)[CM].sort_index()
        check('joint patch counts recover frozen AREA '+kind,np.array_equal(a.index.to_numpy(),b.index.to_numpy()) and np.array_equal(a.to_numpy(),b.to_numpy()))
    for name,frame,conds in [('area',ag,['grouping_crop','group']),('matched',mc,['contrast','side']),('matched_location',loc,['contrast','side','location','band'])]:
        save(frame,name+'_cm',True)
        cl,di,cs,ds=metric_tables(frame,conds)
        save(di,name+'_direction_per_prediction',True);save(ds,name+'_direction_summary')
        if name!='matched_location':save(cl,name+'_class_per_prediction',True);save(cs,name+'_class_summary')
        if name=='matched':
            contrasts=[]
            for ids,g in di.groupby(RUNKEY+['contrast','true_class','predicted_class']):
                z=g.set_index('side')
                contrasts.append(dict(zip(RUNKEY+['contrast','true_class','predicted_class'],ids))|dict(right_minus_left_rate=z.loc['right','rate']-z.loc['left','rate']))
            c=pd.DataFrame(contrasts)
            save(c,'matched_contrast_per_prediction',True)
            save(summarize(c,['contrast','true_class','predicted_class'],['right_minus_left_rate']),'matched_contrast_summary')
    # Reference composition, ED/AI ranges are separate from model outcomes.
    features=read(PROC/'patch_features.csv');features=features.merge(groups[['patch_uid','crop','group']],on='patch_uid',validate='one_to_many')
    rows=[]
    for key,g in features.groupby(['dataset_id','crop','group']):
        for field in ['corn_ratio','soybean_ratio','other_ratio','ED',key[1]+'_AREA_MN',key[1]+'_AI']:
            rows.append(dict(target=key[0],grouping_crop=key[1],group=key[2],feature=field,n_defined=int(g[field].notna().sum()),min=g[field].min(),median=g[field].median(),max=g[field].max()))
    save(pd.DataFrame(rows),'area_feature_distributions')


def f1_error_components(cm, c):
    """Four additive error terms for class c, each with its own run's Z."""
    z=int(cm[c].sum()+cm[:,c].sum())
    return {(role,CLASSES[j]):float(cm[c,j] if role=='outgoing' else cm[j,c])/z if z else np.nan
            for role in ['outgoing','incoming'] for j in range(3) if j!=c}


def close_values(name, a, b):
    a,b=np.asarray(a,float),np.asarray(b,float)
    check(name,a.shape==b.shape and np.allclose(a,b,rtol=0,atol=1e-12,equal_nan=True),
          float(np.nanmax(abs(a-b))) if a.size and np.isfinite(a-b).any() else 'all NA')


def diagnose():
    """Read existing counts only; all joint arrays and historical masks are retained."""
    whole=read(PROC/'whole_cm.csv');joint=read(PROC/'type_band_cm.csv')
    # Directly audit serialized integer CMs, including zero-support mask states.
    key=RUNKEY
    w=whole.set_index(key)[CM].sort_index()
    recovered=joint.groupby(key)[CM].sum().sort_index()
    check('all exclusive masks and bands recover whole integers',w.equals(recovered))
    coverage=whole[whole.kind.eq('cross')].groupby(['model','source','target']).fold.agg(list)
    check('36 paths models with exactly five explicit folds',len(coverage)==36 and all(sorted(x)==[1,2,3,4,5] for x in coverage))
    audit=[]
    for name,conds in [('whole',[]),('distance',['band']),('area',['grouping_crop','group']),('matched',['contrast','side'])]:
        cl=read(PROC/(name+'_class_per_prediction.csv'))
        di=read(PROC/(name+'_direction_per_prediction.csv'))
        k=RUNKEY+conds
        a=di.groupby(k+['true_class']).rate.agg(lambda x:x.sum(min_count=2)).rename_axis(index={'true_class':'crop'}).sort_index()
        b=cl.set_index(k+['crop']).leakage.sort_index()
        close_values(name+' two directed rates restore leakage',a,b)
        close_values(name+' FN+FP restores one minus F1',cl.fn_component+cl.fp_component,1-cl.f1)
        for r in di.itertuples():
            if r.kind=='cross':audit.append(dict(table=name,true_class=r.true_class,
                                                status=r.rate_status,delta_rate=r.delta_rate))
    audit=pd.DataFrame(audit)
    rows=[]
    for k,g in audit.groupby(['table','true_class']):
        rows.append(dict(table=k[0],true_class=k[1],cross_rows=len(g),NA=int(g.delta_rate.isna().sum()),
                         negative=int(g.delta_rate.lt(0).sum()),zero=int(g.delta_rate.eq(0).sum()),positive=int(g.delta_rate.gt(0).sum())))
    save(pd.DataFrame(rows),'na_negative_inventory')
    ex=read(SUM/'exclusive_type_direction_summary.csv')
    direct=read(SUM/'whole_direction_summary.csv')
    k=['model','source','target','true_class','predicted_class']
    close_values('exclusive type distance contributions restore full directed increments',
                 ex.groupby(k).net_class_error_contribution.sum().sort_index(),direct.set_index(k).delta_rate.sort_index())
    for prefix,conditions,support_name,support_cols in [
        ('exclusive_type',['band','bitmask'],'reference_type_band_support',['patches','class_total','pixel_share']),
        ('type',['boundary_type','band'],'inclusive_type_reference_support',['patches','class_total','pixel_share'])]:
        dp=read(PROC/(prefix+'_direction_per_prediction.csv'))
        ref=read(SUM/(support_name+'.csv'))
        identity=['target']+conditions+['true_class']
        cols=RUNKEY+conditions+['true_class','predicted_class','pixels','errors','rate','within_rate','delta_rate','delta_errors','rate_status']
        dp=dp[cols].merge(ref[identity+support_cols],on=identity,validate='many_to_one')
        dp['net_class_error_contribution']=dp.delta_errors/dp.class_total
        save(dp,prefix+'_contribution_per_prediction',True)
        if prefix=='exclusive_type':
            k=RUNKEY+['true_class','predicted_class']
            wd=read(PROC/'whole_direction_per_prediction.csv').set_index(k).sort_index()
            close_values('per-prediction exclusive contributions restore whole increments',
                         dp.groupby(k).net_class_error_contribution.sum().sort_index(),wd.delta_rate)
    # Reference support for all model/source conditions; matrix rows rather than metrics.
    reference=read(SUM/'reference_type_band_support.csv').set_index(['target','band','bitmask','true_class'])
    for c,cn in enumerate(CLASSES):
        a=joint[CM[c*3:c*3+3]].sum(axis=1).to_numpy()
        b=np.asarray([reference.loc[(r.target,r.band,r.bitmask,cn),'pixels'] for r in joint.itertuples()])
        check('same joint reference support '+cn,np.array_equal(a,b))
    weight=read(SUM/'distance_common_weights.csv')
    close_values('common weights sum to one by target',weight.groupby('target').common_weight.sum(),np.ones(4))
    weighted=read(PROC/'distance_weighted_per_prediction.csv')
    cl=read(PROC/'whole_class_per_prediction.csv')
    k=RUNKEY+['crop']
    a=weighted.set_index(k).sort_index();b=cl[cl.crop.isin(['corn','soybean'])].set_index(k).sort_index()
    close_values('original distance weights recover full-site leakage',a.full_original,b.leakage)
    close_values('original weighted increments recover full-site increments',a.delta_full_original,b.delta_leakage)
    # Each F1 error uses its receiving/true class Z, not a real-class error denominator.
    components=[]
    for _,r in whole.iterrows():
        cm=cm_of(r)
        for c in [0,2]:
            for (role,other),val in f1_error_components(cm,c).items():
                components.append({k:r[k] for k in RUNKEY}|dict(crop=CLASSES[c],role=role,other_class=other,component=val))
    comp=add_baselines(pd.DataFrame(components),['crop','role','other_class'],['component'])
    save(comp,'whole_f1_error_components_per_prediction',True)
    csum=summarize(comp,['crop','role','other_class'],['component']);save(csum,'whole_f1_error_components_summary')
    k=RUNKEY+['crop']
    close_values('four F1 terms restore per-prediction delta F1',comp.groupby(k).delta_component.sum(min_count=4).sort_index(),
                 b.delta_f1)
    csummary=read(SUM/'whole_class_summary.csv');cs=csummary[csummary.crop.isin(['corn','soybean'])]
    k=['model','source','target','crop']
    close_values('four mean F1 terms restore delta F1',csum.groupby(k).delta_component.sum(min_count=4).sort_index(),cs.set_index(k).delta_f1.sort_index())
    # Model/source contrasts retain explicit folds and differences from the same within baseline.
    di=read(PROC/'distance_direction_per_prediction.csv');near=di[di.band.eq(BANDS[0])];far=di[di.band.eq(BANDS[-1])]
    k=RUNKEY+['true_class','predicted_class']
    paired=near.merge(far,on=k,suffixes=('_near','_interior'),validate='one_to_one')
    for metric in ['rate','delta_rate']:
        paired['interior_minus_near_'+metric]=paired[metric+'_interior']-paired[metric+'_near']
    save(paired,'directed_endpoints_per_prediction',True)
    save(summarize(paired,['true_class','predicted_class'],['interior_minus_near_rate']), 'directed_endpoints_summary')
    # Frozen groups overview: high minus low directional increments, complete four targets.
    area=read(PROC/'area_direction_per_prediction.csv');lo=area[area.group.eq('low')];hi=area[area.group.eq('high')]
    k=RUNKEY+['grouping_crop','true_class','predicted_class']
    ah=lo.merge(hi,on=k,suffixes=('_low','_high'),validate='one_to_one')
    ah['high_minus_low_rate']=ah.rate_high-ah.rate_low
    save(ah,'area_high_low_per_prediction',True)
    save(summarize(ah,['grouping_crop','true_class','predicted_class'],['high_minus_low_rate']),'area_high_low_summary')
    # Same selected patch sets connected to location; no unrelated summary-table joins.
    ld=read(PROC/'matched_location_direction_per_prediction.csv')
    contrasts=[]
    for ids,g in ld.groupby(RUNKEY+['contrast','location','band','true_class','predicted_class']):
        z=g.set_index('side')
        contrasts.append(dict(zip(RUNKEY+['contrast','location','band','true_class','predicted_class'],ids))|
                         dict(right_minus_left_rate=z.loc['right','rate']-z.loc['left','rate']))
    lc=pd.DataFrame(contrasts);save(lc,'matched_location_contrast_per_prediction',True)
    save(summarize(lc,['contrast','location','band','true_class','predicted_class'],['right_minus_left_rate']),'matched_location_contrast_summary')
    # Record candidate/selected/common-support coverage and remaining feature imbalance.
    matches=read(PROC/'fixed_matches.csv');feature=read(PROC/'patch_features.csv');rules=read(SUM/'comparison_rules.csv')
    d=feature[feature.dataset_id.eq('il_2023')].set_index('patch_id');rr=[]
    for rule in rules.itertuples():
        z=matches[matches.contrast.eq(rule.contrast)]
        check('unique selected patches '+rule.contrast,not z.left_patch_id.duplicated().any() and not z.right_patch_id.duplicated().any() and len(z)>=rule.minimum_pairs)
        for side in ['left','right']:
            f=d.loc[z[side+'_patch_id']]
            rr.append(dict(contrast=rule.contrast,side=side,patches=len(f),candidate_patches=getattr(rule,side+'_candidates'),
                           candidate_coverage=len(f)/getattr(rule,side+'_candidates'),site_patch_coverage=len(f)/400,
                           soybean_pixel_coverage=f.soybean_pixels.sum()/d.soybean_pixels.sum(),
                           corn_pixel_coverage=f.corn_pixels.sum()/d.corn_pixels.sum()))
        if rule.contrast=='area_at_close_composition':
            for c in ['corn','soybean']:check('composition caliper '+c,(abs(z['left_'+c+'_ratio']-z['right_'+c+'_ratio'])<=.05).all())
        else:check('AREA caliper', (abs(np.log(z.left_soybean_AREA_MN/z.right_soybean_AREA_MN))<=np.log(1.1)).all())
    save(pd.DataFrame(rr),'matched_support_coverage')
    # Compact science counts, always based on full precision and with denominators explicit.
    gap=read(SUM/'crop_gap_summary.csv');wg=read(SUM/'weighted_crop_gap_summary.csv')
    asym=read(SUM/'boundary_asymmetry_summary.csv');asym=asym[asym.band.eq(BANDS[0])&asym.boundary_type.eq('corn_soybean')]
    ap=read(PROC/'boundary_asymmetry_per_prediction.csv')
    ap['absolute_asymmetry']=abs(ap.rate_asymmetry)
    ap=add_baselines(ap,['boundary_type','band','first_side','second_side'],['rate_asymmetry','absolute_asymmetry'])
    save(ap,'boundary_asymmetry_diagnostic_per_prediction',True)
    # |mean signed asymmetry| and mean |per-prediction asymmetry| are different statistics.
    asum=summarize(ap,['boundary_type','band','first_side','second_side'],['absolute_asymmetry'])
    save(asum,'boundary_absolute_asymmetry_summary')
    type_summary=read(SUM/'type_direction_summary.csv')
    tp=type_summary[type_summary.band.eq(BANDS[0])&type_summary.role.ne('not_a_side')].pivot(
        index=['model','source','target','boundary_type','true_class'],columns='role',values='cross_rate_mean')
    save(tp[tp.to_third>tp.to_opposite].reset_index(),'boundary_third_class_dominance_exceptions')
    facts=dict(within_corn_f1_higher=int(gap.drop_duplicates(['model','target']).within_f1_gap.gt(0).sum()),within_n=12,
               cross_corn_f1_higher=int(gap.cross_f1_gap_mean.gt(0).sum()),cross_n=36,
               cross_f1_gap_expanded=int(gap.delta_f1_gap.gt(0).sum()),
               f1_and_leakage_opposite_sign=int((gap.cross_f1_gap_mean*gap.cross_leakage_gap_mean<0).sum()),
               within_weight_patterns=wg.drop_duplicates(['model','target']).within_adjustment_pattern.value_counts().to_dict(),
               cross_weight_patterns=wg.cross_adjustment_pattern.value_counts().to_dict(),
               delta_weight_patterns=wg.delta_adjustment_pattern.value_counts().to_dict(),
               all_cross_weighted_gap_lower=bool((wg.cross_common_weighted_gap_mean<wg.cross_full_original_gap_mean).all()),
               maximum_abs_adjustment_of_increment=float(abs(wg.delta_common_weighted_gap-wg.delta_full_original_gap).max()),
               corn_soy_type_asymmetry_positive=int(asym.cross_rate_asymmetry_mean.gt(0).sum()),
               corn_soy_type_asymmetry_delta_positive=int(asym.delta_rate_asymmetry.gt(0).sum()),
               corn_soy_type_abs_of_mean_asymmetry_expanded=int((abs(asym.cross_rate_asymmetry_mean)>abs(asym.within_rate_asymmetry)).sum()),
               opposite_error_exceeds_third=int((tp.to_opposite>tp.to_third).sum()),boundary_side_combinations=len(tp),
               corn_soy_type_asymmetry_delta_five_directions=asym.delta_rate_asymmetry_direction.value_counts().to_dict())
    (SUM/'scientific_counts.json').write_text(json.dumps(facts,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    save(gap[gap.cross_f1_gap_mean.le(0)],'corn_f1_advantage_exceptions')
    save(gap[gap.cross_f1_gap_mean*gap.cross_leakage_gap_mean<0],'f1_leakage_ordering_exceptions')
    # Record the frozen group definitions rather than deriving replacement thresholds.
    save(read(ROOT/'results/summary/sec33_f1_raw_scale/group_features.csv'),'frozen_group_features_reused')
    # Zero-support inclusive regions have undefined conditional rates but zero count contributions.
    type_summary['net_class_error_contribution']=type_summary.net_added_errors/type_summary.class_total
    save(type_summary,'type_direction_summary')
    # Supplemental reference-only redundancy: no p-values, no independent AI explanation.
    save(read(ROOT/'results/summary/sec33_f1_raw_scale/area_ai_rank_redundancy.csv'),'area_ai_rank_redundancy_reused')
    # Matched distances are partitions of these exact selected patches.
    ml=read(PROC/'matched_location_cm.csv');mc=read(PROC/'matched_cm.csv')
    k=RUNKEY+['contrast','side']
    x=ml[ml.location.eq('all_types')].groupby(k)[CM].sum().sort_index();y=mc.set_index(k)[CM].sort_index()
    check('matched same-patch seven bands recover selected whole CM',x.equals(y))
    # Re-read saved distances, only checking validity and band identity, never invoking EDT.
    assets=read(SUM/'asset_inventory.csv')
    for r in assets.itertuples():
        folder=Path(r.reference_folder)/'details/reference_assets'
        dist=np.load(record(folder/'class_boundary_distance_pixels.npy'),allow_pickle=False)
        bands=np.load(record(folder/'distance_band_index.npy'),allow_pickle=False)
        check('saved distance finite positive '+r.target,np.isfinite(dist).all() and (dist>0).all())
        check('saved distance seven intervals '+r.target,np.array_equal(np.searchsorted([1,2,3,4,5,6],dist,side='left'),bands))
    # Input code documents are read for definitions, not run as old production workflows.
    for path in ['legacy/manuscript/HLS-Crop/src/learning/distance_band_analysis.py',
                 'legacy/manuscript/HLS-Crop/src/learning/boundary_analysis.py',
                 'legacy/manuscript/HLS-Crop/src/dataset.py',
                 'legacy/manuscript/HLS-Crop/docs/PROJECT_CONTEXT.md',
                 'results/summary/sec33_exploration/boundary_manifest.json',
                 'results/summary/sec33_exploration/boundary_identity_checks.csv']:
        record(ROOT/path,'definition or historical audit')
    # Schema inventory is for navigation; identity keys and metric definitions are in the dictionary.
    catalog=[]
    for parent in [PROC,SUM]:
        for path in sorted(parent.glob('*.csv')):
            if path.name=='table_catalog.csv':continue
            frame=pd.read_csv(path,encoding='utf-8-sig')
            catalog.append(dict(path=path.relative_to(ROOT).as_posix(),rows=len(frame),columns=len(frame.columns),
                                fields=';'.join(frame.columns)))
    save(pd.DataFrame(catalog),'table_catalog')
    finish('diagnose')


def seal():
    """Hash delivery without circular self-hash; does not claim a rerun of EDT/counting."""
    paths=[Path(__file__),ROOT/'scripts/plot_sec33_crop_spatial_context.py',ROOT/'scripts/test/test_sec33_crop_spatial_context.py',
           ROOT/'scripts/explore_sec33_round3_distance.py',ROOT/'scripts/calculate_crop_f1.py',ROOT/'scripts/figstyle.py',
           ROOT/'plan/tasks/2026-10-05-sec33-crop-spatial-context.md',ROOT/'verification/sec33-crop-spatial-context-2026-10-06.md']
    paths += [p for folder in [PROC,SUM,FIG] for p in folder.rglob('*') if p.is_file() and p.name!='delivery_manifest.json']
    for p in paths:record(p,'delivery')
    out=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),data_status='derived / exploratory',
             distance_transform_rerun=False,artifacts=list(INPUTS.values()))
    (SUM/'delivery_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','count','analyze','diagnose','seal']);a=p.parse_args()
    globals()[a.stage]()

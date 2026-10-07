"""Post-main-analysis sensitivity using SAVED K4 assignments and patch counts.

Stages: reference -> plot features and review -> aggregate -> analyze -> audit -> seal.
No fitting, prediction, landscape metrics or distance generation is performed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import itertools
import json
from pathlib import Path
import numpy as np
import pandas as pd
import explore_sec33_reference_patch_types as old

ROOT=old.ROOT
BASE=old.PROC
NAME='sec33_k4_sensitivity'
PROC=ROOT/'results/processed'/NAME
SUM=ROOT/'results/summary'/NAME
FIG=ROOT/'figures/exploratory'/NAME
CROPS=['corn','soybean']
TYPES=[f'K4-C{i}' for i in range(1,5)]
KEY=['target','PID']
REGIONS={'all':list(range(7)),'boundary':[0],'interior':list(range(1,7)),
         'far_interior':[6],**{f'band_{i+1}':[i] for i in range(7)}}
INPUTS={}
CHECKS=[]


def record(path):
    p=Path(path).resolve()
    if str(p) not in INPUTS:
        INPUTS[str(p)]={'path':p.as_posix(),'sha256':old.sha(p),'bytes':p.stat().st_size}
    return p


def read(path):
    return pd.read_csv(record(path),float_precision='round_trip')


def write(df,name,processed=False):
    directory=PROC if processed else SUM
    directory.mkdir(parents=True,exist_ok=True)
    df.to_csv(directory/(name+'.csv'),index=False,float_format='%.17g',encoding='utf-8',lineterminator='\n')


def check(name,ok,detail=''):
    CHECKS.append(dict(check=name,status='Verified' if bool(ok) else 'Not verified',detail=str(detail)))
    old.require(ok,name+': '+str(detail))


def json_write(path,data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')


def finish(stage):
    record(__file__);record(old.__file__)
    write(pd.DataFrame(CHECKS,columns=['check','status','detail']),stage+'_checks')
    json_write(SUM/(stage+'_manifest.json'),dict(stage=stage,created_at_utc=datetime.now(timezone.utc).isoformat(),
        status='Verified',data_status='derived / exploratory; post-main K4 sensitivity',inputs=list(INPUTS.values()),
        kmeans_rerun=False,fragstats_rerun=False,prediction_rerun=False,distance_regenerated=False))


def unchanged_prior():
    manifest=json.loads(record(old.SUM/'delivery_manifest.json').read_text(encoding='utf-8'))
    for item in manifest['artifacts']:
        check('prior artifact unchanged '+item['path'],old.sha(ROOT/item['path'])==item['sha256'])


def join_assignments(features,candidates,frozen):
    """All associations are identities; deliberate order changes are harmless."""
    for name,d in [('features',features),('candidates',candidates),('frozen',frozen)]:
        old.require(not d.duplicated(KEY).any(),'duplicate '+name+' identity')
    f=features[features.crop.isin(CROPS)].copy()
    cols=KEY+['crop','patch_uid','k2','k4']
    joined=f.merge(candidates[cols],on=KEY,how='outer',suffixes=('','_candidate'),validate='one_to_one',indicator=True)
    old.require(joined['_merge'].eq('both').all(),'candidate coverage')
    old.require(joined.crop.eq(joined.crop_candidate).all() and joined.patch_uid.eq(joined.patch_uid_candidate).all(),'candidate identity mismatch')
    joined=joined.drop(columns=['_merge','crop_candidate','patch_uid_candidate'])
    z=frozen[frozen.crop.isin(CROPS)][KEY+['spatial_type','crop','patch_uid']]
    joined=joined.merge(z,on=KEY,how='outer',suffixes=('','_frozen'),validate='one_to_one',indicator=True)
    old.require(joined['_merge'].eq('both').all(),'frozen coverage')
    old.require(joined.crop.eq(joined.crop_frozen).all() and joined.patch_uid.eq(joined.patch_uid_frozen).all(),'frozen identity mismatch')
    old.require(joined.k2.eq(joined.spatial_type).all(),'K2 candidate and frozen disagree')
    old.require(joined.k4.isin([1,2,3,4]).all(),'invalid K4 assignment')
    joined['k2_type']='K2-T'+joined.k2.astype(int).astype(str)
    joined['spatial_type']='K4-C'+joined.k4.astype(int).astype(str)
    return joined.drop(columns=['_merge','crop_frozen','patch_uid_frozen']).sort_values(KEY).reset_index(drop=True)


def support_summary(v,denominator,domain,target,crop,typ):
    pix=int(v.reference_pixels.sum());n=len(v)
    return dict(domain=domain,target=target,crop=crop,spatial_type=typ,n_patches=n,pixels=pix,area_ha=pix*.09,
        patch_fraction=n/len(denominator),area_fraction=pix/denominator.reference_pixels.sum(),
        singleton_count=int(v.reference_pixels.eq(1).sum()),singleton_fraction=v.reference_pixels.eq(1).mean(),
        boundary_pixels=int(v.boundary_pixels.sum()),interior_pixels=int(v.interior_pixels.sum()),
        far_interior_pixels=int(v.far_interior_pixels.sum()),boundary_share=v.boundary_pixels.sum()/pix,
        no_interior_patches=int(v.no_interior.sum()),no_interior_fraction=v.no_interior.mean(),
        edge_patches=int(v.touches_outer_edge.sum()),edge_patch_fraction=v.touches_outer_edge.mean(),
        edge_pixels=int(v.loc[v.touches_outer_edge,'reference_pixels'].sum()),
        edge_area_fraction=v.loc[v.touches_outer_edge,'reference_pixels'].sum()/pix,
        multifold_area_fraction=v.loc[v.oof_fold_count.gt(1),'reference_pixels'].sum()/pix,
        **{m+'_median':v[m].median() for m in old.METRICS})


def reference():
    old.require(not (PROC/'selected_assignments.csv').exists(),'reference stage already saved')
    PROC.mkdir(parents=True,exist_ok=True);SUM.mkdir(parents=True,exist_ok=True)
    unchanged_prior()
    f=read(BASE/'reference_patch_features.csv');a=read(BASE/'cluster_candidates.csv');frozen=read(BASE/'frozen_patch_assignments.csv')
    joined=join_assignments(f,a,frozen)
    check('all 149234 crop assignments',len(joined)==149234)
    write(joined,'selected_assignments',True)
    params=json.loads(record(BASE/'cluster_parameters.json').read_text(encoding='utf-8'))
    reps=[];supports=[];distributions=[];cross=[]
    domains=[('all','all','all',joined)]
    domains += [('crop','all',c,v) for c,v in joined.groupby('crop')]
    domains += [('site_crop',t,c,v) for (t,c),v in joined.groupby(['target','crop'])]
    for domain,target,crop,d in domains:
        for typ in TYPES:
            v=d[d.spatial_type.eq(typ)]
            check('type supported '+str((domain,target,crop,typ)),len(v)>0)
            supports.append(support_summary(v,d,domain,target,crop,typ))
            for m in old.METRICS:
                q=v[m].quantile([0,.05,.25,.5,.75,.95,1]).tolist()
                distributions.append(dict(domain=domain,target=target,crop=crop,spatial_type=typ,metric=m,n=len(v),
                    n_missing=int(v[m].isna().sum()),minimum=q[0],q05=q[1],q25=q[2],median=q[3],q75=q[4],q95=q[5],maximum=q[6]))
        for t2 in ['K2-T1','K2-T2']:
            for t4 in TYPES:
                v=d[d.k2_type.eq(t2)&d.spatial_type.eq(t4)]
                cross.append(dict(domain=domain,target=target,crop=crop,k2_type=t2,k4_type=t4,n_patches=len(v),
                    pixels=int(v.reference_pixels.sum()),area_ha=v.reference_pixels.sum()*.09,
                    patch_fraction=len(v)/len(d),area_fraction=v.reference_pixels.sum()/d.reference_pixels.sum()))
        if domain!='all':
            for typ in TYPES:
                v=d[d.spatial_type.eq(typ)&~d.touches_outer_edge].copy()
                z=(old.feature_matrix(v)-params['center'])/params['scale']
                center=np.asarray(params['centers']['4'])[TYPES.index(typ)]
                distance=((z-center)**2).sum(1)
                v['squared_distance_to_saved_center']=distance
                # Stable tie break uses reference identities only.
                chosen=v.sort_values(['squared_distance_to_saved_center','target','PID']).iloc[0].to_dict()
                reps.append(dict(selection_domain=domain,**chosen))
    write(pd.DataFrame(supports),'type_reference_support');write(pd.DataFrame(distributions),'feature_distributions')
    write(pd.DataFrame(cross),'k2_k4_crosstab');write(pd.DataFrame(reps),'representative_patches')
    # Verify reference-only band supports independently from saved ID and band arrays.
    band_support=[]
    for target in old.SITES:
        with np.load(record(BASE/f'reference_full_{target}.npz')) as r:
            ids=r['ids'];bands=r['bands'];labels=r['label']
            check('reference grid '+target,ids.shape==bands.shape==labels.shape==(2560,2560))
            n=int(ids.max())+1
            bins=np.bincount((ids.astype(np.int64)*7+bands).ravel(),minlength=n*7).reshape(n,7)
            classes=np.full(n,-1,dtype=np.int8)
            for c in range(3):classes[np.unique(ids[labels==c])]=c
            for crop in CROPS:
                z=joined[joined.target.eq(target)&joined.crop.eq(crop)]
                c=old.CLASSES.index(crop);pids=z.PID.to_numpy(int)
                check('reference PID crop/total support '+target+crop,np.all(classes[pids]==c) and np.array_equal(bins[pids].sum(1),z.reference_pixels))
                check('reference boundary/interior '+target+crop,np.array_equal(bins[pids,0],z.boundary_pixels) and np.array_equal(bins[pids,1:].sum(1),z.interior_pixels))
                for typ in TYPES:
                    sub=z[z.spatial_type.eq(typ)].PID.to_numpy(int)
                    for b in range(7):
                        band_support.append(dict(target=target,crop=crop,spatial_type=typ,band=b+1,
                            pixels=int(bins[sub,b].sum()),n_patches_with_support=int((bins[sub,b]>0).sum())))
    write(pd.DataFrame(band_support),'reference_band_support')
    index=read(BASE/'prediction_count_index.csv')
    expected={(k,m,s,t,fold) for t in old.SITES for m in old.MODELS for k in ['within','cross']
              for s in ([t] if k=='within' else [v for v in old.SITES if v!=t]) for fold in ([0] if k=='within' else range(1,6))}
    check('192 explicit prediction identities',len(index)==192 and not index.duplicated(old.RUN).any() and set(index[old.RUN].itertuples(index=False,name=None))==expected)
    settings=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),local_analysis_date='2026-10-07',
        starting_head='d29a228',status='post-main-analysis sensitivity; K2 remains main',selected_k=4,
        reason='Author requested examination of major crop area within saved K4 C3/C4 after K2 analysis.',
        saved_clustering_parameters=params,assignment_source='results/processed/sec33_reference_patch_types/cluster_candidates.csv:k4',
        assignment_key=KEY,regions=REGIONS,comparison='C4 minus C3; same source prediction number; different reference patch sets',
        ref_diagnosis_precedes_new_error_aggregation=True,not_initially_prespecified_main_analysis=True,
        locked_files={str(p.relative_to(ROOT)).replace('\\','/'):old.sha(p) for p in [PROC/'selected_assignments.csv',SUM/'representative_patches.csv',BASE/'cluster_parameters.json',BASE/'cluster_candidates.csv',BASE/'frozen_configuration.json',BASE/'frozen_patch_assignments.csv']})
    json_write(PROC/'analysis_settings.json',settings);finish('reference')
    print(pd.DataFrame(supports).query("domain == 'all'")[['spatial_type','n_patches','area_fraction','AREA_median','SHAPE_median','ENN_median','boundary_share']].to_string(index=False),flush=True)


def verify_selection():
    settings=json.loads(record(PROC/'analysis_settings.json').read_text(encoding='utf-8'))
    for p,h in settings['locked_files'].items():check('selected/reference file unchanged '+p,old.sha(ROOT/p)==h)


def aggregate_array(pc,features):
    """PID indexes the original array; no dependence on feature row order."""
    old.require(np.issubdtype(pc.dtype,np.integer) and (pc>=0).all(),'nonnegative integer counts')
    old.require(pc.ndim==3 and pc.shape[1:]==(7,3),'count array axes')
    old.require(not features.PID.duplicated().any(),'duplicate PID during aggregation')
    old.require(set(features.PID)==set(range(1,len(pc))),'all count PIDs linked exactly once')
    old.require(not pc[0].any(),'PID zero must be empty')
    result=np.zeros((5,3,7,3),dtype=np.int64)
    for (crop,typ),v in features.groupby(['crop','k4']):
        pids=v.PID.to_numpy(int)
        old.require(np.array_equal(pc[pids].sum((1,2)),v.reference_pixels),'per-PID reference support')
        result[int(typ),old.CLASSES.index(crop)]=pc[pids].sum(0,dtype=np.int64)
    old.require(np.array_equal(result.sum((0,1)),pc.sum(0)),'K4 full count closure')
    return result


def aggregate():
    old.require(not (PROC/'type_error_counts.csv').exists(),'aggregation already exists')
    old.require((SUM/'reference_visual_review.md').exists(),'review reference figure before reading counts')
    verify_selection()
    selected=read(PROC/'selected_assignments.csv');features=read(BASE/'reference_patch_features.csv')
    features=features.merge(selected[KEY+['k4']],on=KEY,how='left',validate='one_to_one')
    check('only other class untyped',features.k4.isna().equals(features.crop.eq('other')))
    features['k4']=features.k4.fillna(0).astype(int)
    index=read(BASE/'prediction_count_index.csv');refbands=read(SUM/'reference_band_support.csv')
    rows=[];arrays=[];reference_support={}
    for j,row in enumerate(index.itertuples(index=False)):
        key={k:getattr(row,k) for k in old.RUN};name='/'.join(str(key[k]) for k in old.RUN)
        path=record(BASE/row.file)
        check('input count SHA '+name,old.sha(path)==row.sha256)
        with np.load(path) as archive:
            pc=archive['patch_band_prediction_counts'];oldcm=archive['type_band_bit_cm']
        f=features[features.target.eq(row.target)]
        counts=aggregate_array(pc,f)
        check('K4 restores K2 seven-band full CM '+name,np.array_equal(counts.sum(0),oldcm.sum((0,3))))
        support=counts.sum(-1)
        if row.target not in reference_support:reference_support[row.target]=support
        check('shared K4 support '+name,np.array_equal(support,reference_support[row.target]))
        arrays.append(counts)
        for crop in CROPS:
            c=old.CLASSES.index(crop);fc=f[f.crop.eq(crop)];class_pixels=int(fc.reference_pixels.sum())
            for typ in range(1,5):
                g=fc[fc.k4.eq(typ)];pids=g.PID.to_numpy(int);type_pixels=int(g.reference_pixels.sum())
                saved=refbands[refbands.target.eq(row.target)&refbands.crop.eq(crop)&refbands.spatial_type.eq(TYPES[typ-1])].sort_values('band')
                check('seven-band reference support '+name+crop+str(typ),np.array_equal(support[typ,c],saved.pixels))
                for region,bb in REGIONS.items():
                    vec=counts[typ,c,bb].sum(0);rr=old.rates(vec,c)
                    supported=int((pc[pids][:,bb,:].sum((1,2))>0).sum())
                    rows.append(dict(**key,crop=crop,spatial_type=TYPES[typ-1],region=region,**rr,
                        pred_corn=int(vec[0]),pred_other=int(vec[1]),pred_soybean=int(vec[2]),
                        n_patches=len(g),n_patches_with_support=supported,type_pixels=type_pixels,class_pixels=class_pixels,
                        boundary_share=g.boundary_pixels.sum()/type_pixels,pixel_share_of_class=rr['pixels']/class_pixels))
        if j%24==23:print('aggregated',j+1,'/192',flush=True)
    np.savez_compressed(PROC/'k4_run_type_class_band_cm.npz',counts=np.stack(arrays))
    write(index.assign(array_index=np.arange(len(index))),'prediction_index',True)
    d=pd.DataFrame(rows);write(d,'type_error_counts',True)
    check('all count rows',len(d)==192*2*4*len(REGIONS))
    finish('aggregate')


def contrast_types(d,fields):
    keys=['model','source','target','fold','crop','region']
    a=d[d.spatial_type.eq('K4-C3')].set_index(keys)
    b=d[d.spatial_type.eq('K4-C4')].set_index(keys)
    old.require(a.index.is_unique and b.index.is_unique and set(a.index)==set(b.index),'C3 C4 condition identities')
    support=['pixels','type_pixels','n_patches','n_patches_with_support','boundary_share','class_pixels']
    z=a[fields+support].join(b[fields+support],lsuffix='_C3',rsuffix='_C4',validate='one_to_one')
    for m in fields:z['C4_minus_C3_'+m]=z[m+'_C4']-z[m+'_C3']
    return z.reset_index()


def analyze():
    verify_selection();d=read(PROC/'type_error_counts.csv')
    rates=['leakage','other_crop_rate','other_rate'];fields=['pixels','errors','other_crop_errors','other_errors']+rates
    x=old.join_baseline(d,['region'],fields)
    for col in ['errors','other_crop_errors','other_errors']:
        x['net_'+col]=x['delta_'+col]
        x['contribution_'+col]=x['delta_'+col]/x.class_pixels
    check('two directed rates restore leakage',np.allclose(x.delta_other_crop_rate+x.delta_other_rate,x.delta_leakage,rtol=0,atol=1e-12,equal_nan=True))
    write(x,'type_error_per_prediction',True)
    constants=['pixels','type_pixels','class_pixels','n_patches','n_patches_with_support','boundary_share','pixel_share_of_class','valid_status']+['within_'+m for m in fields if m!='pixels']
    metrics=rates+['delta_'+m for m in rates]+['net_'+m for m in ['errors','other_crop_errors','other_errors']]+['contribution_'+m for m in ['errors','other_crop_errors','other_errors']]
    s=old.strict_summary(x,['model','source','target','crop','spatial_type','region'],metrics,constants)
    write(s,'type_error_summary')
    # No sum of rates used for any closure.
    keys=['model','source','target','fold','crop','spatial_type']
    near=x[x.region.eq('boundary')].set_index(keys).sort_index();inside=x[x.region.eq('interior')].set_index(keys).sort_index();total=x[x.region.eq('all')].set_index(keys).sort_index()
    check('boundary plus interior net count closure',np.array_equal(near.net_errors+inside.net_errors,total.net_errors))
    check('boundary plus interior contribution closure',np.allclose(near.contribution_errors+inside.contribution_errors,total.contribution_errors,rtol=0,atol=1e-12))
    oldx=read(BASE/'type_error_per_prediction.csv');kk=['model','source','target','fold','crop','region']
    oldx['region']=oldx.region.replace(dict(zip(old.BANDS,[f'band_{i+1}' for i in range(7)])))
    newnet=x.groupby(kk).net_errors.sum().sort_index();oldnet=oldx[oldx.region.isin(REGIONS)].groupby(kk).net_added_errors.sum().sort_index()
    check('K4 and K2 whole crop net errors identical',newnet.index.equals(oldnet.index) and np.array_equal(newnet,oldnet))
    cfields=['within_'+m for m in rates]+rates+['delta_'+m for m in rates]+['net_errors','contribution_errors']
    contrasts=contrast_types(x,cfields);write(contrasts,'C4_minus_C3_per_prediction',True)
    cs=old.strict_summary(contrasts,['model','source','target','crop','region'],
        [m for m in contrasts if m.startswith('C4_minus_C3_')],
        [m for m in contrasts if m.startswith(('pixels_','type_pixels_','n_patches_','boundary_share_','class_pixels_','within_'))])
    write(cs,'C4_minus_C3_summary')
    for m in rates:
        expected=(s[s.spatial_type.eq('K4-C4')].set_index(['model','source','target','crop','region'])['delta_'+m+'_mean']-
                  s[s.spatial_type.eq('K4-C3')].set_index(['model','source','target','crop','region'])['delta_'+m+'_mean']).sort_index()
        check('mean of explicit differences '+m,np.allclose(expected,cs.set_index(['model','source','target','crop','region'])['C4_minus_C3_delta_'+m+'_mean'].sort_index(),rtol=0,atol=1e-12,equal_nan=True))
    # Crop comparison retains the same type/region but different reference crop sets.
    ck=['model','source','target','fold','spatial_type','region']
    a=x[x.crop.eq('corn')].set_index(ck);b=x[x.crop.eq('soybean')].set_index(ck)
    cm=a[['leakage','within_leakage','delta_leakage']].join(b[['leakage','within_leakage','delta_leakage']],lsuffix='_corn',rsuffix='_soybean',validate='one_to_one')
    for m in ['leakage','within_leakage','delta_leakage']:cm['soybean_minus_corn_'+m]=cm[m+'_soybean']-cm[m+'_corn']
    cm=cm.reset_index();write(cm,'crop_comparison_per_prediction',True)
    write(old.strict_summary(cm,ck[:-3]+['spatial_type','region'],[m for m in cm if m.startswith('soybean_minus_corn_')],[]),'crop_comparison_summary')
    # Condition-matched model/source ranges, with all means retained elsewhere.
    comparisons=[]
    for dimension,keys2 in [('model',['source','target','crop','spatial_type','region']),('source',['model','target','crop','spatial_type','region'])]:
        for key,v in s.groupby(keys2):
            old.require(len(v)==3,'three '+dimension+' levels')
            r=dict(dimension=dimension,**dict(zip(keys2,key)))
            for m in ['leakage_mean','delta_leakage_mean','delta_other_crop_rate_mean','delta_other_rate_mean']:
                r[m+'_range']=v[m].max()-v[m].min() if v[m].notna().all() else np.nan
                r[m+'_ascending_order']=';'.join(v.sort_values([m,dimension])[dimension]) if v[m].notna().all() else 'not_calculable'
            comparisons.append(r)
    write(pd.DataFrame(comparisons),'model_source_comparisons')
    write(s[s.target.eq('il_2023')&s.crop.eq('soybean')],'D_soybean_review')
    write(x[x.target.eq('il_2023')&x.crop.eq('soybean')],'D_soybean_per_prediction',True)
    exceptions=cs[(cs.C4_minus_C3_delta_leakage_mean<=0)|cs.C4_minus_C3_delta_leakage_direction.ne('all_positive')]
    write(exceptions,'C4_C3_nonpositive_or_mixed_inventory')
    inventory=[]
    for region,v in s.groupby('region'):
        for m in ['delta_leakage','delta_other_crop_rate','delta_other_rate']:
            inventory.append(dict(region=region,metric=m,n=len(v),n_na=int(v[m+'_mean'].isna().sum()),n_negative=int(v[m+'_mean'].lt(0).sum()),n_zero=int(v[m+'_mean'].eq(0).sum()),n_mixed=int(v[m+'_direction'].eq('mixed').sum())))
    write(pd.DataFrame(inventory),'na_negative_inventory');finish('analyze')


def audit():
    """Independent identity/count/figure checks and compact descriptive tables."""
    verify_selection()
    index=read(PROC/'prediction_index.csv');f=read(PROC/'selected_assignments.csv')
    check('index unique and ordered array axis',len(index)==192 and not index.duplicated(old.RUN).any() and np.array_equal(index.array_index,np.arange(192)))
    expected={(k,m,s,t,fold) for t in old.SITES for m in old.MODELS for k in ['within','cross']
              for s in ([t] if k=='within' else [v for v in old.SITES if v!=t]) for fold in ([0] if k=='within' else range(1,6))}
    check('all expected run identities',set(index[old.RUN].itertuples(index=False,name=None))==expected)
    allcm=np.load(record(PROC/'k4_run_type_class_band_cm.npz'))['counts']
    whole=read(old.OLD/'whole_cm.csv').set_index(old.RUN)
    cols=[f'cm_{i}_{j}' for i in range(3) for j in range(3)]
    for row in index.itertuples(index=False):
        key=tuple(getattr(row,c) for c in old.RUN);name=str(key)
        with np.load(record(BASE/row.file)) as arc:
            check('saved PID axis '+name,np.array_equal(arc['PID'],np.arange(len(arc['patch_band_prediction_counts']))))
        check('192 full three-class CM '+name,np.array_equal(allcm[row.array_index].sum((0,2)),whole.loc[key,cols].to_numpy(int).reshape(3,3)))
    d=read(PROC/'type_error_counts.csv')
    check('unique type rate identities',not d.duplicated(old.RUN+['crop','spatial_type','region']).any())
    lookup=index.set_index(old.RUN).array_index
    for region,bb in REGIONS.items():
        z=d[d.region.eq(region)]
        computed=np.array([
            allcm[int(lookup.loc[tuple(getattr(r,c) for c in old.RUN)]),
                  TYPES.index(r.spatial_type)+1,old.CLASSES.index(r.crop),bb].sum(0)
            for r in z.itertuples(index=False)
        ])
        check('rate-table integer counts '+region,np.array_equal(computed,z[['pred_corn','pred_other','pred_soybean']].to_numpy(int)))
        n=computed.sum(1);class_index=z.crop.map({'corn':0,'soybean':2}).to_numpy(int)
        correct=computed[np.arange(len(computed)),class_index]
        leakage=np.divide(n-correct,n,out=np.full(len(n),np.nan),where=n!=0)
        check('rate denominator and NA '+region,np.allclose(leakage,z.leakage,rtol=0,atol=1e-12,equal_nan=True))
    s=read(SUM/'type_error_summary.csv');cs=read(SUM/'C4_minus_C3_summary.csv')
    x=read(PROC/'type_error_per_prediction.csv');cx=read(PROC/'C4_minus_C3_per_prediction.csv')
    pairkeys=['model','source','target','fold','crop','region']
    c3=x[x.spatial_type.eq('K4-C3')].set_index(pairkeys).sort_index()
    c4=x[x.spatial_type.eq('K4-C4')].set_index(pairkeys).sort_index()
    pair=cx.set_index(pairkeys).sort_index()
    check('C3/C4 explicit run and condition identity',c3.index.equals(c4.index) and pair.index.equals(c3.index))
    for metric in ['within_leakage','leakage','delta_leakage','delta_other_crop_rate','delta_other_rate','net_errors']:
        col='C4_minus_C3_'+metric
        check('independent C4 minus C3 '+metric,np.allclose(c4[metric]-c3[metric],pair[col],rtol=0,atol=1e-12,equal_nan=True))
        pv=cx.pivot(index=['model','source','target','crop','region'],columns='fold',values=col).reindex(columns=[1,2,3,4,5])
        arr=pv.to_numpy();summary=cs.set_index(['model','source','target','crop','region']).loc[pv.index]
        for suffix,expected in [('mean',np.mean(arr,axis=1)),('std',np.std(arr,axis=1,ddof=1)),
                                ('min',np.min(arr,axis=1)),('max',np.max(arr,axis=1))]:
            check('independent C4/C3 five-value '+metric+' '+suffix,np.allclose(expected,summary[col+'_'+suffix],rtol=0,atol=1e-12,equal_nan=True))
    # Independently check saved summary means and sample standard deviations.
    keys=['model','source','target','crop','spatial_type','region']
    for metric in ['leakage','delta_leakage','delta_other_crop_rate','delta_other_rate','net_errors']:
        expected=x.pivot(index=keys,columns='fold',values=metric).reindex(columns=[1,2,3,4,5])
        a=expected.to_numpy();mu=np.mean(a,axis=1);sd=np.std(a,axis=1,ddof=1);z=s.set_index(keys).loc[expected.index]
        check('independent five-value means '+metric,np.allclose(mu,z[metric+'_mean'],atol=1e-12,rtol=0,equal_nan=True))
        check('independent sample SD '+metric,np.allclose(sd,z[metric+'_std'],atol=1e-12,rtol=0,equal_nan=True))
    p=read(SUM/'figure2_plot_data.csv');cl=cs.set_index(['model','source','target','crop','region'])
    for row in p.itertuples():
        value=cl.loc[(row.model,row.source,row.target,row.crop,row.region),row.metric]
        check('figure2 cell '+str(row.Index),np.isclose(value,row.value,rtol=0,atol=1e-12,equal_nan=True))
    fd=read(SUM/'figure1_distribution_data.csv')
    for r in fd.itertuples():
        vals=f[f.crop.eq(r.crop)&f.spatial_type.eq(r.spatial_type)][r.metric].quantile([.05,.25,.5,.75,.95])
        check('figure1 quantiles '+str((r.crop,r.spatial_type,r.metric)),np.allclose(vals,[r.q05,r.q25,r.median,r.q75,r.q95],rtol=0,atol=1e-12))
    counts=[]
    for region,v in cs.groupby('region'):
        for metric in ['within_leakage','leakage','delta_leakage','delta_other_crop_rate','delta_other_rate','net_errors']:
            z=v.drop_duplicates(['model','target','crop']) if metric=='within_leakage' else v
            col='C4_minus_C3_'+metric
            row=dict(region=region,metric=metric,n=len(z),positive=int(z[col+'_mean'].gt(0).sum()),negative=int(z[col+'_mean'].lt(0).sum()),
                zero=int(z[col+'_mean'].eq(0).sum()),n_na=int(z[col+'_mean'].isna().sum()),minimum=z[col+'_mean'].min(),median=z[col+'_mean'].median(),maximum=z[col+'_mean'].max())
            if metric!='within_leakage':row.update({k:int(z[col+'_direction'].eq(k).sum()) for k in ['all_positive','all_negative','all_zero','mixed','not_calculable']})
            counts.append(row)
    write(pd.DataFrame(counts),'comparison_direction_counts')
    allregions=['all','boundary','interior','far_interior']
    write(cs[cs.region.isin(allregions)],'C4_C3_main_regions_complete')
    source=[]
    for key,v in cs.groupby(['model','target','crop','region']):
        col='C4_minus_C3_delta_leakage_mean';a=v[col]
        source.append(dict(zip(['model','target','crop','region'],key),n_sources=len(v),
            direction='C4_higher_all_sources' if a.gt(0).all() else 'C3_higher_all_sources' if a.lt(0).all() else 'varies_by_source',
            minimum=a.min(),maximum=a.max(),**{old.SITES[r.source]:getattr(r,col) for r in v.itertuples()}))
    write(pd.DataFrame(source),'source_sign_consistency')
    target=[]
    for key,v in cs[cs.region.eq('all')].groupby(['target','crop']):
        a=v.C4_minus_C3_delta_leakage_mean
        target.append(dict(target=key[0],crop=key[1],n=len(v),C4_higher=int(a.gt(0).sum()),C3_higher=int(a.lt(0).sum()),minimum=a.min(),maximum=a.max(),
            all_five_C4_higher=int(v.C4_minus_C3_delta_leakage_direction.eq('all_positive').sum()),all_five_C3_higher=int(v.C4_minus_C3_delta_leakage_direction.eq('all_negative').sum())))
    write(pd.DataFrame(target),'target_crop_direction_counts')
    cr=read(SUM/'crop_comparison_summary.csv');crop_rows=[]
    for (typ,region),v in cr.groupby(['spatial_type','region']):
        for metric in ['within_leakage','leakage','delta_leakage']:
            z=v.drop_duplicates(['model','target']) if metric=='within_leakage' else v
            col='soybean_minus_corn_'+metric+'_mean'
            crop_rows.append(dict(spatial_type=typ,region=region,metric=metric,n=len(z),soybean_higher=int(z[col].gt(0).sum()),corn_higher=int(z[col].lt(0).sum()),n_na=int(z[col].isna().sum())))
    write(pd.DataFrame(crop_rows),'crop_order_counts')
    cropkeys=['model','source','target','region']
    crop3=cr[cr.spatial_type.eq('K4-C3')].set_index(cropkeys)
    crop4=cr[cr.spatial_type.eq('K4-C4')].set_index(cropkeys)
    crop_change=crop3.join(crop4,lsuffix='_C3',rsuffix='_C4',validate='one_to_one')
    for metric in ['within_leakage','leakage','delta_leakage']:
        a=crop_change['soybean_minus_corn_'+metric+'_mean_C3'];z=crop_change['soybean_minus_corn_'+metric+'_mean_C4']
        crop_change[metric+'_crop_order_changes']=(a*z<0).where(a.notna()&z.notna())
    keep=[c for c in crop_change if c.startswith('soybean_minus_corn_') and c.endswith(('_mean_C3','_mean_C4')) or c.endswith('_crop_order_changes')]
    write(crop_change[keep].reset_index(),'crop_C3_C4_order_changes')
    joined=cs[cs.region.eq('boundary')].set_index(['model','source','target','crop']).join(
        cs[cs.region.eq('interior')].set_index(['model','source','target','crop']),lsuffix='_boundary',rsuffix='_interior',validate='one_to_one')
    pattern=[]
    for metric in ['leakage','delta_leakage','delta_other_crop_rate','delta_other_rate']:
        b=joined['C4_minus_C3_'+metric+'_mean_boundary'];i=joined['C4_minus_C3_'+metric+'_mean_interior']
        pattern.append(dict(metric=metric,n=len(joined),boundary_lower_interior_higher=int((b.lt(0)&i.gt(0)).sum()),boundary_higher_interior_lower=int((b.gt(0)&i.lt(0)).sum()),same_sign=int((b*i>0).sum())))
    write(pd.DataFrame(pattern),'boundary_interior_sign_patterns')
    # Fixed D soybean review includes every source/model, and each direction remains explicit.
    dz=x[x.target.eq('il_2023')&x.crop.eq('soybean')&x.region.isin(allregions)&x.spatial_type.isin(TYPES[2:])].copy()
    write(dz,'D_C3_C4_diagnostic_per_prediction')
    v=cs[cs.region.eq('all')].copy()
    v['directed_increment_signs_opposite']=v.C4_minus_C3_delta_other_crop_rate_mean*v.C4_minus_C3_delta_other_rate_mean<0
    v['abs_vs_increment_signs_opposite']=v.C4_minus_C3_leakage_mean*v.C4_minus_C3_delta_leakage_mean<0
    write(v[['model','source','target','crop','directed_increment_signs_opposite','abs_vs_increment_signs_opposite']],'direction_disagreements')
    finish('audit')


def seal():
    verify_selection();unchanged_prior();finish('final_integrity')
    paths=[p for directory in [PROC,SUM,FIG] for p in directory.rglob('*') if p.is_file() and p.name!='delivery_manifest.json']
    paths += [Path(__file__),ROOT/'scripts/plot_sec33_k4_sensitivity.py',ROOT/'scripts/test/test_sec33_k4_sensitivity.py',
              ROOT/'plan/tasks/2026-10-07-sec33-k4-sensitivity.md',ROOT/'verification/sec33-k4-sensitivity-2026-10-07.md',
              ROOT/'scripts/.gitattributes',ROOT/'plan/tasks/.gitattributes',ROOT/'verification/.gitattributes']
    json_write(SUM/'delivery_manifest.json',dict(created_at_utc=datetime.now(timezone.utc).isoformat(),
        data_status='derived / exploratory',artifacts=[dict(path=p.relative_to(ROOT).as_posix(),sha256=old.sha(p),bytes=p.stat().st_size) for p in paths]))
    print('sealed',len(paths),'files')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['reference','aggregate','analyze','audit','seal'])
    globals()[parser.parse_args().stage]()

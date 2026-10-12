"""Bounded C/D soybean finding refinement using saved full-patch counts.

Compare shape groups with identical reference-only weights, separate outgoing
directions and natural count contributions, and test distance/AREA coarsening.
No retraining, inference, image generation, distance generation or paper edits.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from sec33_metrics import RUN, SITE_LABELS, five_stats

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'results/processed/sec33_reference_patch_types'
OLD=ROOT/'results/summary/spatial_error_conditions'
OP=ROOT/'results/processed/spatial_error_conditions'
OUT=ROOT/'results/summary/spatial_findings_refinement'
PROC=ROOT/'results/processed/spatial_findings_refinement'
TARGETS=['ida_2023','il_2023']
COMMON_SOURCES=['iw_2023','iw2_2023']
MODELS=['convgru','unet3d','utae']
COARSE=[0,10,50,100,200,500,np.inf]
FINE=[0,1,10,25,50,75,100,150,200,350,500,1000,np.inf]
THREE=[(0,),(1,2,3,4,5),(6,)]
SEVEN=[(i,) for i in range(7)]
SCHEMES={'a6d3':(COARSE,THREE),'a6d7':(COARSE,SEVEN),'a12d7':(FINE,SEVEN)}
RULES={'primary':(10,1000),'all_supported':(1,1)}
INPUTS={}
CHECKS=[]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def read(path):
    INPUTS[path.relative_to(ROOT).as_posix()]=sha(path)
    return pd.read_csv(path,float_precision='round_trip')


def save(frame,name,processed=False):
    folder=PROC if processed else OUT
    folder.mkdir(parents=True,exist_ok=True)
    frame.to_csv(folder/(name+'.csv'),index=False,float_format='%.17g',lineterminator='\n')


def check(name,condition,detail=''):
    ok=bool(condition)
    CHECKS.append(dict(check=name,status='Verified' if ok else 'Not verified',detail=str(detail)))
    if not ok:raise ValueError(name+': '+str(detail))


def divide(n,d):
    n,d=np.broadcast_arrays(np.asarray(n,float),np.asarray(d,float))
    return np.divide(n,d,out=np.full(n.shape,np.nan),where=d!=0)


def stats(frame,keys,values):
    rows=[]
    for key,g in frame.groupby(keys,sort=True,dropna=False):
        if len(g)!=5 or set(g.fold)!={1,2,3,4,5}:raise ValueError(('five predictions',key))
        row=dict(zip(keys,key))|{'n_predictions':5}
        for col in values:row.update(five_stats(g[col],col))
        rows.append(row)
    return pd.DataFrame(rows)


def make_cells(f,counts,scheme):
    edges,bands=SCHEMES[scheme]
    area=np.searchsorted(edges[1:-1],f.AREA,side='right')
    arm=(f.SHAPE>=2).to_numpy(int)
    n_a,n_d=len(edges)-1,len(bands)
    codes=arm*n_a+area
    cube=np.zeros((2*n_a,n_d,3),np.int64)
    supports=np.zeros((2*n_a,n_d,5),float)
    for d,bb in enumerate(bands):
        cc=counts[:,bb,:].sum(axis=1)
        n=cc.sum(axis=1)
        np.add.at(cube[:,d,:],codes,cc)
        for j,v in enumerate([(n>0).astype(int),n*np.log(f.AREA),n*f.ENN,
                              n*f.touches_outer_edge,n*f.reference_pixels.eq(1)]):
            np.add.at(supports[:,d,j],codes,v)
    rows=[]
    for h,a,d in itertools.product(range(2),range(n_a),range(n_d)):
        c=cube[h*n_a+a,d]
        s=supports[h*n_a+a,d]
        hi=edges[a+1]
        label=(f'<{hi:g}' if a==0 else f'>={edges[a]:g}' if np.isinf(hi) else f'{edges[a]:g}-<{hi:g}')
        ds=bands[d]
        dl='d>6' if ds==(6,) else '1<d<=6' if len(ds)>1 else f'{ds[0]}<d<={ds[0]+1}'
        rows.append(dict(scheme=scheme,arm=h,area_bin=a,area_label=label,distance_bin=d,distance_label=dl,
            stratum=a*n_d+d,pixels=int(c.sum()),to_corn=int(c[0]),to_other=int(c[1]),to_soybean=int(c[2]),
            patch_count=int(s[0]),log_area_pixel_sum=float(s[1]),enn_pixel_sum=float(s[2]),
            outer_edge_pixels=int(s[3]),singleton_pixels=int(s[4])))
    return pd.DataFrame(rows)


def build_counts():
    f=read(REF/'reference_patch_features.csv')
    index=read(REF/'prediction_count_index.csv')
    index=index[index.target.isin(TARGETS)].copy()
    oldwhole=read(OP/'whole_crop_per_prediction.csv')
    lookup=oldwhole[oldwhole.crop.eq('soybean')].set_index(RUN)
    check('96 target C/D identities',len(index)==96 and not index.duplicated(RUN).any())
    frames=[]
    for target in TARGETS:
        ff=f[(f.target==target)&(f.crop=='soybean')].sort_values('PID').copy()
        check('complete valid soybean features '+target,not ff.PID.duplicated().any() and
              np.isfinite(ff[['AREA','SHAPE','ENN']]).all().all() and ff.SHAPE.ge(1).all() and
              np.allclose(ff.AREA,ff.reference_pixels*.09,atol=1e-9,rtol=0))
        for r in index[index.target.eq(target)].itertuples(index=False):
            path=REF/r.file
            digest=sha(path)
            INPUTS[path.relative_to(ROOT).as_posix()]=digest
            check('saved NPZ hash '+r.file,digest==r.sha256)
            with np.load(path) as z:
                at=pd.Index(z['PID']).get_indexer(ff.PID)
                check('explicit PID join '+r.file,(at>=0).all() and len(np.unique(at))==len(ff))
                cc=z['patch_band_prediction_counts'][at].astype(np.int64)
            check('reference count '+r.file,(cc>=0).all() and np.array_equal(cc.sum(axis=(1,2)),ff.reference_pixels))
            run={k:getattr(r,k) for k in RUN}
            truth=lookup.loc[tuple(run.values())]
            check('soybean whole matrix row '+r.file,cc[:,:,2].sum()==truth.tp and cc[:,:,:2].sum()==truth.fn)
            for scheme in SCHEMES:
                frame=make_cells(ff,cc,scheme)
                for k,v in run.items():frame[k]=v
                frames.append(frame)
        print('Read 48 saved predictions for '+SITE_LABELS[target],flush=True)
    allcells=pd.concat(frames,ignore_index=True)
    sfields=['pixels','patch_count','log_area_pixel_sum','enn_pixel_sum','outer_edge_pixels','singleton_pixels']
    refkey=['target','scheme','arm','stratum']
    check('invariant target reference support',allcells.groupby(refkey)[sfields].nunique(dropna=False).le(1).all().all())
    ref=allcells[refkey+['area_bin','area_label','distance_bin','distance_label']+sfields].drop_duplicates()
    check('unique reference cells',not ref.duplicated(refkey).any())
    ref['area_ha']=ref.pixels*.09
    ref['pixel_share_of_crop']=ref.pixels/ref.groupby(['target','scheme']).pixels.transform('sum')
    save(ref,'reference_cells')
    save(allcells.drop(columns=sfields[1:]),'cell_counts_per_prediction',True)
    return allcells,ref,oldwhole,f


def build_weights(ref):
    rows=[]
    cover=[]
    for scheme in SCHEMES:
        for scope in ['within_target','joint_CD']:
            for pool in [[t] for t in TARGETS] if scope=='within_target' else [TARGETS]:
                sub=ref[(ref.scheme==scheme)&ref.target.isin(pool)]
                n=sub.pivot(index='stratum',columns=['target','arm'],values='pixels')
                patches=sub.pivot(index='stratum',columns=['target','arm'],values='patch_count')
                shares=n/n.sum(axis=0)
                for rule,(pm,nm) in RULES.items():
                    eligible=((n>=nm)&(patches>=pm)).all(axis=1)
                    raw=shares.min(axis=1)*eligible
                    check(f'nonzero common support {scope} {scheme} {rule} {pool}',raw.sum()>0)
                    weight=raw/raw.sum()
                    check(f'normalized common weights {scope} {scheme} {rule} {pool}',abs(weight.sum()-1)<1e-12)
                    for r in sub.itertuples(index=False):
                        rows.append(dict(target=r.target,scheme=scheme,scope=scope,rule=rule,arm=r.arm,
                            stratum=r.stratum,area_label=r.area_label,distance_label=r.distance_label,
                            pixels=r.pixels,patch_count=r.patch_count,eligible=bool(eligible.loc[r.stratum]),
                            weight=float(weight.loc[r.stratum])))
                    for t,h in n.columns:
                        rr=sub[(sub.target==t)&(sub.arm==h)].set_index('stratum').loc[weight.index]
                        good=eligible.to_numpy()
                        wg=weight[eligible]
                        geom=np.exp(np.sum(wg*rr.loc[eligible,'log_area_pixel_sum']/rr.loc[eligible,'pixels']))
                        enn=np.sum(wg*rr.loc[eligible,'enn_pixel_sum']/rr.loc[eligible,'pixels'])
                        cover.append(dict(target=t,scheme=scheme,scope=scope,rule=rule,arm=h,
                            total_pixels=int(n[t,h].sum()),retained_pixels=int(n.loc[eligible,(t,h)].sum()),
                            excluded_pixels=int(n.loc[~eligible,(t,h)].sum()),coverage=float(n.loc[eligible,(t,h)].sum()/n[t,h].sum()),
                            common_strata=int(eligible.sum()),total_strata=len(eligible),overlap_mass=float(raw.sum()),
                            matched_geometric_area_ha=float(geom),matched_mean_enn_m=float(enn)))
    w=pd.DataFrame(rows);coverage=pd.DataFrame(cover)
    save(w,'common_support_weights');save(coverage,'coverage_and_reference_balance')
    return w,coverage


def compute_gaps(cells,weights):
    rows=[]
    for key,g in cells.groupby(RUN+['scheme'],sort=False):
        run=dict(zip(RUN+['scheme'],key))
        refw=weights[(weights.target==run['target'])&(weights.scheme==run['scheme'])]
        for (scope,rule),ww in refw.groupby(['scope','rule']):
            use=g.merge(ww[['arm','stratum','eligible','weight']],on=['arm','stratum'],validate='one_to_one')
            use=use[use.eligible]
            row=run|dict(scope=scope,rule=rule)
            for name,count in [('corn','to_corn'),('other','to_other')]:
                value=use.assign(v=use.weight*use[count]/use.pixels).groupby('arm').v.sum()
                row['low_'+name]=float(value.loc[0]);row['high_'+name]=float(value.loc[1])
                row['gap_'+name]=row['high_'+name]-row['low_'+name]
            for side in ['low','high','gap']:row[side+'_omission']=row[side+'_corn']+row[side+'_other']
            rows.append(row)
    out=pd.DataFrame(rows)
    bk=['model','target','scheme','scope','rule']
    vals=[f'{side}_{metric}' for side in ['low','high','gap'] for metric in ['corn','other','omission']]
    baseline=out[out.kind.eq('within')][bk+vals].rename(columns={v:'within_'+v for v in vals})
    out=out.merge(baseline,on=bk,validate='many_to_one')
    for v in vals:out['delta_'+v]=out[v]-out['within_'+v]
    check('gap directions close',np.allclose(out.delta_gap_corn+out.delta_gap_other,out.delta_gap_omission,atol=1e-14,rtol=0))
    old=read(OP/'conditional_contrasts_per_prediction.csv')
    old=old[(old.crop=='soybean')&(old.contrast_name=='shape_control_area_distance')&old.target.isin(TARGETS)]
    ours=out[(out.scheme=='a6d3')&(out.scope=='within_target')]
    keys=RUN+['rule']
    both=ours.merge(old,on=keys,validate='one_to_one',suffixes=('','_old'))
    check('original coarse definition complete',len(both)==192 and len(ours)==len(old))
    check('replicate original within-target contrast',np.allclose(both.gap_omission,both.contrast,atol=1e-12,rtol=0) and
          np.allclose(both.delta_gap_omission,both.delta_contrast,atol=1e-12,rtol=0))
    save(out,'standardized_rates_per_prediction',True)
    save(out[out.kind.eq('within')],'within_standardized_rates')
    summary=stats(out[out.kind.eq('cross')],['model','source','target','scheme','scope','rule'],vals+['delta_'+v for v in vals])
    save(summary,'cross_standardized_rates')
    return out,summary


def natural_contributions(cells,oldwhole,features):
    sub=cells[cells.scheme.eq('a6d7')]
    keys=RUN+['arm']
    r=sub.groupby(keys,as_index=False)[['pixels','to_corn','to_other','to_soybean']].sum()
    r['fn']=r.to_corn+r.to_other
    fields=['to_corn','to_other','fn']
    bk=['model','target','arm']
    b=r[r.kind.eq('within')][bk+fields].rename(columns={c:'within_'+c for c in fields})
    r=r.merge(b,on=bk,validate='many_to_one')
    w=oldwhole[(oldwhole.target.isin(TARGETS))&(oldwhole.crop=='soybean')][RUN+['pixels','fn','baseline_fn']]
    w=w.rename(columns={'pixels':'whole_pixels','fn':'whole_fn','baseline_fn':'whole_within_fn'})
    r=r.merge(w,on=RUN,validate='many_to_one')
    f=features[features.target.isin(TARGETS)&features.crop.eq('soybean')].copy()
    f['arm']=(f.SHAPE>=2).astype(int)
    support=f.groupby(['target','arm'],as_index=False).agg(patch_count=('PID','size'),reference_pixels=('reference_pixels','sum'))
    r=r.merge(support,on=['target','arm'],validate='many_to_one')
    check('natural group reference closure',np.array_equal(r.pixels,r.reference_pixels))
    r['area_ha']=r.pixels*.09
    for c in fields:
        r['delta_'+c]=r[c]-r['within_'+c]
        r[c+'_rate']=r[c]/r.pixels
        r['within_'+c+'_rate']=r['within_'+c]/r.pixels
        r['delta_'+c+'_rate']=r['delta_'+c]/r.pixels
        r['net_'+c+'_contribution']=r['delta_'+c]/r.whole_pixels
    r['area_share']=r.pixels/r.whole_pixels
    check('natural FN closure',np.array_equal(r.groupby(RUN).fn.sum().values,w.set_index(RUN).sort_index().whole_fn.values))
    save(r,'natural_shape_counts_per_prediction',True)
    save(r[r.kind.eq('within')],'within_natural_shape_counts')
    valuecols=fields+['delta_'+c for c in fields]+[c+'_rate' for c in fields]+['delta_'+c+'_rate' for c in fields]+['net_'+c+'_contribution' for c in fields]
    summary=stats(r[r.kind.eq('cross')],['model','source','target','arm'],valuecols)
    supp=r[['target','arm','pixels','patch_count','area_ha','area_share']].drop_duplicates()
    summary=summary.merge(supp,on=['target','arm'],validate='many_to_one')
    total=summary.groupby(['model','source','target']).delta_fn_mean.transform('sum')
    summary['ratio_of_mean_fn_net']=divide(summary.delta_fn_mean,total)
    save(summary,'cross_natural_shape_counts')
    return r,summary


def stratum_contributions(cells,weights,gaps):
    sub=cells[cells.kind.eq('cross')].copy()
    w=weights[(weights.scope=='joint_CD')&(weights.rule=='primary')]
    sub=sub.merge(w[['target','scheme','arm','stratum','eligible','weight']],on=['target','scheme','arm','stratum'],validate='many_to_one')
    bk=['model','target','scheme','arm','stratum']
    base=cells[cells.kind.eq('within')][bk+['to_corn','to_other']].rename(columns={c:'within_'+c for c in ['to_corn','to_other']})
    sub=sub.merge(base,on=bk,validate='many_to_one')
    # Keep excluded cells with weight zero and explicit eligibility, never NaN*0.
    for v in ['corn','other']:
        sub['delta_'+v+'_rate']=divide(sub['to_'+v]-sub['within_to_'+v],sub.pixels)
    keys=RUN+['scheme','stratum','area_label','distance_label']
    lo=sub[sub.arm.eq(0)].set_index(keys)
    hi=sub[sub.arm.eq(1)].set_index(keys).loc[lo.index]
    out=lo[['eligible','weight']].copy()
    for v in ['corn','other']:
        out['low_delta_'+v]=lo['delta_'+v+'_rate']
        out['high_delta_'+v]=hi['delta_'+v+'_rate']
        out['gap_'+v+'_contribution']=np.where(out.eligible,out.weight*(out['high_delta_'+v]-out['low_delta_'+v]),0)
    out['gap_omission_contribution']=out.gap_corn_contribution+out.gap_other_contribution
    out=out.reset_index()
    restored=out.groupby(RUN+['scheme']).gap_omission_contribution.sum().sort_index()
    truth=gaps[(gaps.scope=='joint_CD')&(gaps.rule=='primary')&(gaps.kind=='cross')].set_index(RUN+['scheme']).delta_gap_omission.sort_index()
    check('stratum contributions restore standardized gap',restored.index.equals(truth.index) and np.allclose(restored,truth,atol=1e-12,rtol=0))
    save(out,'stratum_gap_contributions_per_prediction',True)
    avg=out.groupby(['model','source','target','scheme','area_label','distance_label'],as_index=False)[['weight','gap_corn_contribution','gap_other_contribution','gap_omission_contribution']].mean()
    save(avg,'stratum_gap_contributions')


def reading_tables(gaps,summary,coverage,natural):
    old=read(OLD/'cross_conditional_contrasts.csv')
    picture=old[(old.contrast_name=='shape_control_area_distance')&(old.rule=='primary')].copy()
    cols=['model','source','target','crop','contrast_mean','delta_contrast_mean','delta_contrast_positive','delta_contrast_negative','low_coverage','high_coverage']
    save(picture[cols],'all_paths_candidate_context')
    rows=[]
    for key,g in summary.groupby(['scheme','scope','rule','target']):
        for sources in ['all_available','common_AB']:
            sub=g if sources=='all_available' else g[g.source.isin(COMMON_SOURCES)]
            vals={v:sub[v] for v in ['delta_gap_omission_mean','delta_gap_corn_mean','delta_gap_other_mean']}
            rows.append(dict(zip(['scheme','scope','rule','target'],key))|dict(sources=sources,
                n_model_source=len(sub),positive_mean=int((vals['delta_gap_omission_mean']>0).sum()),
                all5_positive=int(sub.delta_gap_omission_positive.eq(5).sum()),all5_negative=int(sub.delta_gap_omission_negative.eq(5).sum()),
                delta_gap_min=float(vals['delta_gap_omission_mean'].min()),delta_gap_max=float(vals['delta_gap_omission_mean'].max()),
                corn_min=float(vals['delta_gap_corn_mean'].min()),corn_max=float(vals['delta_gap_corn_mean'].max()),
                other_min=float(vals['delta_gap_other_mean'].min()),other_max=float(vals['delta_gap_other_mean'].max())))
    save(pd.DataFrame(rows),'candidate_consistency')
    c=gaps[(gaps.kind=='cross')&(gaps.scope=='joint_CD')&gaps.source.isin(COMMON_SOURCES)]
    keys=['model','source','fold','scheme','rule']
    left=c[c.target=='ida_2023'].set_index(keys)
    right=c[c.target=='il_2023'].set_index(keys).loc[left.index]
    pair=left.index.to_frame(index=False)
    for metric in ['omission','corn','other']:
        pair['C_delta_gap_'+metric]=left['delta_gap_'+metric].values
        pair['D_delta_gap_'+metric]=right['delta_gap_'+metric].values
        pair['C_minus_D_'+metric]=pair['C_delta_gap_'+metric]-pair['D_delta_gap_'+metric]
    save(pair,'paired_C_D_per_prediction',True)
    save(stats(pair,['model','source','scheme','rule'],[c for c in pair.columns if c not in keys]),'paired_C_D_summary')
    f1=read(OLD/'cross_whole_crop.csv')
    f1=f1[f1.target.isin(TARGETS)&f1.crop.isin(['corn','soybean'])]
    fc=['model','source','target','crop','f1_mean','delta_f1_mean','delta_recall_mean','delta_precision_mean','delta_fn_mean','delta_fp_mean','delta_fn_loss_mean','delta_fp_loss_mean']
    save(f1[fc],'whole_F1_context')
    focus=summary[(summary.scope=='joint_CD')&(summary.rule=='primary')&summary.source.isin(COMMON_SOURCES)].copy()
    fk=['model','source','target','scheme','scope','rule']
    values=['low_omission_mean','high_omission_mean','gap_omission_mean','gap_omission_positive','gap_omission_negative',
            'delta_low_omission_mean','delta_high_omission_mean','delta_gap_omission_mean','delta_gap_corn_mean','delta_gap_other_mean',
            'delta_gap_omission_min','delta_gap_omission_max','delta_gap_omission_positive','delta_gap_omission_negative']
    focus=focus[fk+values]
    base=gaps[gaps.kind.eq('within')][['model','target','scheme','scope','rule','gap_omission']].rename(columns={'gap_omission':'within_gap_omission'})
    focus=focus.merge(base,on=['model','target','scheme','scope','rule'],validate='many_to_one')
    cov=coverage[(coverage.scope=='joint_CD')&(coverage.rule=='primary')].pivot(index=['target','scheme','scope','rule'],columns='arm',values='coverage').rename(columns={0:'low_coverage',1:'high_coverage'}).reset_index()
    focus=focus.merge(cov,on=['target','scheme','scope','rule'],validate='many_to_one')
    nat=natural[natural.arm.eq(1)][['model','source','target','area_share','delta_fn_mean','ratio_of_mean_fn_net']].rename(columns={
        'area_share':'complex_area_share','delta_fn_mean':'complex_fn_net_mean','ratio_of_mean_fn_net':'complex_share_of_fn_net'})
    focus=focus.merge(nat,on=['model','source','target'],validate='many_to_one')
    save(focus,'core_common_source_comparisons')


def main():
    cells,ref,whole,features=build_counts()
    weights,coverage=build_weights(ref)
    gaps,summary=compute_gaps(cells,weights)
    _,natural=natural_contributions(cells,whole,features)
    stratum_contributions(cells,weights,gaps)
    reading_tables(gaps,summary,coverage,natural)
    save(pd.DataFrame(CHECKS),'verification_checks')
    config=dict(status='derived_exploratory',shape_split=2,area_edges_coarse=COARSE[:-1]+['inf'],
        area_edges_fine=FINE[:-1]+['inf'],schemes={k:dict(area_bins=len(e)-1,distance_bands=[list(x) for x in d]) for k,(e,d) in SCHEMES.items()},
        rules=RULES,targets=TARGETS,common_sources=COMMON_SOURCES,
        weight='min of full arm pixel shares over the two within-target arms or all four C/D arms; renormalize on common eligible cells',
        no_causal_or_significance_inference=True)
    (OUT/'analysis_config.json').write_text(json.dumps(config,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    outputs=list(PROC.glob('*.csv'))+list(OUT.glob('*.csv'))+[OUT/'analysis_config.json']
    manifest=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        inputs=INPUTS,script_sha256=sha(Path(__file__)),outputs={p.relative_to(ROOT).as_posix():sha(p) for p in outputs},
        verification='Verified',scope='saved C/D soybean counts, reference support, original definition replication, standardized and natural count identities; not causal or distance generation validation')
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(f'Saved {len(cells)} cell-prediction rows; {len(CHECKS)} checks.',flush=True)


if __name__=='__main__':main()

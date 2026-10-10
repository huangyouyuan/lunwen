"""Targeted audit and delivery hashing for whole-reference patch exploration."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
import explore_sec33_reference_patch_types as b


def features():
    b.record(__file__)
    f=b.read(b.PROC/'reference_patch_features.csv');rows=[];ennrows=[]
    for target in b.SITES:
        ref=np.load(b.record(b.PROC/f'reference_full_{target}.npz'));ids=ref['ids'];lab=ref['label'];n=int(ids.max())+1
        z=f[f.target.eq(target)].sort_values('PID');pids=z.PID.to_numpy(int);area=np.bincount(ids.ravel(),minlength=n)
        cardinal=np.zeros(n,np.int64);diagonal=cardinal.copy()
        for a,c,acc in [(ids[:,:-1],ids[:,1:],cardinal),(ids[:-1],ids[1:],cardinal),
                        (ids[:-1,:-1],ids[1:,1:],diagonal),(ids[:-1,1:],ids[1:,:-1],diagonal)]:
            acc+=2*np.bincount(a[a==c],minlength=n)
        perimeter=4*area-cardinal;root=np.floor(np.sqrt(area)).astype(int)
        pmin=4*root+np.where(area==root*root,0,np.where(area<=root*(root+1),2,4))
        shape=perimeter[pids]/pmin[pids];contig=(2*cardinal[pids]+diagonal[pids])/(12*area[pids])
        b.check('SHAPE raster perimeter identity '+target,np.allclose(shape,z.SHAPE,rtol=0,atol=5.01e-5))
        b.check('CONTIG local adjacency identity '+target,np.allclose(contig,z.CONTIG,rtol=0,atol=5.01e-5))
        rows.append(dict(target=target,shape_max_abs_error=float(np.max(abs(shape-z.SHAPE))),
                         contig_max_abs_error=float(np.max(abs(contig-z.CONTIG))),rounding_tolerance=5.01e-5))
        # A fixed reference-only sample corroborates ENN's metres/center-distance convention.
        # This does not re-run FRAGSTATS or replace stored metrics.
        for crop,c in [('corn',0),('soybean',2)]:
            mask=lab==c;yy,xx=np.nonzero(mask);coords=np.column_stack([yy,xx]);pidcoords=ids[mask]
            tree=cKDTree(coords);v=z[z.crop.eq(crop)].sort_values(['AREA','PID'])
            chosen=v.iloc[np.linspace(0,len(v)-1,8,dtype=int)]
            for r in chosen.itertuples():
                ry,rx=np.nonzero(ids[r.row_min:r.row_max+1,r.col_min:r.col_max+1]==r.PID)
                query=np.column_stack([ry+r.row_min,rx+r.col_min]);nn=8;answer=np.full(len(query),np.inf)
                unresolved=np.arange(len(query))
                while len(unresolved):
                    ds,ii=tree.query(query[unresolved],k=min(nn,len(coords)),workers=2)
                    wrong=pidcoords[ii]!=r.PID;candidate=np.min(np.where(wrong,ds,np.inf),axis=1)
                    found=np.isfinite(candidate);answer[unresolved[found]]=candidate[found]
                    unresolved=unresolved[~found];nn*=2
                    # Large interiors are irrelevant to the minimum; restrict to exposed patch cells.
                    if nn>256 and len(unresolved):
                        border=np.ones_like(ids[r.row_min:r.row_max+1,r.col_min:r.col_max+1],bool)
                        from scipy.ndimage import binary_erosion
                        sub=ids[r.row_min:r.row_max+1,r.col_min:r.col_max+1]==r.PID
                        border=sub & ~binary_erosion(sub,structure=np.ones((3,3)),border_value=0)
                        unresolved=unresolved[border[ry[unresolved],rx[unresolved]]]
                value=float(answer.min()*30)
                b.check('ENN sample '+target+str(r.PID),abs(value-r.ENN)<=5.01e-5)
                ennrows.append(dict(target=target,crop=crop,PID=r.PID,pixels=r.reference_pixels,stored_ENN=r.ENN,checked_ENN=value))
        print('audited metrics',target,flush=True)
    b.write(pd.DataFrame(rows),'metric_formula_checks');b.write(pd.DataFrame(ennrows),'enn_reference_samples')
    b.finish('feature_audit')


def summary():
    b.record(__file__);b.verify_frozen()
    f=b.read(b.PROC/'frozen_patch_assignments.csv');provenance=[]
    for target in b.SITES:
        short=target.split('_')[0]
        d=pd.read_csv(b.record(b.LABEL/f'2023{short}.patch'),skipinitialspace=True);d.columns=d.columns.str.strip()
        d=d[d.LID.str.strip().eq(f'D:\\label\\2023{short}.tif')]
        z=f[f.target.eq(target)];q=d.merge(z,on='PID',suffixes=('_raw','_used'),validate='one_to_one')
        error=max(float((q[m+'_raw']-q[m+'_used']).abs().max()) for m in b.METRICS)
        b.check('professional patch table copied unchanged '+target,len(q)==len(d)==len(z) and error==0)
        provenance.append(dict(target=target,source_file=f'2023{short}.patch',rows=len(q),max_metric_abs_difference=error,status='Verified'))
    b.write(pd.DataFrame(provenance),'direct_patch_table_provenance')
    background=b.read(b.SUM/'background_class.csv')
    for row in background.itertuples():
        z=f[f.target.eq(row.dataset_id)&f.crop.eq(row.class_name)]
        b.check('whole-label class background '+row.dataset_id+row.class_name,
            len(z)==row.patch_count_8n and z.reference_pixels.sum()==row.class_pixels and abs(z.AREA.mean()-row.area_mn_reported)<=5.01e-5)
    new=b.read(b.PROC/'whole_crop_f1.csv');wc=b.read(b.ROOT/'results/summary/f1_raw_scale/within_site_crop_f1.csv').set_index(['model','target'])
    cc=b.read(b.ROOT/'results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv').set_index(['model','source','target'])
    dc=b.read(b.ROOT/'results/summary/f1_raw_scale/crop_f1_difference_36paths.csv').set_index(['model','source','target'])
    comparisons=[]
    for (m,s,t,c),z in new[new.kind.eq('cross')].groupby(['model','source','target','crop']):
        a=z.sort_values('fold').f1.to_numpy();w=new[new.kind.eq('within')&new.model.eq(m)&new.target.eq(t)&new.crop.eq(c)].f1.item()
        vals=[w,a.mean(),a.std(ddof=1),w-a.mean()]
        old=[wc.loc[(m,t),c+'_f1'],cc.loc[(m,s,t),c+'_f1_mean'],cc.loc[(m,s,t),c+'_f1_std'],dc.loc[(m,s,t),c+'_f1_difference']]
        err=float(np.max(abs(np.array(vals)-old)));b.check('formal whole F1 '+m+s+t+c,err<=1e-12 and set(z.fold)=={1,2,3,4,5})
        comparisons.append(dict(model=m,source=s,target=t,crop=c,within_f1=w,cross_f1_mean=vals[1],cross_f1_std=vals[2],delta_f1=vals[3],max_abs_difference=err))
    b.write(pd.DataFrame(comparisons),'whole_f1_formal_comparison')
    # Verify count-file identity coverage and source/output hashes without repeating prediction reads.
    ix=b.read(b.PROC/'prediction_count_index.csv');b.check('unique 192 identities',len(ix)==192 and not ix.duplicated(b.RUN).any())
    reference_support={}
    for r in ix.itertuples():
        b.check('count file hash '+r.file,b.sha(b.PROC/r.file)==r.sha256)
        ar=np.load(b.record(b.PROC/r.file));pc=ar['patch_band_prediction_counts'];tc=ar['type_band_bit_cm']
        z=f[f.target.eq(r.target)]
        for (typ,crop),v in z.groupby(['spatial_type','crop']):
            c=b.CLASSES.index(crop);expected=pc[v.PID.to_numpy(int)].sum(0)
            b.check('patch-to-type band closure '+r.file+str(typ)+crop,np.array_equal(expected,tc[typ,c].sum(1)))
        support=tc.sum(-1)
        if r.target not in reference_support:reference_support[r.target]=support
        b.check('model-source-fold reference mask '+r.file,np.array_equal(support,reference_support[r.target]))
    stats={};d=b.read(b.SUM/'type_error_summary.csv');allr=d[d.region.eq('all')]
    contrasted=b.read(b.SUM/'type_contrasts_summary.csv');loc=b.read(b.SUM/'location_contrasts_summary.csv')
    for typ in [1,2]:
        v=allr[allr.spatial_type.eq(typ)];l=loc[loc.spatial_type.eq(typ)]
        stats['T'+str(typ)]=dict(cases=len(v),negative_mean_leakage_delta=int((v.delta_leakage_mean<0).sum()),
            other_crop_delta_larger=int((v.delta_other_crop_rate_mean>v.delta_other_rate_mean).sum()),
            boundary_delta_larger=int((l.interior_minus_boundary_delta_leakage_mean<0).sum()),
            interior_delta_larger=int((l.interior_minus_boundary_delta_leakage_mean>0).sum()),
            location_five_directions=l.interior_minus_boundary_delta_leakage_direction.value_counts().to_dict())
    stats['T2_minus_T1_delta']=dict(negative_mean=int((contrasted.T2_minus_T1_delta_leakage_mean<0).sum()),
        positive_mean=int((contrasted.T2_minus_T1_delta_leakage_mean>0).sum()),
        directions=contrasted.T2_minus_T1_delta_leakage_direction.value_counts().to_dict())
    pivot=allr.pivot(index=['model','source','target','crop'],columns='spatial_type',values='leakage_mean')
    stats['cross_T1_absolute_leakage_higher']=int((pivot[1]>pivot[2]).sum())
    full=b.read(b.PROC/'type_error_counts.csv');within=full[full.kind.eq('within')&full.region.eq('all')]
    pivot=within.pivot(index=['model','target','crop'],columns='spatial_type',values='leakage')
    stats['within_T1_absolute_leakage_higher']=int((pivot[1]>pivot[2]).sum())
    direction=b.read(b.SUM/'boundary_type_error_summary.csv')
    pure=direction[((direction.bitmask==1)&direction.crop.eq('corn'))|((direction.bitmask==2)&direction.crop.isin(['corn','soybean']))|((direction.bitmask==4)&direction.crop.eq('soybean'))].copy()
    pure['opposite_rate_mean']=np.where(pure.bitmask.eq(2),pure.other_crop_rate_mean,pure.other_rate_mean)
    pure['third_rate_mean']=np.where(pure.bitmask.eq(2),pure.other_rate_mean,pure.other_crop_rate_mean)
    pure['opposite_dominates']=pure.opposite_rate_mean>pure.third_rate_mean
    b.write(pure,'pure_boundary_opposite_vs_third')
    b.write(pure[~pure.opposite_dominates],'pure_boundary_direction_exceptions')
    stats['pure_boundary']={str(t):dict(cases=len(v),opposite_dominates=int(v.opposite_dominates.sum())) for t,v in pure.groupby('spatial_type')}
    b.write(contrasted[contrasted.T2_minus_T1_delta_leakage_mean.lt(0)],'type_delta_ordering_exceptions')
    contrast=allr.pivot(index=['model','source','target','crop'],columns='spatial_type',values='net_contribution_to_class_leakage_mean')
    stats['T2_net_contribution_absolute_larger']=int((abs(contrast[2])>abs(contrast[1])).sum())
    na=[]
    for file in [b.SUM/'type_error_summary.csv',b.SUM/'boundary_type_error_summary.csv',b.SUM/'whole_patch_miss_summary.csv']:
        z=b.read(file)
        for c in [c for c in z if c.endswith('_mean') and (c.startswith('delta_') or c=='leakage_mean')]:
            na.append(dict(table=file.name,metric=c,rows=len(z),na=int(z[c].isna().sum()),negative=int(z[c].lt(0).sum()),zero=int(z[c].eq(0).sum())))
    b.write(pd.DataFrame(na),'na_negative_inventory')
    (b.SUM/'scientific_counts.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    # Review subsets supplement, never replace, full-path tables.
    b.write(d[(d.target.eq('il_2023')&d.crop.eq('soybean'))|((d.source.eq('iw2_2023')&d.target.eq('il_2023'))|(d.source.eq('il_2023')&d.target.eq('iw2_2023')))],'d_soy_and_bidirectional_review')
    b.finish('summary_audit');print(json.dumps(stats,ensure_ascii=False,indent=2))


def delivery():
    b.verify_frozen()
    parts=[]
    for folder in [b.PROC,b.SUM,b.FIG,b.ROOT/'results/raw/sec33_reference_patch_types']:
        parts.extend(x for x in folder.rglob('*') if x.is_file() and x.name!='delivery_manifest.json')
    parts.extend([b.ROOT/'.gitattributes',Path(__file__),Path(b.__file__),b.ROOT/'scripts/plot_sec33_reference_patch_types.py',
                  b.ROOT/'scripts/test/test_sec33_reference_patch_types.py',
                  b.ROOT/'scripts/export_sec33_reference_patch_raw_tables.py',
                  b.ROOT/'plan/tasks/2026-10-06-sec33-reference-patch-types.md',
                  b.ROOT/'verification/sec33-reference-patch-types-2026-10-07.md'])
    out=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),data_status='derived / exploratory',
             artifacts=[dict(path=str(p.relative_to(b.ROOT)).replace('\\','/'),sha256=b.sha(p),bytes=p.stat().st_size) for p in parts])
    (b.SUM/'delivery_manifest.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('sealed',len(parts),'artifacts')


def report_tables():
    b.record(__file__)
    d=b.read(b.SUM/'type_error_summary.csv');d=d[d.region.eq('all')]
    keys=['model','source','target','spatial_type']
    a=d[d.crop.eq('corn')].set_index(keys);s=d[d.crop.eq('soybean')].set_index(keys)
    out=[]
    for k,row in a.iterrows():
        r=s.loc[k];out.append(dict(zip(keys,k),within_corn_leakage=row.within_leakage,within_soybean_leakage=r.within_leakage,
            cross_corn_leakage_mean=row.leakage_mean,cross_soybean_leakage_mean=r.leakage_mean,
            within_soybean_minus_corn=r.within_leakage-row.within_leakage,
            cross_soybean_minus_corn=r.leakage_mean-row.leakage_mean,
            increment_soybean_minus_corn=r.delta_leakage_mean-row.delta_leakage_mean))
    b.write(pd.DataFrame(out),'crop_leakage_comparison')
    # Independently match every heatmap cell to its supporting result identity.
    plotted=b.read(b.SUM/'figure2_plot_data.csv');summary=b.read(b.SUM/'type_error_summary.csv')
    lookup=summary.set_index(['model','source','target','crop','spatial_type','region'])
    for row in plotted.itertuples():
        expected=lookup.loc[(row.model,row.source,row.target,row.crop,row.spatial_type,row.region),'delta_'+row.metric+'_mean']
        b.check('figure2 cell '+str(row.Index),np.isclose(row.value,expected,rtol=0,atol=1e-12,equal_nan=True))
    ref=b.read(b.PROC/'frozen_patch_assignments.csv');stats=[]
    for (crop,typ),v in ref[ref.crop.ne('other')].groupby(['crop','spatial_type']):
        for m in ['AREA','SHAPE','ENN']:
            q=v[m].quantile([.05,.25,.5,.75,.95]).tolist();stats.append(dict(crop=crop,spatial_type=typ,metric=m,n=len(v),q05=q[0],q25=q[1],median=q[2],q75=q[3],q95=q[4]))
    b.write(pd.DataFrame(stats),'figure1_distribution_data')
    b.finish('report_tables')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('stage',choices=['features','summary','report_tables','delivery']);globals()[p.parse_args().stage]()

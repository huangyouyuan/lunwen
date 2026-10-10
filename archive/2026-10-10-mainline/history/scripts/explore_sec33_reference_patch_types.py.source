"""Whole-reference connected-patch exploration. Never trains or runs inference.

Run prepare, cluster, freeze, count, analyze, then plot script. The freeze gate
precedes prediction reads. Integer patch IDs are checked spatially, not assumed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from scipy import ndimage
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from threadpoolctl import threadpool_limits

ROOT = Path(__file__).resolve().parents[1]
NAME = 'sec33_reference_patch_types'
PROC = ROOT/'results/processed'/NAME
SUM = ROOT/'results/summary'/NAME
FIG = ROOT/'figures/exploratory'/NAME
LABEL = ROOT/'legacy/experiment-results/label'
OLD = ROOT/'results/processed/sec33_crop_spatial_context'
SITES = {'iw_2023':'A','iw2_2023':'B','ida_2023':'C','il_2023':'D'}
CLASSES = ['corn','other','soybean']
MODELS = ['convgru','unet3d','utae']
BANDS = ['0<d<=1','1<d<=2','2<d<=3','3<d<=4','4<d<=5','5<d<=6','d>6']
METRICS = ['AREA','GYRATE','SHAPE','CONTIG','ENN']
RUN = ['kind','model','source','target','fold']
INPUTS, CHECKS = {}, []


def require(ok, message):
    if not bool(ok):
        raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()


def record(path):
    p=Path(path).resolve()
    if str(p) not in INPUTS:
        INPUTS[str(p)]=dict(path=p.as_posix(),sha256=sha(p),bytes=p.stat().st_size)
    return p


def read(path):
    return pd.read_csv(record(path),float_precision='round_trip')


def write(df,name,processed=False):
    d=PROC if processed else SUM;d.mkdir(parents=True,exist_ok=True)
    df.to_csv(d/(name+'.csv'),index=False,float_format='%.17g',encoding='utf-8')


def check(name,ok,detail=''):
    CHECKS.append(dict(check=name,status='Verified' if ok else 'Not verified',detail=str(detail)))
    require(ok,name+': '+str(detail))


def finish(stage):
    record(__file__)
    write(pd.DataFrame(CHECKS,columns=['check','status','detail']),stage+'_checks')
    data=dict(stage=stage,created_at_utc=datetime.now(timezone.utc).isoformat(),
              status='Verified',data_status='derived / exploratory',
              inputs=list(INPUTS.values()),distance_regenerated=False,fragstats_rerun=False)
    (SUM/(stage+'_manifest.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def full(a):
    """Reconstruct the existing storage layout; never defines landscape units."""
    require(a.shape==(400,128,128),'known reference storage shape')
    return a.reshape(20,20,128,128).transpose(0,2,1,3).reshape(2560,2560)


def component_mapping(labels,ids):
    """Validate 8-connected components and a bijection with supplied IDs."""
    mapping=[]
    for c in np.unique(labels):
        cc,n=ndimage.label(labels==c,np.ones((3,3),int))
        pairs=np.unique(np.column_stack((cc[cc>0],ids[cc>0])),axis=0)
        require(len(pairs)==n and len(np.unique(pairs[:,1]))==n,'ID/component bijection')
        mapping.extend((int(pid),int(c),int(cid)) for cid,pid in pairs)
    require(len({x[0] for x in mapping})==len(mapping),'IDs cross classes')
    return mapping


def prepare():
    require(not (PROC/'reference_patch_features.csv').exists(),'features already prepared')
    PROC.mkdir(parents=True,exist_ok=True);SUM.mkdir(parents=True,exist_ok=True)
    raw=[];inventory=[]
    for f in sorted(LABEL.glob('*.patch')):
        d=pd.read_csv(record(f),skipinitialspace=True);d.columns=d.columns.str.strip()
        d['LID']=d.LID.str.strip();d['TYPE']=d.TYPE.str.strip();d['input_file']=f.name
        raw.append(d)
        for lid,z in d.groupby('LID'): inventory.append(dict(file=f.name,LID=lid,rows=len(z)))
    raw=pd.concat(raw,ignore_index=True)
    # Duplicate D records in the A-named file are identical; retain their inventory.
    columns=['LID','PID','TYPE']+METRICS
    dup=raw.duplicated(['LID','PID'],keep=False)
    duplicates=raw[dup].copy();write(duplicates,'input_duplicate_records',True)
    check('duplicate records agree',not raw[columns].drop_duplicates().duplicated(['LID','PID']).any())
    raw=raw.drop_duplicates(columns)
    write(pd.DataFrame(inventory),'raw_file_identity_inventory')
    all_features=[];mapping_rows=[];grid=[]
    for target,letter in SITES.items():
        short=target.split('_')[0];f=LABEL/f'2023{short}.tif';ip=LABEL/f'2023{short}_id8.tif'
        with tifffile.TiffFile(record(f)) as t:
            label=t.asarray();geo=t.geotiff_metadata;nodata=t.pages[0].tags.get(42113)
        with tifffile.TiffFile(record(ip)) as t:
            ids=t.asarray();igeo=t.geotiff_metadata
        check('reference grid '+target,label.shape==(2560,2560) and ids.shape==label.shape and
              set(np.unique(label))=={1,2,3} and geo['ModelPixelScale'][:2]==[30.,30.])
        check('ID geotransform '+target,all(geo[k]==igeo[k] for k in ['ModelPixelScale','ModelTiepoint']))
        check('no missing labels '+target,nodata is None and ids.min()>0)
        mapping=component_mapping(label,ids)
        check('8-connected bijection '+target,True,len(mapping))
        d=raw[raw.LID.eq(f'D:\\label\\2023{short}.tif')].copy().sort_values('PID')
        counts=np.bincount(ids.ravel());pids=d.PID.to_numpy(int)
        check('table ID coverage '+target,np.array_equal(pids,np.arange(1,len(counts))))
        cla=np.zeros(len(counts),int)
        for pid,c,cid in mapping:
            cla[pid]=c;mapping_rows.append(dict(target=target,PID=pid,reference_class=c,recovered_component_id=cid))
        check('table class and area '+target,np.array_equal(d.TYPE.str[-1].astype(int),cla[pids]) and
              np.allclose(d.AREA,counts[pids]*.09,rtol=0,atol=1e-8))
        old=np.load(record(OLD/f'reference_{target}.npz'),allow_pickle=False)
        band=full(old['bands']);bits=full(old['pair_bits']);oldlab=full(old['labels'])
        check('new full label equals established reference '+target,np.array_equal(label,oldlab+1))
        check('band/type valid '+target,set(np.unique(band))==set(range(7)) and set(np.unique(bits))<=set(range(8)))
        folds=full(np.broadcast_to(old['fold_id'][:,None,None],(400,128,128)))
        fold_pairs=np.unique(ids.astype('int64')*8+folds)
        fold_count=np.bincount(fold_pairs//8,minlength=len(counts))
        edgeids=np.unique(np.concatenate((ids[0],ids[-1],ids[:,0],ids[:,-1])))
        nb=np.bincount(ids[band==0],minlength=len(counts));far=np.bincount(ids[band==6],minlength=len(counts))
        rr,cc=np.indices(ids.shape)
        rmin=np.full(len(counts),2560);rmax=np.zeros(len(counts),int)
        cmin=rmin.copy();cmax=rmax.copy()
        np.minimum.at(rmin,ids.ravel(),rr.ravel());np.maximum.at(rmax,ids.ravel(),rr.ravel())
        np.minimum.at(cmin,ids.ravel(),cc.ravel());np.maximum.at(cmax,ids.ravel(),cc.ravel())
        d['target']=target;d['site']=letter;d['crop']=[CLASSES[c-1] for c in cla[pids]]
        d['patch_uid']=[f'{target}__ref{p:06d}' for p in pids];d['reference_pixels']=counts[pids]
        d['touches_outer_edge']=np.isin(pids,edgeids);d['oof_fold_count']=fold_count[pids]
        d['boundary_pixels']=nb[pids];d['interior_pixels']=counts[pids]-nb[pids];d['far_interior_pixels']=far[pids]
        d['boundary_share']=nb[pids]/counts[pids];d['no_interior']=d.interior_pixels.eq(0)
        d['row_min']=rmin[pids];d['row_max']=rmax[pids];d['col_min']=cmin[pids];d['col_max']=cmax[pids]
        d['feature_status']='valid';d['missing_reason']=''
        for m in METRICS:
            invalid=~np.isfinite(d[m]) | (d[m]<0)
            d.loc[invalid,'feature_status']='invalid';d.loc[invalid,'missing_reason']+=m+';'
        all_features.append(d)
        np.savez_compressed(PROC/f'reference_full_{target}.npz',label=label-1,ids=ids,bands=band,bits=bits,oof_fold=folds)
        grid.append(dict(target=target,rows=2560,cols=2560,resolution_m=30,epsg=5070,
                         id_epsg_tag_present='ProjectedCSTypeGeoKey' in igeo,
                         nodata='none',connectivity=8,patches=len(pids),crop_patches=int(d.crop.ne('other').sum())))
        print('prepared',target,len(pids),flush=True)
    f=pd.concat(all_features,ignore_index=True);write(f,'reference_patch_features',True)
    write(pd.DataFrame(mapping_rows),'id_component_correspondence',True);write(pd.DataFrame(grid),'grid_inventory')
    crops=f[f.crop.ne('other')]
    rows=[];corr=[]
    for key,z in [('all',crops)]+[(f'{t}/{c}',z) for (t,c),z in crops.groupby(['target','crop'])]:
        for m in METRICS:
            rows.append(dict(domain=key,metric=m,n=len(z),n_na=int(z[m].isna().sum()),minimum=z[m].min(),
                q25=z[m].quantile(.25),median=z[m].median(),q75=z[m].quantile(.75),q95=z[m].quantile(.95),maximum=z[m].max()))
        co=z[METRICS].corr(method='spearman')
        for i,m in enumerate(METRICS):
            for n in METRICS[i+1:]:corr.append(dict(domain=key,first=m,second=n,spearman=co.loc[m,n]))
    write(pd.DataFrame(rows),'feature_distributions');write(pd.DataFrame(corr),'feature_correlations')
    # Whole-site background only: copied from actual whole-label level outputs.
    for file in LABEL.joinpath('fragstats_results').glob('*.csv'):
        if file.name.startswith('完整标签'):
            write(read(file),'background_'+{'完整标签类别级指标':'class','完整标签景观级指标':'landscape','完整标签邻接矩阵':'adjacency'}[file.stem])
    finish('prepare')


def feature_matrix(f):
    return np.log(f[['AREA','SHAPE','ENN']].to_numpy(float))


def cluster():
    require(not (PROC/'cluster_candidates.csv').exists(),'clustering already recorded')
    f=read(PROC/'reference_patch_features.csv');f=f[f.crop.ne('other')].copy().reset_index(drop=True)
    require(f.feature_status.eq('valid').all(),'invalid features need explicit isolated assignment')
    x=feature_matrix(f);strata=f.target+'/'+f.crop
    weight=1/strata.map(strata.value_counts()).to_numpy(float);weight/=weight.mean()
    mean=np.average(x,axis=0,weights=weight);sd=np.sqrt(np.average((x-mean)**2,axis=0,weights=weight));z=(x-mean)/sd
    rng=np.random.default_rng(61006)
    sample=np.concatenate([rng.choice(ix,min(300,len(ix)),replace=False) for ix in f.groupby(['target','crop']).indices.values()])
    diag=[];runs=[];out=f[['target','site','crop','PID','patch_uid']].copy();centers={}
    with threadpool_limits(limits=2):
        for k in [2,3,4]:
            km=KMeans(k,n_init=20,random_state=61006).fit(z,sample_weight=weight);pred=km.labels_
            # Stable type numbers by mean log area of centers; not an error ranking.
            order=np.argsort(km.cluster_centers_[:,0]);lookup=np.argsort(order)
            out[f'k{k}']=lookup[pred]+1;centers[str(k)]=km.cluster_centers_[order].tolist()
            init=[];boot=[]
            for rep in range(5):
                alt=KMeans(k,n_init=10,random_state=710+rep).fit(z,sample_weight=weight)
                ari=adjusted_rand_score(pred,alt.labels_);init.append(ari);runs.append(dict(k=k,kind='initialization',rep=rep,ari=ari))
            for rep in range(6):
                ix=np.concatenate([rng.choice(ix,int(len(ix)*.7),replace=False) for ix in f.groupby(['target','crop']).indices.values()])
                alt=KMeans(k,n_init=10,random_state=810+rep).fit(z[ix],sample_weight=weight[ix])
                ari=adjusted_rand_score(pred,alt.predict(z));boot.append(ari);runs.append(dict(k=k,kind='stratified_70pct_subsample',rep=rep,ari=ari))
            ordinary=KMeans(k,n_init=20,random_state=61006).fit(z)
            eqari=adjusted_rand_score(pred,ordinary.labels_)
            support=pd.crosstab(strata,pred)
            sil=silhouette_score(z[sample],pred[sample])
            diag.append(dict(k=k,silhouette_balanced_sample=sil,initialization_ari_min=min(init),subsample_ari_min=min(boot),
                subsample_ari_median=np.median(boot),ordinary_patch_weight_ari=eqari,min_site_crop_cluster_n=int(support.to_numpy().min()),
                eligible=bool(sil>=.25 and min(init)>=.9 and min(boot)>=.75 and np.median(boot)>=.85 and support.to_numpy().min()>=30)))
            print('cluster',diag[-1],flush=True)
    write(out,'cluster_candidates',True);write(pd.DataFrame(diag),'cluster_diagnostics');write(pd.DataFrame(runs),'cluster_stability_runs')
    profiles=[]
    for k in [2,3,4]:
        g=f.assign(cluster=out[f'k{k}'])
        for (t,c,cl),v in g.groupby(['target','crop','cluster']):
            profiles.append(dict(k=k,target=t,crop=c,cluster=cl,n=len(v),pixels=int(v.reference_pixels.sum()),
                tiny_fraction=float(v.reference_pixels.eq(1).mean()),edge_fraction=float(v.touches_outer_edge.mean()),
                **{m+'_median':v[m].median() for m in METRICS}))
    write(pd.DataFrame(profiles),'cluster_profiles')
    params=dict(features=['AREA','SHAPE','ENN'],transforms=['natural_log']*3,
                interpretation='area, perimeter complexity, same-class nearest-neighbor distance',
                standardization='reference patch weights equal for each of eight site-crop strata',
                center=mean.tolist(),scale=sd.tolist(),random_state=61006,centers=centers,
                clustering_weight='1 / crop patch count in target-crop stratum, normalized mean=1',
                excluded_features={'GYRATE':'rank-redundant size and spatial extent; not pure elongation',
                                   'CONTIG':'rank-redundant with AREA in this input',
                                   'FRAC':'not supplied','PROX':'not supplied; no radius assumed'},
                data_status='reference features only; predictions not read')
    (PROC/'cluster_parameters.json').write_text(json.dumps(params,indent=2)+'\n',encoding='utf-8')
    finish('cluster')


def freeze():
    require(not (PROC/'frozen_configuration.json').exists(),'already frozen')
    f=read(PROC/'reference_patch_features.csv');a=read(PROC/'cluster_candidates.csv');d=read(SUM/'cluster_diagnostics.csv')
    eligible=d[d.eligible]
    require(len(eligible)>0,'no eligible clusters; transparent fallback needs feature-only review')
    best=eligible.silhouette_balanced_sample.max()
    k=int(eligible[eligible.silhouette_balanced_sample>=best-.02].k.min())
    a=a[['target','PID',f'k{k}']].rename(columns={f'k{k}':'spatial_type'})
    f=f.merge(a,on=['target','PID'],how='left',validate='one_to_one')
    f['spatial_type']=f.spatial_type.fillna(0).astype(int)
    write(f,'frozen_patch_assignments',True)
    reps=[]
    p=json.loads(record(PROC/'cluster_parameters.json').read_text())
    for (c,t),v in f[f.spatial_type.gt(0)].groupby(['crop','spatial_type']):
        candidates=v[~v.touches_outer_edge].copy()
        z=(feature_matrix(candidates)-p['center'])/p['scale'];cent=np.asarray(p['centers'][str(k)])[t-1]
        at=int(np.argmin(((z-cent)**2).sum(1)))
        reps.append(candidates.iloc[at].to_dict())
    write(pd.DataFrame(reps),'representative_patches')
    config=dict(created_at_utc=datetime.now(timezone.utc).isoformat(),selected_k=k,
        selection='eligible silhouette maximum; smallest K within 0.02; no prediction errors used',
        frozen_files={str(x.relative_to(ROOT)):sha(x) for x in [PROC/'reference_patch_features.csv',PROC/'cluster_candidates.csv',PROC/'cluster_parameters.json',PROC/'frozen_patch_assignments.csv',SUM/'cluster_diagnostics.csv']},
        names_pending_reference_visual_review=True,prediction_read_gate=True)
    (PROC/'frozen_configuration.json').write_text(json.dumps(config,indent=2)+'\n',encoding='utf-8')
    check('frozen assignments cover all classes',len(f)==len(read(PROC/'reference_patch_features.csv')))
    finish('freeze');print('FROZEN K',k,flush=True)


def count_patch_prediction(ids,bands,prediction):
    require(ids.shape==bands.shape==prediction.shape,'aligned full-grid arrays')
    require(set(np.unique(prediction))<={0,1,2},'prediction class encoding')
    n=int(ids.max())+1
    return np.bincount((ids.astype('int64')*21+bands*3+prediction).ravel(),minlength=n*21).reshape(n,7,3)


def rates(counts,c):
    n=int(np.sum(counts));correct=int(counts[c]);other_crop=2 if c==0 else 0
    return dict(pixels=n,correct=correct,errors=n-correct,other_crop_errors=int(counts[other_crop]),other_errors=int(counts[1]),
                recall=correct/n if n else np.nan,leakage=(n-correct)/n if n else np.nan,
                other_crop_rate=counts[other_crop]/n if n else np.nan,other_rate=counts[1]/n if n else np.nan,
                valid_status='defined' if n else 'zero_reference_support')


def verify_frozen():
    config=json.loads(record(PROC/'frozen_configuration.json').read_text())
    for path,expected in config['frozen_files'].items():
        check('frozen input '+path,sha(ROOT/path)==expected)
    return config


def count():
    config=verify_frozen();ktypes=config['selected_k']
    require(not (PROC/'prediction_count_index.csv').exists(),'saved counts already exist')
    import explore_sec33_crop_spatial_context as old
    f=read(PROC/'frozen_patch_assignments.csv');whole=read(OLD/'whole_cm.csv').set_index(RUN)
    oldband=read(OLD/'distance_class_per_prediction.csv').set_index(RUN+['band','crop'])
    cmcols=[f'cm_{i}_{j}' for i in range(3) for j in range(3)]
    allruns=list(old.runs());index=[];rows=[];brows=[];loss=[];f1rows=[]
    regions={'all':list(range(7)),'boundary':[0],'interior':list(range(1,7)),'far_interior':[6],
             **{bn:[i] for i,bn in enumerate(BANDS)}}
    for target in SITES:
        ref=np.load(record(PROC/f'reference_full_{target}.npz'));lab=ref['label'];ids=ref['ids'];band=ref['bands'];bits=ref['bits'];foldmap=ref['oof_fold']
        z=f[f.target.eq(target)].sort_values('PID');pids=z.PID.to_numpy(int);nt=int(ids.max())+1
        type_lut=np.zeros(nt,int);type_lut[pids]=z.spatial_type
        pix_type=type_lut[ids]
        basecode=((((pix_type*3+lab)*7+band)*8+bits)*3).astype('int32')
        expected_support=np.bincount((ids.astype('int64')*7+band).ravel(),minlength=nt*7).reshape(nt,7)
        for kind,model,source,t,folder in allruns:
            if t!=target:continue
            maps=folder/'maps'
            with tifffile.TiffFile(record(maps/'reference.tif')) as tf:
                rlab=tf.asarray();rgeo=tf.geotiff_metadata
                rtransform={key:tuple(tf.pages[0].tags[key].value) for key in [33550,33922]}
            check('prediction reference '+str(folder),np.array_equal(rlab,lab+1))
            frozenband=np.load(record(folder/'details/reference_assets/distance_band_index.npy'))
            check('saved distances '+str(folder),np.array_equal(frozenband,band))
            folds=[0] if kind=='within' else [1,2,3,4,5]
            for fold in folds:
                tag='oof' if kind=='within' else f'fold_{fold}'
                pp=maps/(tag+'_prediction.tif')
                with tifffile.TiffFile(record(pp)) as tf:
                    pred=tf.asarray().astype('int16')-1;pgeo=tf.geotiff_metadata
                    ptransform={key:tuple(tf.pages[0].tags[key].value) for key in [33550,33922]}
                check('prediction geotransform '+str(pp),pred.shape==lab.shape and
                      ptransform==rtransform)
                if pgeo is None:
                    check('missing CRS but explicit scale/tiepoint '+str(pp),True,'Partially verified GeoKey provenance; scale/tiepoint, label and saved pixels verified separately')
                # Trace fold identity and confirm full TIFF pixels against original saved arrays.
                observed=set()
                for oldfold in (range(1,6) if kind=='within' else [fold]):
                    dp=folder/'details'/f'fold_{oldfold}'
                    meta=json.loads(record(dp/'test_patch_run.json').read_text(encoding='utf-8-sig'))
                    check('run identity '+str(dp),meta['model_name']==model and meta['train_dataset_id']==source and meta['eval_dataset_id']==target and meta['experiment_fold']==oldfold)
                    saved=np.load(record(dp/'test_patch_predictions.npz'),allow_pickle=False)
                    tiles=saved['patch_id'].astype(int)
                    require(len(set(tiles))==len(tiles) and not observed.intersection(tiles),'duplicate OOF tiles')
                    for ix,pid in enumerate(tiles):
                        rr,cc=divmod(int(pid),20);ys=slice(rr*128,(rr+1)*128);xs=slice(cc*128,(cc+1)*128)
                        require(str(saved['patch_uid'][ix])==f'{target}__p{pid:04d}','saved prediction UID')
                        require(np.array_equal(pred[ys,xs],saved['predictions'][ix]),'whole-map versus saved prediction pixels')
                        if kind=='within':require(np.all(foldmap[ys,xs]==meta['test_fold']),'OOF test fold identity')
                    observed.update(tiles)
                check('full coverage and original pixels '+str(pp),observed==set(range(400)))
                cm=np.bincount((lab*3+pred).ravel(),minlength=9).reshape(3,3)
                expected=whole.loc[(kind,model,source,target,fold),cmcols].to_numpy(int).reshape(3,3)
                check('whole CM '+str(pp),np.array_equal(cm,expected))
                pc=count_patch_prediction(ids,band,pred)
                check('patch reference support '+str(pp),np.array_equal(pc.sum(2),expected_support))
                tc=np.bincount((basecode+pred).ravel(),minlength=(ktypes+1)*3*7*8*3).reshape(ktypes+1,3,7,8,3)
                check('types restore whole CM '+str(pp),np.array_equal(tc.sum((0,2,3)),cm))
                key=dict(kind=kind,model=model,source=source,target=target,fold=fold)
                path=PROC/f'counts_{kind}_{model}_{source}_{target}_{fold}.npz'
                if path.exists():
                    cached=np.load(record(path))
                    check('preserved prior partial count '+str(path),np.array_equal(cached['patch_band_prediction_counts'],pc) and np.array_equal(cached['type_band_bit_cm'],tc) and np.array_equal(cached['PID'],np.arange(nt)))
                else:
                    np.savez_compressed(path,patch_band_prediction_counts=pc.astype('int32'),type_band_bit_cm=tc.astype('int32'),PID=np.arange(nt))
                index.append(dict(**key,file=path.name,sha256=sha(path),prediction_file=str(pp)))
                for c,crop in [(0,'corn'),(2,'soybean')]:
                    nclass=int(cm[c].sum());tp=int(cm[c,c]);den=int(nclass+cm[:,c].sum())
                    f1rows.append(dict(**key,crop=crop,f1=2*tp/den if den else np.nan,reference_pixels=nclass))
                    classz=z[z.crop.eq(crop)]
                    for bi,bn in enumerate(BANDS):
                        oldrow=oldband.loc[(kind,model,source,target,fold,bn,crop)]
                        bandcounts=tc[:,c,bi].sum((0,1))
                        check('band crop counts '+str(pp)+bn+crop,int(bandcounts.sum())==oldrow.pixels and int(bandcounts[c])==oldrow.tp)
                    for typ in range(1,ktypes+1):
                        g=classz[classz.spatial_type.eq(typ)];gp=g.PID.to_numpy(int)
                        pt=pc[gp].sum(1);no_correct=pt[:,c]==0
                        loss.append(dict(**key,crop=crop,spatial_type=typ,n_patches=len(g),pixels=int(pt.sum()),
                            no_correct_patches=int(no_correct.sum()),no_correct_patch_fraction=float(no_correct.mean()),
                            no_correct_pixels=int(pt[no_correct].sum()),no_correct_area_fraction=float(pt[no_correct].sum()/pt.sum()),
                            no_interior_patches=int(g.no_interior.sum()),no_interior_patch_fraction=float(g.no_interior.mean())))
                        for region,bb in regions.items():
                            vc=pc[gp][:,bb,:];counts=vc.sum((0,1));r=rates(counts,c)
                            rows.append(dict(**key,crop=crop,spatial_type=typ,region=region,**r,
                                n_patches_with_support=int((vc.sum((1,2))>0).sum()),type_pixels=int(g.reference_pixels.sum()),
                                class_pixels=nclass,pixel_share_of_type=r['pixels']/g.reference_pixels.sum(),pixel_share_of_class=r['pixels']/nclass))
                        for edge in [False,True]:
                            sub=g[g.touches_outer_edge.eq(edge)].PID.to_numpy(int);counts=pc[sub].sum((0,1));r=rates(counts,c)
                            rows.append(dict(**key,crop=crop,spatial_type=typ,region='all_edge' if edge else 'all_nonedge',**r,
                                n_patches_with_support=len(sub),type_pixels=int(g.reference_pixels.sum()),class_pixels=nclass,
                                pixel_share_of_type=r['pixels']/g.reference_pixels.sum(),pixel_share_of_class=r['pixels']/nclass))
                        for bit in range(8):
                            counts=tc[typ,c,0,bit];r=rates(counts,c)
                            brows.append(dict(**key,crop=crop,spatial_type=typ,bitmask=bit,**r,
                                type_pixels=int(g.reference_pixels.sum()),class_pixels=nclass,pixel_share_of_class=r['pixels']/nclass))
                print('counted',kind,model,source,target,fold,flush=True)
    check('all runs',len(index)==192)
    write(pd.DataFrame(index),'prediction_count_index',True);write(pd.DataFrame(rows),'type_error_counts',True)
    write(pd.DataFrame(brows),'boundary_type_error_counts',True);write(pd.DataFrame(loss),'whole_patch_miss_counts',True)
    write(pd.DataFrame(f1rows),'whole_crop_f1',True);finish('count')


def join_baseline(d,condition,fields):
    keys=['model','target','crop','spatial_type']+condition
    w=d[d.kind.eq('within')][keys+fields]
    require(not w.duplicated(keys).any(),'unique within keys')
    x=d[d.kind.eq('cross')].merge(w.rename(columns={x:'within_'+x for x in fields}),on=keys,how='left',validate='many_to_one',indicator=True)
    require(x['_merge'].eq('both').all(),'all cross records match baseline')
    x=x.drop(columns='_merge')
    for col in fields:x['delta_'+col]=x[col]-x['within_'+col]
    if 'pixels' in fields:require(x.pixels.eq(x.within_pixels).all(),'shared reference support')
    return x


def strict_summary(d,keys,fields,constants):
    out=[]
    for key,v in d.groupby(keys,dropna=False,sort=False):
        require(len(v)==5 and set(v.fold)=={1,2,3,4,5},'five explicit source predictions')
        row=dict(zip(keys,key if isinstance(key,tuple) else [key]))
        for c in constants:
            require(v[c].nunique(dropna=False)==1,'constant baseline/support '+c)
            row[c]=v[c].iloc[0]
        for c in fields:
            a=v.sort_values('fold')[c].to_numpy(float);valid=np.isfinite(a);complete=valid.all()
            row.update({c+'_mean':float(a.mean()) if complete else np.nan,c+'_std':float(a.std(ddof=1)) if complete else np.nan,
                        c+'_min':float(a.min()) if complete else np.nan,c+'_max':float(a.max()) if complete else np.nan,
                        c+'_n_valid':int(valid.sum()),c+'_positive':int((a>0).sum()),c+'_negative':int((a<0).sum()),c+'_zero':int((a==0).sum()),
                        c+'_direction':'not_calculable' if not complete else 'all_positive' if (a>0).all() else 'all_negative' if (a<0).all() else 'all_zero' if (a==0).all() else 'mixed'})
        out.append(row)
    return pd.DataFrame(out)


def analyze():
    verify_frozen();f=read(PROC/'frozen_patch_assignments.csv');support=[]
    for (target,crop,typ),z in f[f.crop.ne('other')].groupby(['target','crop','spatial_type']):
        allc=f[f.target.eq(target)&f.crop.eq(crop)]
        support.append(dict(target=target,site=SITES[target],crop=crop,spatial_type=typ,n_patches=len(z),pixels=int(z.reference_pixels.sum()),
            patch_fraction=len(z)/len(allc),area_fraction=z.reference_pixels.sum()/allc.reference_pixels.sum(),
            boundary_share=z.boundary_pixels.sum()/z.reference_pixels.sum(),no_interior_fraction=z.no_interior.mean(),
            edge_patch_fraction=z.touches_outer_edge.mean(),edge_area_fraction=z.loc[z.touches_outer_edge,'reference_pixels'].sum()/z.reference_pixels.sum(),
            multifold_patch_fraction=z.oof_fold_count.gt(1).mean(),multifold_area_fraction=z.loc[z.oof_fold_count.gt(1),'reference_pixels'].sum()/z.reference_pixels.sum(),
            **{m+'_median':z[m].median() for m in METRICS}))
    write(pd.DataFrame(support),'type_reference_support')
    metrics=['recall','leakage','other_crop_rate','other_rate'];counts=['pixels','correct','errors','other_crop_errors','other_errors']
    for stem,condition in [('type_error',['region']),('boundary_type_error',['bitmask'])]:
        d=read(PROC/(stem+'_counts.csv'));x=join_baseline(d,condition,counts+metrics)
        x['net_added_errors']=x.delta_errors
        x['net_contribution_to_class_leakage']=x.delta_errors/x.class_pixels
        x['net_contribution_to_type_leakage']=x.delta_errors/x.type_pixels
        x['net_other_crop_contribution']=x.delta_other_crop_errors/x.class_pixels
        x['net_other_contribution']=x.delta_other_errors/x.class_pixels
        check(stem+' directional closure',np.allclose(x.delta_other_crop_rate+x.delta_other_rate,x.delta_leakage,rtol=0,atol=1e-12,equal_nan=True))
        extra=['net_added_errors','net_contribution_to_class_leakage','net_contribution_to_type_leakage','net_other_crop_contribution','net_other_contribution']
        write(x,stem+'_per_prediction',True)
        summ=strict_summary(x,['model','source','target','crop','spatial_type']+condition,
            metrics+['delta_'+c for c in metrics]+extra,
            ['pixels','type_pixels','class_pixels']+['within_'+m for m in metrics])
        write(summ,stem+'_summary')
        if stem=='type_error':
            # Boundary + interior net contribution closes type and whole-crop differences.
            key=['model','source','target','fold','crop','spatial_type']
            near=x[x.region.eq('boundary')].set_index(key);inside=x[x.region.eq('interior')].set_index(key);total=x[x.region.eq('all')].set_index(key)
            check('boundary interior integer net closure',np.array_equal((near.net_added_errors+inside.net_added_errors).sort_index(),total.net_added_errors.sort_index()))
            check('boundary interior rate contribution closure',np.allclose((near.net_contribution_to_type_leakage+inside.net_contribution_to_type_leakage).sort_index(),total.delta_leakage.sort_index(),rtol=0,atol=1e-12))
            paired=inside[['delta_leakage','delta_other_crop_rate','delta_other_rate']].join(near[['delta_leakage','delta_other_crop_rate','delta_other_rate']],lsuffix='_interior',rsuffix='_boundary',validate='one_to_one').reset_index()
            for m in ['leakage','other_crop_rate','other_rate']:paired['interior_minus_boundary_delta_'+m]=paired['delta_'+m+'_interior']-paired['delta_'+m+'_boundary']
            write(paired,'location_contrasts_per_prediction',True)
            write(strict_summary(paired,['model','source','target','crop','spatial_type'],['interior_minus_boundary_delta_'+m for m in ['leakage','other_crop_rate','other_rate']],[]),'location_contrasts_summary')
            types=x[x.region.eq('all')].pivot(index=['model','source','target','fold','crop'],columns='spatial_type',values='delta_leakage')
            types['T2_minus_T1_delta_leakage']=types[2]-types[1];types=types.reset_index()
            write(types,'type_contrasts_per_prediction',True)
            write(strict_summary(types,['model','source','target','crop'],['T2_minus_T1_delta_leakage'],[]),'type_contrasts_summary')
            old=read(OLD/'whole_class_per_prediction.csv');old=old[old.kind.eq('cross')&old.crop.isin(['corn','soybean'])]
            net=x[x.region.eq('all')].groupby(['model','source','target','fold','crop']).net_contribution_to_class_leakage.sum()
            check('types recover whole leakage delta',np.allclose(net.sort_index(),old.set_index(['model','source','target','fold','crop']).delta_leakage.sort_index(),atol=1e-12,rtol=0))
    lost=read(PROC/'whole_patch_miss_counts.csv');fields=['no_correct_patch_fraction','no_correct_area_fraction','no_correct_patches','no_correct_pixels']
    x=join_baseline(lost,[],fields);write(x,'whole_patch_miss_per_prediction',True)
    write(strict_summary(x,['model','source','target','crop','spatial_type'],fields+['delta_'+s for s in fields],
                        ['n_patches','pixels','no_interior_patches','no_interior_patch_fraction']+['within_'+s for s in fields]),'whole_patch_miss_summary')
    f1=read(PROC/'whole_crop_f1.csv');old=read(OLD/'whole_class_per_prediction.csv');old=old[old.crop.isin(['corn','soybean'])]
    key=RUN+['crop'];merged=f1.merge(old[key+['f1']],on=key,suffixes=('_new','_old'),validate='one_to_one')
    check('full F1 unchanged',len(merged)==384 and np.allclose(merged.f1_new,merged.f1_old,rtol=0,atol=1e-12))
    finish('analyze')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['prepare','cluster','freeze','count','analyze'])
    args=parser.parse_args();globals()[args.stage]()

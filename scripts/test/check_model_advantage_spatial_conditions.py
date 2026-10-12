"""Independent, read-only verification of saved model-advantage analysis."""
import ast
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
PROC=ROOT/'results/processed/model_advantage_spatial_conditions'
OUT=ROOT/'results/summary/model_advantage_spatial_conditions'
REF=ROOT/'results/processed/sec33_reference_patch_types'
RUN=['kind','model','source','target','fold']
PAIR=['kind','comparison_model','source','target','fold','crop']


def read(path):
    return pd.read_csv(path,float_precision='round_trip')


class ModelAdvantageChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p=read(PROC/'group_advantage_per_prediction.csv')

    def test_manifest_and_pairing_provenance(self):
        m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
        for rel,digest in (m['inputs']|m['outputs']).items():
            self.assertEqual(hashlib.sha256((ROOT/rel).read_bytes()).hexdigest(),digest,rel)
        self.assertEqual(hashlib.sha256((ROOT/'scripts/analyze_model_advantage_spatial_conditions.py').read_bytes()).hexdigest(),m['script_sha256'])
        self.assertTrue(read(OUT/'verification_checks.csv').status.eq('Verified').all())
        d=read(OUT/'prediction_identity_audit.csv')
        self.assertEqual(len(d),240)
        self.assertFalse(d.duplicated(RUN).any())
        self.assertTrue(d[d.kind.eq('within')].groupby(['source','fold']).membership_sha256.nunique().eq(1).all())

    def test_distance_code_semantics(self):
        path=ROOT/'legacy/manuscript/HLS-Crop/src/learning/distance_band_analysis.py'
        tree=ast.parse(path.read_text(encoding='utf-8'))
        defs=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
              ['compute_boundary_distance_map','distance_band_index']]
        namespace={'np':np,'BAND_EDGES':(0,1,2,3,4,5,6,np.inf)}
        exec(compile(ast.Module(body=defs,type_ignores=[]),str(path),'exec'),namespace)
        vals=np.array([0,.5,1,1.0001,2,3,4,5,6,6.0001,np.nan,np.inf])
        self.assertEqual(namespace['distance_band_index'](vals).tolist(),[-1,0,0,1,1,2,3,4,5,6,-1,-1])
        # Synthetic arrays are only unit-test fixtures, never research results.
        label=np.array([[0,0,1,1],[0,0,1,1]],dtype=np.uint8)
        distance,exists=namespace['compute_boundary_distance_map'](label)
        self.assertTrue(exists)
        self.assertTrue(np.allclose(distance,[[1.5,.5,.5,1.5]]*2))
        distance,exists=namespace['compute_boundary_distance_map'](np.array([[0,0,255],[0,0,255]],dtype=np.uint8))
        self.assertFalse(exists);self.assertTrue(np.isnan(distance).all())

    def test_independent_saved_patch_counts(self):
        features=read(REF/'reference_patch_features.csv')
        index=read(REF/'prediction_count_index.csv').set_index(RUN)
        cases=[('within','iw_2023','iw_2023',0,'corn','utae'),
               ('within','ida_2023','ida_2023',0,'corn','unet3d'),
               ('cross','iw2_2023','il_2023',3,'soybean','utae')]
        for kind,source,target,fold,crop,model in cases:
            f=features[(features.target==target)&(features.crop==crop)].iloc[::-1]
            fn={}
            for mod in ['convgru',model]:
                row=index.loc[(kind,mod,source,target,fold)]
                with np.load(REF/row.file) as z:
                    at=pd.Index(z['PID']).get_indexer(f.PID)
                    self.assertTrue((at>=0).all())
                    count=z['patch_band_prediction_counts'][at]
                cls=0 if crop=='corn' else 2
                fn[mod]=count.sum(axis=2)-count[:,:,cls]
            p=self.p[(self.p.kind==kind)&(self.p.source==source)&(self.p.target==target)&
                     (self.p.fold==fold)&(self.p.crop==crop)&(self.p.comparison_model==model)]
            band=['0<d<=1','1<d<=2','2<d<=3','3<d<=4','4<d<=5','5<d<=6','d>6']
            for i,label in enumerate(band):
                r=p[(p.scheme=='distance')&(p.group==label)].iloc[0]
                self.assertEqual(r.fn_convgru,fn['convgru'][:,i].sum())
                self.assertEqual(r.net_fewer_pixels,fn['convgru'][:,i].sum()-fn[model][:,i].sum())
            area=[0,10,50,100,200,500,np.inf];shape=[1,1.5,2,3,np.inf]
            for a in range(6):
                for s in range(4):
                    mask=(f.AREA>=area[a])&(f.AREA<area[a+1])&(f.SHAPE>=shape[s])&(f.SHAPE<shape[s+1])
                    al=['<10','10-<50','50-<100','100-<200','200-<500','>=500'][a]
                    sl=['1-<1.5','1.5-<2','2-<3','>=3'][s]
                    r=p[(p.scheme=='area_shape')&(p.group==al+'|'+sl)].iloc[0]
                    self.assertEqual(r.reference_pixels,f.loc[mask,'reference_pixels'].sum())
                    self.assertEqual(r.net_fewer_pixels,fn['convgru'][mask].sum()-fn[model][mask].sum())

    def test_group_contributions_and_missing_support(self):
        p=self.p
        self.assertFalse(p.duplicated(PAIR+['scheme','group']).any())
        for key,g in p.groupby(PAIR+['scheme']):
            self.assertEqual(g.reference_pixels.sum(),g.whole_crop_pixels.iloc[0])
            self.assertEqual(g.net_fewer_pixels.sum(),g.whole_net_fewer_pixels.iloc[0])
            self.assertAlmostEqual(g.whole_rate_contribution.sum(),g.whole_net_fewer_pixels.iloc[0]/g.whole_crop_pixels.iloc[0],places=12)
        empty=p.reference_pixels.eq(0)
        self.assertTrue(p.loc[empty,'advantage'].isna().all())
        self.assertTrue(p.loc[empty,'net_fewer_pixels'].eq(0).all())
        tiny=(p.whole_net_fewer_pixels/p.whole_crop_pixels).abs()<.001
        self.assertTrue(p.loc[tiny,'net_reduction_share'].isna().all())
        self.assertTrue((p.net_fewer_pixels<0).any())
        self.assertTrue(np.allclose(p.advantage_change,p.error_increment_convgru-p.error_increment_other_model,
                                    equal_nan=True,atol=1e-14,rtol=0))

    def test_same_support_weights_and_direct_model_contrast(self):
        w=read(OUT/'same_support_weights.csv')
        rates=read(PROC/'conditional_model_rates_per_prediction.csv')
        counts=read(ROOT/'results/processed/spatial_error_conditions/group_metrics_per_prediction.csv')
        for key,g in w.groupby(['target','crop','contrast_name','rule','arm']):
            self.assertTrue(g.loc[~g.eligible,'weight_distance_equal'].eq(0).all())
            self.assertTrue(g.loc[~g.eligible,'weight_distance_native'].eq(0).all())
            self.assertTrue(np.allclose(g.groupby('control_bin').weight_distance_equal.sum(),
                                       g.groupby('control_bin').weight_distance_native.sum(),atol=1e-14))
            n=g.reference_pixels.where(g.eligible,0)
            denom=n.groupby(g.control_bin).transform('sum')
            expected=g.groupby('control_bin').weight_distance_equal.transform('sum')*n/denom
            self.assertTrue(np.allclose(expected.fillna(0),g.weight_distance_native,atol=1e-14))
        # Independent string-based selection, model rates -> model gap, on one matched support.
        for model in ['convgru','utae']:
            sub=counts[(counts.kind=='within')&(counts.target=='il_2023')&(counts.crop=='soybean')&
                       (counts.model==model)&(counts.scheme=='area_shape_distance')].copy()
            parts=sub.group.str.split('|',expand=True)
            sub['arm']=parts[1].isin(['2-<3','>=3']).astype(int)
            sub['control_bin']=parts[0].map(dict(zip(['<10','10-<50','50-<100','100-<200','200-<500','>=500'],range(6))))
            sub['d']=parts[2].map({'0<d<=1':0,'1<d<=6':1,'d>6':2})
            sub['stratum']=3*sub.control_bin+sub.d
            c=sub.groupby(['arm','stratum'])[['reference_pixels','fn']].sum()
            ww=w[(w.target=='il_2023')&(w.crop=='soybean')&(w.contrast_name=='shape_control_area_distance')&(w.rule=='primary')]
            for arm in [0,1]:
                for mode in ['distance_native','distance_equal']:
                    eligible=ww[(ww.arm==arm)&ww.eligible].set_index('stratum')
                    cc=c.loc[arm].loc[eligible.index]
                    value=(eligible['weight_'+mode]*cc.fn/cc.reference_pixels).sum()
                    rr=rates[(rates.kind=='within')&(rates.target=='il_2023')&(rates.crop=='soybean')&
                             (rates.model==model)&(rates.contrast_name=='shape_control_area_distance')&
                             (rates.rule=='primary')&(rates.arm==arm)&(rates.distance_mode==mode)].iloc[0]
                    self.assertAlmostEqual(value,rr.rate,places=12)

    def test_five_prediction_means_std_and_signs(self):
        s=read(OUT/'cross_group_advantages.csv')
        keys=['comparison_model','source','target','crop','scheme','group']
        data=self.p[self.p.kind.eq('cross')].set_index(keys).sort_index()
        for r in s.itertuples(index=False):
            g=data.loc[tuple(getattr(r,k) for k in keys)]
            self.assertEqual(set(g.fold),{1,2,3,4,5})
            for v in ['advantage','advantage_change','net_fewer_pixels']:
                vals=g[v].to_numpy()
                if np.isfinite(vals).all():
                    self.assertAlmostEqual(vals.mean(),getattr(r,v+'_mean'),places=11)
                    self.assertAlmostEqual(vals.std(ddof=1),getattr(r,v+'_std'),places=10)
                else:self.assertTrue(np.isnan(getattr(r,v+'_mean')))
                self.assertEqual(int((vals>0).sum()),getattr(r,v+'_positive'))
                self.assertEqual(int((vals<0).sum()),getattr(r,v+'_negative'))

    def test_reused_CD_identity_and_reading_table(self):
        old=read(ROOT/'results/processed/spatial_findings_refinement/standardized_rates_per_prediction.csv')
        old=old[(old.scheme=='a12d7')&(old.scope=='joint_CD')&(old.rule=='primary')].set_index(RUN)
        bridge=read(PROC/'refined_CD_bridge_per_prediction.csv')
        for r in bridge.itertuples(index=False):
            key=[r.kind,'convgru',r.source,r.target,r.fold]
            a=old.loc[tuple(key)];key[1]=r.comparison_model;b=old.loc[tuple(key)]
            self.assertAlmostEqual(r.change_high_minus_low_advantage,a.delta_gap_omission-b.delta_gap_omission,places=12)
        main=read(OUT/'main_reading_table.csv')
        self.assertEqual(len(main),16)
        self.assertFalse(main.duplicated(['target','crop','comparison_model']).any())
        self.assertTrue(main.within_advantage.gt(0).all())


if __name__=='__main__':
    unittest.main(verbosity=2)

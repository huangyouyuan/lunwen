"""Read-only checks, including direct-mask reconstruction of the C/D comparison."""
from pathlib import Path
import hashlib
import json
import unittest

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/summary/spatial_findings_refinement'
PROC=ROOT/'results/processed/spatial_findings_refinement'
REF=ROOT/'results/processed/sec33_reference_patch_types'
RUN=['kind','model','source','target','fold']


def read(path):return pd.read_csv(path,float_precision='round_trip')


class RefinementChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rates=read(PROC/'standardized_rates_per_prediction.csv')
        cls.ref=read(OUT/'reference_cells.csv')
        cls.cells=read(PROC/'cell_counts_per_prediction.csv')
        cls.features=read(REF/'reference_patch_features.csv')
        cls.index=read(REF/'prediction_count_index.csv')

    def test_manifest(self):
        m=json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
        for path,digest in (m['inputs']|m['outputs']).items():
            with self.subTest(path=path):
                self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest)
        self.assertEqual(hashlib.sha256((ROOT/'scripts/refine_spatial_findings.py').read_bytes()).hexdigest(),m['script_sha256'])
        self.assertTrue(read(OUT/'verification_checks.csv').status.eq('Verified').all())

    def test_existing_bubble_distribution_matches_error_support(self):
        bubble=read(ROOT/'results/summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv')
        support=read(ROOT/'results/summary/spatial_error_conditions/reference_group_support.csv')
        area=['<10','10-<50','50-<100','100-<200','200-<500','>=500']
        shape=['1-<1.5','1.5-<2','2-<3','>=3']
        bubble['group']=[area[a]+'|'+shape[h] for a,h in zip(bubble.area_bin_order,bubble.shape_bin_order)]
        keys=['target','crop','group']
        merged=bubble.merge(support[support.scheme.eq('area_shape')],on=keys,
                            validate='one_to_one',suffixes=('_bubble','_error'))
        self.assertEqual(len(bubble),192)
        self.assertEqual(len(merged),len(bubble))
        for field in ['patch_count','reference_pixels','singleton_patch_count','outer_edge_patch_count','outer_edge_pixels']:
            self.assertTrue(merged[field+'_bubble'].eq(merged[field+'_error']).all(),field)
        self.assertTrue(np.allclose(merged.area_share_pct/100,merged.area_share,atol=1e-14,rtol=0))
        self.assertTrue(np.allclose(bubble.groupby(['target','crop']).area_share_pct.sum(),100,atol=1e-12,rtol=0))
        soybean=bubble[bubble.crop.eq('soybean')&bubble.target.isin(['ida_2023','il_2023'])].copy()
        soybean['arm']=(soybean.shape_bin_order>=2).astype(int)
        grouped=soybean.groupby(['target','arm'])[['reference_pixels','patch_count']].sum()
        natural=read(OUT/'within_natural_shape_counts.csv')
        for row in natural.itertuples(index=False):
            saved=grouped.loc[(row.target,row.arm)]
            self.assertEqual(row.pixels,saved.reference_pixels)
            self.assertEqual(row.patch_count,saved.patch_count)

    def test_prediction_identity_and_count_closure(self):
        self.assertEqual(len(self.cells),27648)
        self.assertFalse(self.cells.duplicated(RUN+['scheme','arm','stratum']).any())
        totals=self.cells.groupby(RUN+['scheme'])[['pixels','to_corn','to_other','to_soybean']].sum().reset_index()
        for _,g in totals.groupby(RUN):
            self.assertEqual(set(g.scheme),{'a6d3','a6d7','a12d7'})
            self.assertTrue(g[['pixels','to_corn','to_other','to_soybean']].nunique().eq(1).all())
        native=read(PROC/'natural_shape_counts_per_prediction.csv')
        truth=read(ROOT/'results/processed/sec33_crop_spatial_context/whole_cm.csv').set_index(RUN)
        for key,g in native.groupby(RUN):
            cm=truth.loc[key]
            self.assertEqual(int(g.to_corn.sum()),int(cm.cm_2_0))
            self.assertEqual(int(g.to_other.sum()),int(cm.cm_2_1))
            self.assertEqual(int(g.to_soybean.sum()),int(cm.cm_2_2))
            self.assertEqual(set(g.arm),{0,1})
        s=read(OUT/'cross_natural_shape_counts.csv')
        self.assertTrue(np.allclose(s.groupby(['model','source','target']).ratio_of_mean_fn_net.sum(),1,atol=1e-12))

    def test_common_weights_and_coverage(self):
        weights=read(OUT/'common_support_weights.csv')
        cover=read(OUT/'coverage_and_reference_balance.csv')
        for key,g in weights.groupby(['scheme','scope','rule']):
            pools=[g[g.target==t] for t in g.target.unique()] if key[1]=='within_target' else [g]
            for pool in pools:
                table=pool.pivot(index='stratum',columns=['target','arm'],values='weight')
                self.assertTrue(np.allclose(table.values,table.iloc[:,[0]].values,atol=1e-14))
                self.assertTrue(np.allclose(table.sum(axis=0),1,atol=1e-12))
                n=pool.pivot(index='stratum',columns=['target','arm'],values='pixels')
                p=pool.pivot(index='stratum',columns=['target','arm'],values='patch_count')
                keep=((n>=1000)&(p>=10)).all(axis=1) if key[2]=='primary' else ((n>0)&(p>0)).all(axis=1)
                raw=(n/n.sum(axis=0)).min(axis=1)*keep
                self.assertTrue(np.allclose(raw/raw.sum(),table.iloc[:,0],atol=1e-12))
                for t,h in n.columns:
                    row=cover[(cover.scheme==key[0])&(cover.scope==key[1])&(cover.rule==key[2])&(cover.target==t)&(cover.arm==h)].iloc[0]
                    self.assertAlmostEqual(n.loc[keep,(t,h)].sum()/n[t,h].sum(),row.coverage,places=12)

    def test_direct_mask_fine_common_weight_and_directional_gap(self):
        edges=[0,1,10,25,50,75,100,150,200,350,500,1000,np.inf]
        arrays={}
        for target in ['ida_2023','il_2023']:
            f=self.features[(self.features.target==target)&(self.features.crop=='soybean')].iloc[::-1]
            out={}
            for kind,source,fold in [('within',target,0),('cross','iw2_2023',3)]:
                row=self.index[(self.index.kind==kind)&(self.index.model=='convgru')&(self.index.source==source)&(self.index.target==target)&(self.index.fold==fold)].iloc[0]
                with np.load(REF/row.file) as z:
                    byid={int(pid):i for i,pid in enumerate(z['PID'])}
                    data=z['patch_band_prediction_counts'][[byid[int(pid)] for pid in f.PID]].astype(np.int64)
                n=np.zeros((2,84),np.int64);p=np.zeros_like(n);e=np.zeros((2,84,2),np.int64)
                for arm in [0,1]:
                    for a,(lo,hi) in enumerate(zip(edges[:-1],edges[1:])):
                        mask=(f.AREA>=lo)&(f.AREA<hi)&((f.SHAPE>=2) if arm else (f.SHAPE<2))
                        for band in range(7):
                            cc=data[mask,band,:];k=a*7+band
                            n[arm,k]=cc.sum();p[arm,k]=(cc.sum(axis=1)>0).sum();e[arm,k]=cc[:,:2].sum(axis=0)
                out[kind]=(n,p,e)
            self.assertTrue(np.array_equal(out['within'][0],out['cross'][0]))
            arrays[target]=out
        alln=np.concatenate([a['within'][0] for a in arrays.values()])
        allp=np.concatenate([a['within'][1] for a in arrays.values()])
        keep=((alln>=1000)&(allp>=10)).all(axis=0)
        weight=(alln/alln.sum(axis=1)[:,None]).min(axis=0)*keep
        weight=weight/weight.sum()
        for target,a in arrays.items():
            n=a['within'][0]
            delta=a['cross'][2]-a['within'][2]
            scaled=(delta[:,keep,:]/n[:,keep,None]*weight[keep][None,:,None]).sum(axis=1)
            gap=scaled[1]-scaled[0]
            row=self.rates[(self.rates.model=='convgru')&(self.rates.target==target)&(self.rates.source=='iw2_2023')&(self.rates.fold==3)&
                           (self.rates.scheme=='a12d7')&(self.rates.scope=='joint_CD')&(self.rates.rule=='primary')].iloc[0]
            self.assertAlmostEqual(gap[0],row.delta_gap_corn,places=12)
            self.assertAlmostEqual(gap[1],row.delta_gap_other,places=12)
            self.assertAlmostEqual(gap.sum(),row.delta_gap_omission,places=12)

    def test_five_prediction_statistics_and_C_D_pairing(self):
        s=read(OUT/'cross_standardized_rates.csv')
        keys=['model','source','target','scheme','scope','rule']
        grouped=self.rates[self.rates.kind.eq('cross')].set_index(keys).sort_index()
        for row in s.itertuples(index=False):
            g=grouped.loc[tuple(getattr(row,k) for k in keys)]
            self.assertEqual(set(g.fold),{1,2,3,4,5})
            for v in ['gap_omission','delta_gap_omission','delta_gap_corn','delta_gap_other']:
                vals=g[v].to_numpy()
                self.assertAlmostEqual(vals.mean(),getattr(row,v+'_mean'),places=12)
                self.assertAlmostEqual(vals.std(ddof=1),getattr(row,v+'_std'),places=12)
                self.assertEqual(int((vals>0).sum()),getattr(row,v+'_positive'))
                self.assertEqual(int((vals<0).sum()),getattr(row,v+'_negative'))
        pair=read(PROC/'paired_C_D_per_prediction.csv')
        self.assertFalse(pair.duplicated(['model','source','fold','scheme','rule']).any())
        self.assertEqual(set(pair.source),{'iw_2023','iw2_2023'})
        for m in ['omission','corn','other']:
            self.assertTrue(np.allclose(pair['C_delta_gap_'+m]-pair['D_delta_gap_'+m],pair['C_minus_D_'+m],atol=1e-14))

    def test_additive_direction_and_stratum_closure(self):
        r=self.rates
        self.assertTrue(np.allclose(r.delta_gap_corn+r.delta_gap_other,r.delta_gap_omission,atol=1e-14))
        c=read(PROC/'stratum_gap_contributions_per_prediction.csv')
        self.assertTrue(c.loc[~c.eligible,'gap_omission_contribution'].eq(0).all())
        total=c.groupby(RUN+['scheme']).gap_omission_contribution.sum().sort_index()
        truth=r[(r.kind=='cross')&(r.scope=='joint_CD')&(r.rule=='primary')].set_index(RUN+['scheme']).delta_gap_omission.sort_index()
        self.assertTrue(total.index.equals(truth.index))
        self.assertTrue(np.allclose(total,truth,atol=1e-12))


if __name__=='__main__':unittest.main(verbosity=2)

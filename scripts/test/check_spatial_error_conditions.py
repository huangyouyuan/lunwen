"""Read-only independent checks of saved spatial error-condition tables."""
from pathlib import Path
import hashlib
import json
import unittest

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
SUM=ROOT/'results/summary/spatial_error_conditions'
PROC=ROOT/'results/processed/spatial_error_conditions'
REF=ROOT/'results/processed/sec33_reference_patch_types'
RUN=['kind','model','source','target','fold']
KEY=RUN+['crop','scheme','group']


def read(p):
    return pd.read_csv(p,float_precision='round_trip')


class SavedAnalysisChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g=read(PROC/'group_metrics_per_prediction.csv')
        cls.w=read(PROC/'whole_crop_per_prediction.csv')
        cls.s=read(SUM/'cross_group_metrics.csv')
        cls.f=read(REF/'reference_patch_features.csv')
        cls.ix=read(REF/'prediction_count_index.csv')

    def test_manifest_and_check_status(self):
        manifest=json.loads((SUM/'manifest.json').read_text(encoding='utf-8'))
        for relative,digest in (manifest['inputs']|manifest['outputs']).items():
            with self.subTest(path=relative):
                self.assertEqual(hashlib.sha256((ROOT/relative).read_bytes()).hexdigest(),digest)
        self.assertEqual(hashlib.sha256((ROOT/'scripts/analyze_spatial_error_conditions.py').read_bytes()).hexdigest(),manifest['script_sha256'])
        checks=read(SUM/'verification_checks.csv')
        self.assertTrue(checks.status.eq('Verified').all())

    def test_identity_closure_and_empty_groups(self):
        self.assertEqual(len(self.g),82176)
        self.assertFalse(self.g.duplicated(KEY).any())
        for _,g in self.g.groupby(['model','target','crop','scheme','group']):
            self.assertEqual(len(g[g.kind=='within']),1)
            self.assertEqual(len(g[g.kind=='cross']),15)
        total=self.g.groupby(RUN+['crop','scheme'])[['fn','within_fn','reference_pixels']].sum().reset_index()
        check=total.merge(self.w[RUN+['crop','fn','baseline_fn','pixels']],on=RUN+['crop'],validate='many_to_one',suffixes=('_group','_whole'))
        self.assertTrue(np.array_equal(check.fn_group,check.fn_whole))
        self.assertTrue(np.array_equal(check.within_fn,check.baseline_fn))
        self.assertTrue(np.array_equal(check.reference_pixels,check.pixels))
        empty=self.g[self.g.reference_pixels==0]
        self.assertGreater(len(empty),0)
        self.assertTrue(empty.omission_rate.isna().all())
        self.assertTrue(empty.delta_omission_rate.isna().all())
        self.assertTrue(empty.fn.eq(0).all())

    def test_direct_masks_against_saved_joint_groups(self):
        # Explicit feature-value masks, reverse feature order, and PID lookup;
        # independent of the production fine-cube and searchsorted grouping.
        for target in ['iw_2023','iw2_2023','ida_2023','il_2023']:
            for kind in ['within','cross']:
                run=self.ix[(self.ix.target==target)&(self.ix.kind==kind)].iloc[-1]
                f=self.f[self.f.target==target].iloc[::-1]
                with np.load(REF/run.file) as z:
                    pos={int(pid):i for i,pid in enumerate(z['PID'])}
                    a=z['patch_band_prediction_counts'][[pos[int(pid)] for pid in f.PID]].astype(np.int64)
                for crop in ['corn','soybean']:
                    mask=(f.crop==crop)&(f.AREA>=10)&(f.AREA<50)&(f.SHAPE>=1.5)&(f.SHAPE<2)&(f.ENN>=60)&(f.ENN<90)
                    exact=a[mask].sum(axis=(0,1))
                    row=self.g
                    for col in RUN: row=row[row[col]==run[col]]
                    row=row[(row.crop==crop)&(row.scheme=='area_shape_enn')&(row['group']=='10-<50|1.5-<2|60-<90')].iloc[0]
                    self.assertTrue(np.array_equal(exact,row[['to_corn','to_other','to_soybean']].to_numpy(np.int64)))
                    self.assertEqual(exact.sum(),int(f.loc[mask,'reference_pixels'].sum()))

    def test_five_prediction_mean_sd_and_signed_changes(self):
        # Select large, small, empty and interior groups from all 36 paths.
        sel=self.s[(self.s.scheme=='all')|((self.s.scheme=='area_shape')&self.s['group'].isin(['>=500|1-<1.5','<10|>=3']))|
                   ((self.s.scheme=='distance')&(self.s['group']=='d>6'))]
        by=self.g[self.g.kind=='cross'].set_index(['model','source','target','crop','scheme','group']).sort_index()
        for row in sel.itertuples(index=False):
            key=(row.model,row.source,row.target,row.crop,row.scheme,row.group)
            g=by.loc[key]
            self.assertEqual(set(g.fold),{1,2,3,4,5})
            for col in ['fn','delta_fn','omission_rate','delta_omission_rate','net_omission_contribution']:
                values=g[col].to_numpy(float)
                if np.isfinite(values).all():
                    self.assertAlmostEqual(float(values.mean()),getattr(row,col+'_mean'),places=10)
                    self.assertAlmostEqual(float(values.std(ddof=1)),getattr(row,col+'_std'),places=10)
                    self.assertEqual(int((values>0).sum()),getattr(row,col+'_positive'))
                    self.assertEqual(int((values<0).sum()),getattr(row,col+'_negative'))
                else:
                    self.assertTrue(np.isnan(getattr(row,col+'_mean')))

    def test_shape_contrast_from_direct_masks(self):
        contrast=read(PROC/'conditional_contrasts_per_prediction.csv')
        for target,model,source,fold in [('ida_2023','utae','ida_2023',0),('il_2023','convgru','iw2_2023',3)]:
            run=self.ix[(self.ix.target==target)&(self.ix.model==model)&(self.ix.source==source)&(self.ix.fold==fold)].iloc[0]
            f=self.f[(self.f.target==target)&(self.f.crop=='soybean')]
            with np.load(REF/run.file) as z:
                pos={int(pid):i for i,pid in enumerate(z['PID'])}
                a=z['patch_band_prediction_counts'][[pos[int(pid)] for pid in f.PID]].astype(np.int64)
            n=a.sum(axis=2); error=a[:,:,:2].sum(axis=2)
            refs=[[],[]]; errors=[[],[]]; patches=[[],[]]
            for lo,hi in zip([0,10,50,100,200,500],[10,50,100,200,500,np.inf]):
                for bands in [[0],[1,2,3,4,5],[6]]:
                    pn=n[:,bands].sum(axis=1); pe=error[:,bands].sum(axis=1)
                    for arm in [0,1]:
                        mask=(f.AREA>=lo)&(f.AREA<hi)&((f.SHAPE>=2) if arm else (f.SHAPE<2))
                        refs[arm].append(int(pn[mask].sum()));errors[arm].append(int(pe[mask].sum()))
                        patches[arm].append(int((pn[mask]>0).sum()))
            refs=np.array(refs);errors=np.array(errors);patches=np.array(patches)
            eligible=((refs>=1000)&(patches>=10)).all(axis=0)
            shares=refs/refs.sum(axis=1)[:,None]
            weights=np.minimum(shares[0],shares[1])[eligible];weights=weights/weights.sum()
            rates=errors[:,eligible]/refs[:,eligible]
            value=((rates[1]-rates[0])*weights).sum()
            saved=contrast[(contrast.target==target)&(contrast.model==model)&(contrast.source==source)&(contrast.fold==fold)&
                           (contrast.crop=='soybean')&(contrast.rule=='primary')&(contrast.contrast_name=='shape_control_area_distance')].iloc[0]
            self.assertAlmostEqual(value,saved.contrast,places=12)
            self.assertAlmostEqual(refs[1,eligible].sum()/refs[1].sum(),saved.high_coverage,places=12)

    def test_site_weights_and_decomposition(self):
        w=read(SUM/'site_common_support_weights.csv')
        for _,g in w.groupby(['scheme','crop','rule']):
            kept=g[g.eligible]
            unique=kept.drop_duplicates('group')
            self.assertAlmostEqual(unique.common_weight.sum(),1,places=12)
            table=kept.pivot(index='group',columns='target',values='site_retained_weight')
            self.assertTrue(np.allclose(table.sum(axis=0),1,rtol=0,atol=1e-12))
            got=unique.set_index('group').loc[table.index,'common_weight']
            self.assertTrue(np.allclose(table.mean(axis=1),got,rtol=0,atol=1e-12))
        d=read(SUM/'within_site_gap_decomposition.csv')
        self.assertTrue(np.allclose(d.composition_component+d.condition_rate_component,d.retained_native_gap,rtol=0,atol=1e-12))
        self.assertTrue(np.allclose(self.w.delta_fn_loss+self.w.delta_fp_loss,self.w.delta_f1,rtol=0,atol=1e-12))


if __name__=='__main__':
    unittest.main(verbosity=2)

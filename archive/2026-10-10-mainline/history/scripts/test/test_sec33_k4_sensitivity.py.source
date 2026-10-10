"""Only in-memory fixtures: saved assignment joins and K4 regrouping risks."""
from pathlib import Path
import sys
import unittest
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import explore_sec33_k4_sensitivity as m


class K4Tests(unittest.TestCase):
    def fixtures(self):
        f=pd.DataFrame(dict(target=['A','A','A'],PID=[2,1,3],crop=['corn','corn','other'],patch_uid=['a2','a1','a3']))
        a=pd.DataFrame(dict(target=['A','A'],PID=[1,2],crop=['corn','corn'],patch_uid=['a1','a2'],k2=[1,2],k4=[3,2]))
        k=f.copy();k['spatial_type']=[2,1,0]
        return f,a,k

    def test_identity_join_non_nested_and_shuffled(self):
        f,a,k=self.fixtures();z=m.join_assignments(f,a,k)
        self.assertEqual(z.PID.tolist(),[1,2]);self.assertEqual(z.spatial_type.tolist(),['K4-C3','K4-C2'])
        self.assertEqual(z.k2_type.tolist(),['K2-T1','K2-T2'])

    def test_reject_duplicate_missing_and_wrong_crop(self):
        f,a,k=self.fixtures()
        with self.assertRaises(ValueError):m.join_assignments(f,pd.concat([a,a.iloc[:1]]),k)
        with self.assertRaises(ValueError):m.join_assignments(f,a.iloc[:1],k)
        bad=a.copy();bad.loc[0,'crop']='soybean'
        with self.assertRaises(ValueError):m.join_assignments(f,bad,k)

    def test_integer_regroup_uses_pid_not_row_order(self):
        pc=np.zeros((5,7,3),dtype=np.int32)
        pc[1,0]=[4,1,0];pc[2,6]=[0,1,2];pc[3,1]=[1,3,0];pc[4,0]=[1,0,2]
        f=pd.DataFrame(dict(PID=[3,1,4,2],crop=['other','corn','soybean','corn'],k4=[0,3,4,4],reference_pixels=[4,5,3,3]))
        out=m.aggregate_array(pc,f)
        np.testing.assert_array_equal(out[3,0,0],[4,1,0]);np.testing.assert_array_equal(out[4,0,6],[0,1,2])
        np.testing.assert_array_equal(out.sum((0,1)),pc.sum(0));self.assertEqual(out[0,1].sum(),4)
        self.assertTrue(np.isnan(m.old.rates(out[3,0,1:].sum(0),0)['leakage']))
        with self.assertRaises(ValueError):m.aggregate_array(pc,f.iloc[:3])

    def test_pair_same_prediction_explicitly_and_preserve_mixed(self):
        rows=[]
        for fold in range(1,6):
            for typ in ['K4-C3','K4-C4']:
                rows.append(dict(model='m',source='B',target='D',fold=fold,crop='soybean',region='all',spatial_type=typ,
                    delta_leakage=.1 if typ=='K4-C3' else [-.2,.3,.4,-.1,.2][fold-1],pixels=10,type_pixels=10,n_patches=2,n_patches_with_support=2,boundary_share=.2,class_pixels=20))
        d=pd.DataFrame(rows).sample(frac=1,random_state=8)
        z=m.contrast_types(d,['delta_leakage']).sort_values('fold')
        np.testing.assert_allclose(z.C4_minus_C3_delta_leakage,[-.3,.2,.3,-.2,.1])
        summary=m.old.strict_summary(z,['model','source','target','crop','region'],['C4_minus_C3_delta_leakage'],[]).iloc[0]
        self.assertEqual(summary.C4_minus_C3_delta_leakage_direction,'mixed')
        with self.assertRaises(ValueError):m.contrast_types(d.iloc[1:],['delta_leakage'])


if __name__=='__main__':unittest.main()

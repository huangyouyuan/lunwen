"""In-memory tests only; no scientific files are written or removed."""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import explore_sec33_crop_spatial_context as m


class ContextTests(unittest.TestCase):
    def test_joint_exclusive_bits_close_but_inclusive_overlap(self):
        lab=np.array([[0,2],[1,0]],dtype='uint8');pred=np.array([[2,0],[0,0]],dtype='uint8')
        bands=np.array([[0,0],[1,6]],dtype='uint8');bits=np.array([[2,6],[0,1]],dtype='uint8')
        cm=m.count_prediction(lab,pred,bands,bits)
        np.testing.assert_array_equal(cm.sum((0,1)),np.array([[1,0,1],[1,0,0],[1,0,0]]))
        self.assertEqual(cm[0,6].sum(),1)
        self.assertEqual(cm[:,[2,3,6,7]].sum(),2)
        self.assertEqual(cm[:,[4,5,6,7]].sum(),1)

    def test_true_class_denominator_and_false_positives(self):
        cm=np.array([[8,1,1],[2,5,3],[1,2,6]])
        x=m.class_metrics(cm,2)
        self.assertAlmostEqual(x['leakage'],3/9)
        self.assertAlmostEqual(x['precision'],6/10)
        self.assertAlmostEqual(x['f1'],12/19)
        self.assertAlmostEqual(x['fn_component']+x['fp_component'],1-x['f1'])

    def test_zero_truth_with_false_positive_f1_zero(self):
        cm=np.array([[1,0,1],[0,1,0],[0,0,0]])
        x=m.class_metrics(cm,2)
        self.assertEqual(x['f1'],0)
        self.assertTrue(np.isnan(x['leakage']))
        self.assertTrue(np.isnan(m.class_metrics(np.zeros((3,3),int),2)['f1']))

    def test_five_not_silently_reduced(self):
        x=m.strict_stats([.1,-.1,np.nan,.2,-.2],range(1,6))
        self.assertTrue(np.isnan(x['mean']));self.assertEqual(x['n_valid'],4)
        self.assertEqual(x['direction'],'not_calculable')
        with self.assertRaises(ValueError):m.strict_stats([1,2,3,4],[1,2,3,4])
        with self.assertRaises(ValueError):m.strict_stats([1,2,3,4,5],[1,2,3,4,4])

    def test_baseline_join_uses_identity_not_position(self):
        frame=pd.DataFrame([dict(kind=k,model='m',source=s,target='t',fold=n,band=b,rate=v)
                            for k,s,n,b,v in [('within','t',0,'near',.4),('within','t',0,'far',.1),
                                             ('cross','a',1,'far',.05),('cross','a',1,'near',.3)]])
        z=m.add_baselines(frame.sample(frac=1,random_state=4),['band'],['rate'])
        c=z[z.kind.eq('cross')].set_index('band')
        self.assertAlmostEqual(c.loc['far','delta_rate'],-.05)
        self.assertAlmostEqual(c.loc['near','delta_rate'],-.1)

    def test_common_support_coverage_and_weights(self):
        n=np.array([[60,30,10,0,0,0,0],[20,60,0,20,0,0,0]])
        shared,w,cov=m.common_weights(n)
        np.testing.assert_allclose(cov,[.9,.8])
        np.testing.assert_allclose(w[:2],[(2/3+1/4)/2,(1/3+3/4)/2])
        self.assertAlmostEqual(w.sum(),1)
        self.assertAlmostEqual(m.weight_value([.2,.4,np.nan,np.nan,np.nan,np.nan,np.nan],w),.2*w[0]+.4*w[1])
        self.assertTrue(np.isnan(m.weight_value([np.nan,.4,0,0,0,0,0],w)))

    def test_matching_uses_both_independent_compositions(self):
        a=pd.DataFrame({'patch_id':[1,0],'corn_ratio':[.4,.5],'soybean_ratio':[.3,.4]})
        b=pd.DataFrame({'patch_id':[3,2],'corn_ratio':[.49,.39],'soybean_ratio':[.6,.31]})
        left,right,_=m.matching(a,b,['corn_ratio','soybean_ratio'],[.05,.05])
        self.assertEqual(left.patch_id.tolist(),[1]);self.assertEqual(right.patch_id.tolist(),[2])

    def test_four_f1_components_include_incoming_errors(self):
        w=np.array([[9,1,0],[1,7,2],[2,1,7]])
        arrays=[np.array([[8,1,1],[2,6,2],[k,2,8-k]]) for k in range(1,6)]
        for crop in [0,2]:
            baseline=m.f1_error_components(w,crop)
            deltas=[sum(m.f1_error_components(a,crop).values())-sum(baseline.values()) for a in arrays]
            expected=m.class_metrics(w,crop)['f1']-np.mean([m.class_metrics(a,crop)['f1'] for a in arrays])
            self.assertAlmostEqual(np.mean(deltas),expected)
            self.assertAlmostEqual(baseline[('incoming',m.CLASSES[1])],w[1,crop]/(w[crop].sum()+w[:,crop].sum()))

    def test_class_weighted_contribution_with_absent_type(self):
        reference=np.array([4,0,6]);within=np.array([1,0,2]);cross=np.array([0,0,4])
        contribution=(cross-within)/reference.sum()
        self.assertAlmostEqual(contribution.sum(),(cross.sum()-within.sum())/reference.sum())
        self.assertEqual(contribution[1],0)
        self.assertLess(contribution[0],0)


if __name__=='__main__':unittest.main()

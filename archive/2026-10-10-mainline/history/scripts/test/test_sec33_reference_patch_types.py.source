"""In-memory checks of new whole-patch joins, counts, rates and folds."""
import sys
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import explore_sec33_reference_patch_types as m


class ReferencePatchTests(unittest.TestCase):
    def test_diagonal_connectivity_and_nonmatching_ids(self):
        label=np.array([[1,2,2],[2,1,2],[2,2,3]])
        ids=np.array([[18,7,7],[7,18,7],[7,7,31]])
        a=m.component_mapping(label,ids)
        self.assertEqual({x[0] for x in a},{18,7,31})

    def test_id_crossing_class_or_splitting_component_rejected(self):
        with self.assertRaises(ValueError):m.component_mapping(np.array([[1,1],[2,2]]),np.array([[7,8],[9,9]]))
        with self.assertRaises(ValueError):m.component_mapping(np.array([[1,1],[2,2]]),np.full((2,2),7))

    def test_patch_band_counts_and_zero_support(self):
        ids=np.array([[2,2],[4,4]]);bands=np.array([[0,1],[0,6]]);pred=np.array([[0,2],[1,2]])
        c=m.count_patch_prediction(ids,bands,pred)
        self.assertEqual(c.sum(),4);self.assertEqual(c[2,0,0],1);self.assertEqual(c[4,6,2],1)
        self.assertTrue(np.isnan(m.rates(c[2,2],0)['leakage']))
        self.assertEqual(m.rates(c[4].sum(0),2)['leakage'],.5)

    def test_directional_errors_use_true_class_denominator(self):
        r=m.rates([3,2,5],2)
        self.assertEqual(r['other_crop_rate'],.3);self.assertEqual(r['other_rate'],.2)
        self.assertEqual(r['leakage'],.5);self.assertNotIn('f1',r)

    def test_join_by_identity_and_negative_changes(self):
        d=pd.DataFrame([dict(kind=k,model='m',source=s,target='D',crop='soybean',spatial_type=t,region='all',pixels=10,leakage=e)
                        for k,s,t,e in [('within','D',2,.8),('within','D',1,.4),('cross','B',1,.2),('cross','B',2,.9)]])
        x=m.join_baseline(d,['region'],['pixels','leakage'])
        self.assertAlmostEqual(x[x.spatial_type==1].delta_leakage.iloc[0],-.2)
        self.assertAlmostEqual(x[x.spatial_type==2].delta_leakage.iloc[0],.1)

    def test_five_predictions_and_na_not_equal(self):
        d=pd.DataFrame(dict(group=['a']*5,fold=[5,3,1,4,2],rate=[.1,np.nan,-.1,.2,.3]))
        z=m.strict_summary(d,['group'],['rate'],[]).iloc[0]
        self.assertTrue(np.isnan(z.rate_mean));self.assertEqual(z.rate_n_valid,4)
        self.assertEqual(z.rate_direction,'not_calculable')
        with self.assertRaises(ValueError):m.strict_summary(d.iloc[:4],['group'],['rate'],[])
        bad=d.copy();bad.loc[0,'fold']=3
        with self.assertRaises(ValueError):m.strict_summary(bad,['group'],['rate'],[])

    def test_reference_transform_is_common_and_positive(self):
        f=pd.DataFrame(dict(AREA=[.09,9.],SHAPE=[1.,2.],ENN=[60.,120.]))
        z=m.feature_matrix(f);np.testing.assert_allclose(np.exp(z),f.to_numpy())

    def test_whole_miss_is_no_correct_not_any_error(self):
        counts=np.array([[0,4,0],[1,3,0],[4,0,0]])
        whole_miss=counts[:,0]==0
        self.assertEqual(whole_miss.tolist(),[True,False,False])
        self.assertEqual((counts.sum(1)-counts[:,0]>0).sum(),2)


if __name__=='__main__':unittest.main()

"""Scientific aggregation and identity regressions; in-memory inputs only."""
import sys
from pathlib import Path
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from explore_sec33_f1_raw_scale import (metrics, strict_five, validate_target_patches,
                                      MODELS, SITES, trend, rank_string)


class RawScaleGroupTests(unittest.TestCase):
    def five(self, values):
        return pd.DataFrame({'fold': range(1, 6), 'f1': values})

    def test_zero_baseline_is_valid_and_negative_retained(self):
        r = strict_five(self.five([.1, .2, .3, .4, .5]), 0.)
        self.assertAlmostEqual(r['delta_f1'], -.3)
        self.assertEqual(r['delta_status'], 'defined')
        self.assertAlmostEqual(r['cross_f1_std'], np.std([.1, .2, .3, .4, .5], ddof=1))

    def test_absent_class_distinguishes_zero_from_undefined(self):
        empty = np.zeros((3, 3), dtype=int)
        self.assertTrue(np.isnan(metrics(empty, 'corn')['f1']))
        empty[1, 0] = 7
        self.assertEqual(metrics(empty, 'corn')['f1'], 0.)
        self.assertEqual(metrics(empty, 'corn')['false_positive_pixels'], 7)
        self.assertEqual(strict_five(self.five([0]*5), 0)['delta_f1'], 0)

    def test_undefined_fifth_prediction_does_not_shrink_denominator(self):
        r = strict_five(self.five([.7, .8, .9, 1., np.nan]), .9)
        self.assertEqual(r['n_defined_f1'], 4)
        for field in ['cross_f1_mean', 'cross_f1_std', 'delta_f1']:
            self.assertTrue(np.isnan(r[field]))

    def test_undefined_baseline_preserves_cross_scores(self):
        r = strict_five(self.five([.8]*5), np.nan)
        self.assertAlmostEqual(r['cross_f1_mean'], .8)
        self.assertTrue(np.isnan(r['delta_f1']))

    def test_incomplete_or_duplicate_prediction_identity_rejected(self):
        with self.assertRaisesRegex(ValueError, 'five distinct'):
            strict_five(self.five([.8]*5).iloc[:4], .9)
        x = self.five([.8]*5)
        x.loc[4, 'fold'] = 4
        with self.assertRaisesRegex(ValueError, 'five distinct'):
            strict_five(x, .9)

    def test_mean_of_five_f1_is_not_f1_of_combined_matrices(self):
        matrices = [np.array([[8, 2, 0], [0, 0, 0], [0, 0, 0]])] * 4
        matrices += [np.array([[0, 1, 0], [9, 0, 0], [0, 0, 0]])]
        scores = [metrics(m, 'corn')['f1'] for m in matrices]
        r = strict_five(self.five(scores), .9)
        self.assertAlmostEqual(r['cross_f1_mean'], sum(scores)/5)
        self.assertNotAlmostEqual(r['cross_f1_mean'], metrics(sum(matrices), 'corn')['f1'])

    def test_wrong_target_patch_rejected_even_with_expected_counts(self):
        features = pd.DataFrame([{'dataset_id':t, 'patch_uid':f'{t}__p{i:04d}'}
                                 for t in SITES for i in range(400)])
        rows = pd.DataFrame([{'model':m, 'target':t, 'patch_uid':f'{t}__p{i:04d}'}
                             for m in MODELS for t in SITES for i in range(400)])
        rows.loc[0, 'patch_uid'] = f'{SITES[1]}__p0000'
        with self.assertRaisesRegex(ValueError, 'target patch set mismatch'):
            validate_target_patches(rows, features, False)

    def test_source_rank_reversal_is_one_algebraic_fact(self):
        z = pd.DataFrame({'source':['A', 'B', 'C'], 'cross':[.8, .81, .81]})
        z['delta'] = .9 - z.cross
        self.assertEqual(rank_string(z, 'source', 'cross'), 'B=C>A')
        self.assertEqual(rank_string(z, 'source', 'delta', False), 'B=C<A')
        self.assertEqual(trend([.03, .01, .02]), 'nonmonotonic')


if __name__ == '__main__':
    unittest.main()

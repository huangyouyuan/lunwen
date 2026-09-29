"""Edge cases that matter to the frozen scientific protocol; no mock outputs saved."""
import unittest
import numpy as np
from explore_sec33 import split_values, metrics, dr


class ProtocolTests(unittest.TestCase):
    def test_right_closed_and_linear_quantiles(self):
        groups, q, cuts, _ = split_values([0, 1, 2, 3, 4, 5, 6])
        self.assertEqual(q, [2, 4])
        self.assertEqual(groups.tolist(), ['low', 'low', 'low', 'mid', 'mid', 'high', 'high'])
        self.assertEqual(cuts, q)

    def test_ties_not_split(self):
        groups, q, cuts, reason = split_values([1, 1, 1, 1, 1, 2])
        self.assertEqual(groups.tolist(), ['low']*5 + ['high'])
        self.assertEqual(cuts, [1])
        self.assertIn('duplicate', reason)

    def test_maximum_and_all_equal(self):
        groups, _, cuts, _ = split_values([1, 2, 2, 2, 2, 2])
        self.assertEqual(groups.tolist(), ['all']*6)
        self.assertEqual(cuts, [])
        self.assertEqual(split_values([3, 3, 3])[0].tolist(), ['all']*3)

    def test_missing(self):
        groups, _, _, _ = split_values([np.nan, np.inf, -np.inf])
        self.assertEqual(groups.tolist(), ['missing']*3)

    def test_empty_interpolated_interval(self):
        groups, _, cuts, reason = split_values([0, 10])
        self.assertEqual(groups.tolist(), ['low', 'high'])
        self.assertEqual(cuts, [0])
        self.assertIn('empty_interval', reason)

    def test_absent_class(self):
        cm = np.zeros((3, 3), dtype=int)
        self.assertTrue(np.isnan(metrics(cm, 'corn')['f1']))
        cm[1, 0] = 4
        r = metrics(cm, 'corn')
        self.assertEqual(r['f1'], 0)
        self.assertEqual(r['false_positive_pixels'], 4)
        self.assertTrue(np.isnan(dr(0, 0)))

    def test_pooled_f1_not_patch_average(self):
        a = np.array([[8, 2, 0], [0, 0, 0], [0, 0, 0]])
        b = np.array([[0, 1, 0], [9, 0, 0], [0, 0, 0]])
        self.assertAlmostEqual(metrics(a+b, 'corn')['f1'], 16/28)
        self.assertNotAlmostEqual(metrics(a+b, 'corn')['f1'], (metrics(a, 'corn')['f1']+metrics(b, 'corn')['f1'])/2)
        self.assertAlmostEqual(dr(.8, .6), 25)


if __name__ == '__main__':
    unittest.main()

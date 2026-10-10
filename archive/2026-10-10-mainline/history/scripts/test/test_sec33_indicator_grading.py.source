"""In-memory checks for numerical-distribution and denominator risks."""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_sec33_indicator_grading as m


class GradingPreparationTests(unittest.TestCase):
    def fixture(self):
        return pd.DataFrame(dict(PID=[5, 2, 8, 1], AREA=[.09, .09, .09000000000000001, np.nan],
                                 reference_pixels=[1, 1, 10, 5], boundary_pixels=[1, 1, 2, 1],
                                 interior_pixels=[0, 0, 8, 4], no_interior=[True, True, False, False],
                                 touches_outer_edge=[False, True, False, False]))

    def test_ties_exact_values_and_missing_denominators(self):
        f = self.fixture()
        z = m.value_frequency(f, 'AREA')
        self.assertEqual(len(z), 2)
        self.assertEqual(z.n_patches.tolist(), [2, 1])
        self.assertEqual(z.pixels.tolist(), [2, 10])
        self.assertEqual(z.cumulative_pixels.tolist(), [2, 12])
        self.assertEqual(z.singleton_count.tolist(), [2, 0])
        self.assertEqual(z.no_interior_pixels.sum(), 2)
        self.assertEqual(z.edge_pixels.sum(), 1)
        self.assertEqual(z.area_cdf.iloc[-1], 1)
        self.assertAlmostEqual(z.area_share.iloc[0], 2 / 12)
        self.assertAlmostEqual(z.patch_share.iloc[0], 2 / 3)

    def test_area_weighted_quantile_is_not_patch_quantile(self):
        q = m.inverse_ecdf([1, 2, 3], np.array([1, 2, 7]), [0, .1, .3, .5, 1])
        np.testing.assert_array_equal(q, [1, 1, 2, 3, 3])
        self.assertEqual(np.quantile([1, 2, 3], .5), 2)

    def test_weighted_order_and_ties(self):
        q = m.inverse_ecdf([3, 1, 1], np.array([5, 2, 3]), [.5, .50001])
        np.testing.assert_array_equal(q, [1, 3])

    def test_bad_weights_and_empty_quantiles(self):
        for w in [np.array([1., 2.]), np.array([0, 2]), np.array([-1, 2])]:
            with self.assertRaises(ValueError):
                m.inverse_ecdf([1, 2], w, [.5])
        with self.assertRaises(ValueError):
            m.inverse_ecdf([np.nan], np.array([1]), [.5])
        with self.assertRaises(ValueError):
            m.inverse_ecdf([1], np.array([1]), [1.1])
        self.assertTrue(np.isnan(m.inverse_ecdf([], np.array([], dtype=int), [.5])[0]))

    def test_cdf_gap_uses_union_and_left_zero(self):
        a = pd.DataFrame(dict(value=[1, 3], patch_cdf=[.5, 1.]))
        b = pd.DataFrame(dict(value=[2, 3], patch_cdf=[.75, 1.]))
        self.assertEqual(m.cdf_gap(a, b, 'patch_cdf'), .5)
        self.assertEqual(m.cdf_gap(b, a, 'patch_cdf'), .5)
        self.assertEqual(m.cdf_gap(a, a, 'patch_cdf'), 0)

    def test_reference_domains_do_not_duplicate_within_view(self):
        f = pd.DataFrame([dict(target=t, crop=c, PID=1) for t in m.SITES for c in m.CROPS])
        groups = list(m.domains(f))
        self.assertEqual(len(groups), 11)
        self.assertEqual(sum(len(z) for d, _, _, z in groups if d == 'site_crop'), len(f))
        self.assertEqual(sum(len(z) for d, _, _, z in groups if d == 'crop'), len(f))


if __name__ == '__main__':
    unittest.main()

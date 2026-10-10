"""Only new grade endpoint, identity-independent counting and exclusion risks."""
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_sec33_common_five_grades as m


class CommonFiveGradeTests(unittest.TestCase):
    def test_decimal_area_thresholds_and_integer_endpoints(self):
        self.assertEqual(m.pixel_cuts([1, 10, 50, 150]), [11, 111, 555, 1666])
        self.assertEqual(m.pixel_cuts([42.48, 86.49, 134.91, 204.12]), [472, 961, 1499, 2268])
        values = [1, 11, 12, 111, 112, 555, 556, 1666, 1667]
        np.testing.assert_array_equal(m.classify(values, [11, 111, 555, 1666], integer=True),
                                      [1, 1, 2, 2, 3, 3, 4, 4, 5])

    def test_shape_reverse_cutpoints_and_adjacent_values(self):
        values = [1, 1.3, np.nextafter(1.3, np.inf), 1.6, np.nextafter(1.6, np.inf),
                  2, np.nextafter(2, np.inf), 2.5, np.nextafter(2.5, np.inf), 9]
        np.testing.assert_array_equal(m.classify(values, m.SHAPE_CUTS, reverse=True, minimum=1),
                                      [5, 5, 4, 4, 3, 3, 2, 2, 1, 1])

    def test_ties_never_split_and_order_never_used(self):
        values = np.array([2.5, 1, 2.5, 1.6, 1])
        first = m.classify(values, m.SHAPE_CUTS, reverse=True, minimum=1)
        order = np.array([4, 2, 1, 0, 3])
        np.testing.assert_array_equal(m.classify(values[order], m.SHAPE_CUTS, reverse=True, minimum=1), first[order])
        self.assertEqual(first[0], first[2])

    def test_invalid_is_separate_not_zero_grade(self):
        np.testing.assert_array_equal(m.classify([np.nan, np.inf, -1, 0, .5, 1], m.SHAPE_CUTS,
                                                 reverse=True, minimum=1), [0, 0, 0, 0, 0, 5])
        np.testing.assert_array_equal(m.classify([1.5, 0, np.nan, 1], [11, 111, 555, 1666],
                                                 integer=True), [0, 0, 0, 1])

    def test_area_requires_valid_saved_metric_and_count_agreement(self):
        f = pd.DataFrame(dict(reference_pixels=[1, 11, 12, 12, 12],
                              AREA=[.09, .99, 1.08, np.nan, 99.]))
        np.testing.assert_array_equal(m.assign(f, 'AREA', [11, 111, 555, 1666]), [1, 1, 2, 0, 0])

    def test_bad_cut_configuration_rejected(self):
        for cuts in [[1, 2, 3], [1, 2, 2, 3], [1, 2, np.nan, 4]]:
            with self.assertRaises(ValueError):
                m.classify([1, 2], cuts)

    def test_support_uses_pixel_sums_and_overlapping_flags(self):
        f = pd.DataFrame(dict(target=['iw_2023'] * 3, crop=['corn'] * 3, PID=[7, 2, 9],
                              reference_pixels=[1, 11, 12], boundary_pixels=[1, 4, 3],
                              interior_pixels=[0, 7, 9], far_interior_pixels=[0, 2, 4],
                              touches_outer_edge=[True, False, True]))
        rows = pd.DataFrame(m.support_rows(f, np.array([1, 1, 2])))
        pooled = rows.loc[rows.domain.eq('all')]
        g1 = pooled.loc[pooled.grade_number.eq(1)].iloc[0]
        self.assertEqual(g1.n_patches, 2)
        self.assertEqual(g1.pixels, 12)
        self.assertEqual(g1.boundary_pixels, 5)
        self.assertEqual(g1.interior_pixels, 7)
        self.assertEqual(g1.singleton_count, 1)
        self.assertEqual(g1.no_interior_patches, 1)
        self.assertEqual(g1.edge_patches, 1)
        self.assertEqual(pooled.pixels.sum(), 24)
        self.assertEqual(pooled.n_patches.sum(), 3)
        self.assertAlmostEqual(g1.patch_share, 2 / 3)
        self.assertAlmostEqual(g1.area_share, .5)
        self.assertTrue(pooled.loc[pooled.grade_number.eq(5), 'boundary_share'].isna().all())

    def test_exclusions_do_not_silently_reduce_domain_denominator(self):
        f = pd.DataFrame(dict(target=['iw_2023'] * 2, crop=['corn'] * 2, PID=[1, 2],
                              reference_pixels=[1, 9], boundary_pixels=[1, 2],
                              interior_pixels=[0, 7], far_interior_pixels=[0, 2],
                              touches_outer_edge=[False, False]))
        pooled = pd.DataFrame(m.support_rows(f, np.array([1, 0])))
        pooled = pooled.loc[pooled.domain.eq('all')]
        g1 = pooled.iloc[0]
        self.assertEqual(g1.domain_n_patches, 2)
        self.assertEqual(g1.valid_n_patches, 1)
        self.assertEqual(g1.domain_pixels, 10)
        self.assertEqual(g1.valid_pixels, 1)
        self.assertEqual(g1.area_share, .1)
        self.assertEqual(g1.patch_share, .5)


if __name__ == '__main__':
    unittest.main()

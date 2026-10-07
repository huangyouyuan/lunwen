import unittest

import numpy as np

from scripts.explore_sec33_directional_confusion import f1_from_matrix, five_stats


class DirectionalConfusionTests(unittest.TestCase):
    def test_f1_components_from_integer_matrix(self):
        cm = np.array([[8, 1, 1], [2, 7, 1], [1, 2, 7]], dtype=np.int64)
        f1, precision, recall, leakage, tp, fn, fp = f1_from_matrix(cm, 0)
        self.assertEqual((tp, fn, fp), (8, 2, 3))
        self.assertAlmostEqual(recall, 8 / 10)
        self.assertAlmostEqual(precision, 8 / 11)
        self.assertAlmostEqual(f1, 2 * (8 / 11) * (8 / 10) / ((8 / 11) + (8 / 10)))
        self.assertAlmostEqual(leakage, 0.2)

    def test_directional_errors_recover_crop_leakage(self):
        cm = np.array([[8, 1, 1], [2, 7, 1], [1, 2, 7]], dtype=np.int64)
        for cls in range(3):
            leakage = (cm[cls].sum() - cm[cls, cls]) / cm[cls].sum()
            directional = sum(cm[cls, pc] for pc in range(3) if pc != cls) / cm[cls].sum()
            self.assertAlmostEqual(leakage, directional)

    def test_five_stats_requires_all_five_for_mean(self):
        out = five_stats(np.array([0.1, np.nan, 0.2, 0.3, 0.4]), "delta")
        self.assertTrue(np.isnan(out["delta_mean"]))
        self.assertEqual(out["delta_n_valid"], 4)
        self.assertEqual(out["delta_direction"], "not_calculable")

    def test_five_stats_preserves_mixed_signs(self):
        out = five_stats(np.array([-0.1, 0.0, 0.2, -0.2, 0.1]), "delta")
        self.assertEqual(out["delta_direction"], "mixed")
        self.assertEqual(out["delta_positive"], 2)
        self.assertEqual(out["delta_negative"], 2)
        self.assertEqual(out["delta_zero"], 1)


if __name__ == "__main__":
    unittest.main()

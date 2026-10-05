#!/usr/bin/env python3
"""In-memory tests for the second-round D soybean decomposition."""
import sys
from pathlib import Path
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from explore_sec33_round2 import (COMPONENTS, error_components, direction_label,
                                  f1_from_cm, validate_component_sum)


class Round2Tests(unittest.TestCase):
    def test_four_directions_sum_to_one_minus_f1(self):
        cm = np.array([[80, 5, 7], [4, 50, 6], [9, 8, 90]], dtype=int)
        r = error_components(cm)
        self.assertAlmostEqual(r["component_sum"], 1 - r["soybean_f1"], places=14)
        self.assertAlmostEqual(r["component_sum_error"], 0.0, places=14)
        self.assertAlmostEqual(r["soybean_recall"], 90 / (90 + 9 + 8))
        self.assertAlmostEqual(r["soybean_precision"], 90 / (90 + 7 + 6))

    def test_requested_error_directions_use_correct_cells(self):
        cm = np.zeros((3, 3), dtype=int)
        cm[2, 0], cm[2, 1], cm[0, 2], cm[1, 2], cm[2, 2] = 11, 13, 17, 19, 100
        r = error_components(cm)
        self.assertEqual(r["soy_to_corn_pixels"], 11)
        self.assertEqual(r["soy_to_other_pixels"], 13)
        self.assertEqual(r["corn_to_soy_pixels"], 17)
        self.assertEqual(r["other_to_soy_pixels"], 19)
        self.assertEqual(r["true_soybean_pixels"], 124)
        self.assertEqual(r["predicted_soybean_pixels"], 136)

    def test_zero_z_is_nan_and_not_silently_zero(self):
        r = error_components(np.zeros((3, 3), dtype=int))
        for field in ["soybean_f1", "soybean_precision", "soybean_recall", "Z", "component_sum"]:
            self.assertTrue(np.isnan(r[field]) if field != "Z" else r[field] == 0)
        self.assertTrue(all(np.isnan(r[f"{c}_component"]) for c in COMPONENTS))

    def test_per_prediction_components_are_not_component_of_merged_matrix(self):
        cm_a = np.array([[80, 0, 20], [0, 80, 20], [20, 20, 80]], dtype=int)
        cm_b = np.array([[80, 0, 0], [0, 80, 0], [0, 0, 1]], dtype=int)
        a, b = error_components(cm_a), error_components(cm_b)
        mean_component = np.mean([a["soy_to_corn_component"], b["soy_to_corn_component"]])
        merged = error_components(cm_a + cm_b)["soy_to_corn_component"]
        self.assertNotAlmostEqual(mean_component, merged)

    def test_direction_label_requires_five_defined_values(self):
        self.assertEqual(direction_label(np.array([1, 2, 3, 4, 5])), "all_positive")
        self.assertEqual(direction_label(np.array([-1, -2, -3, -4, -5])), "all_negative")
        self.assertEqual(direction_label(np.array([1, -1, 1, -1, 0])), "mixed")
        self.assertEqual(direction_label(np.array([1, np.nan, 1, 1, 1])), "undefined")

    def test_component_closure_checker(self):
        rows = []
        for value in [0.1, 0.2]:
            row = {f"{c}_component": value / 4 for c in COMPONENTS}
            row["soybean_f1"] = 1 - value
            rows.append(row)
        import pandas as pd
        ok, maximum = validate_component_sum(pd.DataFrame(rows))
        self.assertTrue(ok)
        self.assertLessEqual(maximum, 1e-12)


if __name__ == "__main__":
    unittest.main()

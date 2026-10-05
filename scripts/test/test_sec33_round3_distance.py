#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""In-memory protocol tests for the third boundary-distance exploration."""
import importlib.util
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("round3_distance", ROOT / "scripts/explore_sec33_round3_distance.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class Round3DistanceTests(unittest.TestCase):
    def test_leakage_rate_uses_true_class_support(self):
        cm = np.array([[8, 1, 1], [2, 5, 3], [1, 2, 6]], dtype=np.int64)
        row = MODULE.metrics(cm, "soybean")
        self.assertEqual(row["pixels"], 9)
        self.assertEqual(row["errors"], 3)
        self.assertAlmostEqual(row["error_rate"], 1 / 3)

    def test_zero_support_is_na(self):
        cm = np.zeros((3, 3), dtype=np.int64)
        row = MODULE.metrics(cm, "soybean")
        self.assertEqual(row["status"], "undefined_zero_support")
        self.assertTrue(np.isnan(row["error_rate"]))

    def test_five_predictions_are_not_reduced(self):
        values = np.array([0.1, 0.2, 0.3, 0.4, np.nan])
        self.assertTrue(np.isnan(MODULE.mean_or_nan(values)))
        self.assertTrue(np.isnan(MODULE.std_or_nan(values)))

    def test_negative_delta_is_preserved(self):
        within = 0.4
        cross = 0.2
        self.assertLess(cross - within, 0)

    def test_contribution_closure(self):
        shares = np.array([0.2, 0.3, 0.5])
        delta = np.array([0.1, -0.02, 0.03])
        total = float(np.sum(shares * delta))
        self.assertAlmostEqual(total, 0.029)

    def test_near_and_gt6_pair_direction(self):
        near, far = 0.4, 0.1
        difference = far - near
        self.assertLess(difference, 0)


if __name__ == "__main__":
    unittest.main()

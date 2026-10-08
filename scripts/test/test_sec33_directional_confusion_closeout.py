import importlib.util
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/explore_sec33_directional_confusion_closeout.py"
spec = importlib.util.spec_from_file_location("closeout", SCRIPT)
closeout = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(closeout)


class DirectionalCloseoutTests(unittest.TestCase):
    def test_f1_zero_with_errors(self):
        m = np.array([[0, 4, 2], [1, 8, 1], [2, 1, 7]], dtype=np.int64)
        f1, precision, recall, *_ = closeout.base.f1_from_matrix(m, 0)
        self.assertEqual(f1, 0.0)
        self.assertEqual(precision, 0.0)
        self.assertEqual(recall, 0.0)

    def test_f1_no_true_support_but_false_positive_is_zero(self):
        m = np.array([[0, 0, 0], [1, 8, 1], [2, 1, 7]], dtype=np.int64)
        f1, precision, recall, *_ = closeout.base.f1_from_matrix(m, 0)
        self.assertEqual(f1, 0.0)
        self.assertTrue(np.isnan(recall))
        self.assertEqual(precision, 0.0)

    def test_f1_true_support_without_predictions_is_zero(self):
        m = np.array([[0, 4, 2], [0, 8, 1], [0, 1, 7]], dtype=np.int64)
        f1, precision, recall, *_ = closeout.base.f1_from_matrix(m, 0)
        self.assertEqual(f1, 0.0)
        self.assertEqual(recall, 0.0)
        self.assertTrue(np.isnan(precision))

    def test_f1_no_true_or_predicted_support_is_na(self):
        m = np.array([[0, 0, 0], [0, 8, 1], [0, 1, 7]], dtype=np.int64)
        f1, precision, recall, *_ = closeout.base.f1_from_matrix(m, 0)
        self.assertTrue(np.isnan(f1))
        self.assertTrue(np.isnan(recall))
        self.assertTrue(np.isnan(precision))

    def test_f1_normal_input_unchanged(self):
        m = np.array([[8, 1, 1], [2, 7, 1], [1, 2, 7]], dtype=np.int64)
        f1, *_ = closeout.base.f1_from_matrix(m, 0)
        self.assertAlmostEqual(f1, 16 / 21)

    def test_bitmask_groups_are_mutually_exclusive(self):
        for cls in closeout.CLASSES:
            groups = [closeout.group_for(cls, i) for i in range(8)]
            self.assertEqual(set(groups), set(closeout.GROUPS))

    def test_class_specific_contact_mapping(self):
        for cls, pairs in closeout.CONTACTS.items():
            b1, b2 = pairs[0][1], pairs[1][1]
            self.assertEqual(closeout.group_for(cls, 0), "nearest_no_direct")
            self.assertEqual(closeout.group_for(cls, b1), "contact_1_only")
            self.assertEqual(closeout.group_for(cls, b2), "contact_2_only")
            self.assertEqual(closeout.group_for(cls, b1 | b2), "mixed")

    def test_exclusive_aggregation_restores_counts_and_overlap(self):
        rows = []
        for bit in range(8):
            m = np.zeros((3, 3), dtype=np.int64)
            for i, cls in enumerate(closeout.CLASSES):
                relevant = closeout.CONTACTS[cls][0][1] | closeout.CONTACTS[cls][1][1]
                if not bit & (7 ^ relevant):
                    m[i] = np.array([1, 2, 3]) * (bit + 1)
            rows.append(dict(kind="within", model="convgru", source="il_2023", target="il_2023", fold=0,
                             band=closeout.NEAREST, bitmask=bit,
                             **dict(zip(closeout.CM_COLS, m.ravel()))))
        raw = pd.DataFrame(rows)
        grouped, _ = closeout.exclusive_counts(raw.sample(frac=1, random_state=42))
        for i, cls in enumerate(closeout.CLASSES):
            g = grouped[grouped.true_class.eq(cls)].set_index("exclusive_boundary_group")
            pred = ["pred_" + c for c in closeout.CLASSES]
            np.testing.assert_array_equal(g[pred].sum(), raw[[f"cm_{i}_{j}" for j in range(3)]].sum())
            for j, (_, bit) in enumerate(closeout.CONTACTS[cls]):
                overlap = raw[raw.bitmask.map(lambda b: bool(b & bit))][[f"cm_{i}_{k}" for k in range(3)]].sum()
                np.testing.assert_array_equal(g.loc[[closeout.GROUPS[j], "mixed"], pred].sum(), overlap)

    def test_five_stats_preserves_na_negative_and_mixed_directions(self):
        s = closeout.five_stats([-.1, .2, 0, np.nan, -.2], "delta")
        self.assertTrue(np.isnan(s["delta_mean"]))
        self.assertTrue(np.isnan(s["delta_std"]))
        self.assertEqual(s["delta_n_valid"], 4)
        self.assertEqual(s["delta_n_na"], 1)
        self.assertEqual(s["delta_direction"], "not_calculable")
        s = closeout.five_stats([-.1, .2, 0, .1, -.2], "delta")
        self.assertEqual(s["delta_direction"], "mixed")
        self.assertAlmostEqual(s["delta_std"], np.std([-.1, .2, 0, .1, -.2], ddof=1))

    def test_five_prediction_ids_are_not_row_positions(self):
        closeout.require_five(pd.DataFrame({"fold": [5, 2, 4, 1, 3]}))
        for ids in ([1, 2, 3, 4], [1, 2, 3, 4, 4]):
            with self.assertRaises(ValueError):
                closeout.require_five(pd.DataFrame({"fold": ids}))

    def test_six_way_composition_keys(self):
        d = pd.read_csv(ROOT / "results/summary/sec33_directional_confusion_closeout/source_composition_direction_contrast.csv")
        self.assertEqual(len(d), 216)
        self.assertEqual(set(zip(d.true_class, d.predicted_class)), {
            ("corn", "other"), ("corn", "soybean"), ("other", "corn"),
            ("other", "soybean"), ("soybean", "corn"), ("soybean", "other")})


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""In-memory tests for endpoint delta pairing and soybean leakage decomposition."""
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import close_sec33_round3_distance as m


def fixture():
    w, c, s = [], [], []
    for band, baseline, rates in (
        (m.NEAR, 0.4, [0.45, 0.55, 0.65, 0.4, 0.2]),
        (m.FAR, 0.1, [0.3, 0.2, 0.4, 0.1, 0.05]),
    ):
        common = dict(model="convgru", target="il_2023", population="soybean", band=band)
        w.append(common | dict(pixels=100, error_rate=baseline, status="defined"))
        for fold, rate in enumerate(rates, 1):
            c.append(common | dict(source="iw2_2023", fold=fold, pixels=100,
                                   error_rate=rate, status="defined"))
        s.append(common | dict(source="iw2_2023", delta_error_rate=np.mean(rates) - baseline))
    return pd.DataFrame(w), pd.DataFrame(c), pd.DataFrame(s)


class CloseoutTests(unittest.TestCase):
    def test_pairing_is_by_identity_not_row_order(self):
        w, c, s = fixture()
        actual, summary = m.pair_deltas(w.iloc[::-1], c.sample(frac=1, random_state=17), s)
        np.testing.assert_allclose(actual.d_gt6_minus_near, [.15, -.05, .05, 0, .15], atol=1e-15)
        self.assertEqual(summary.iloc[0].five_direction, "mixed")
        self.assertEqual(summary.iloc[0].n_gt6_higher, 3)
        self.assertEqual(summary.iloc[0].n_near_higher, 1)
        self.assertEqual(summary.iloc[0].n_equal, 1)
        self.assertLess(actual.iloc[-1].gt6_delta_e, 0)

    def test_relative_comparison_differs_from_absolute_rates(self):
        w, c, s = fixture()
        pair, _ = m.pair_deltas(w, c, s)
        first = pair.iloc[0]
        self.assertLess(first.gt6_cross_e - first.near_cross_e, 0)
        self.assertGreater(first.d_gt6_minus_near, 0)

    def test_missing_prediction_rejected(self):
        w, c, s = fixture()
        with self.assertRaisesRegex(ValueError, "incomplete five"):
            m.pair_deltas(w, c.iloc[:-1], s)

    def test_wrong_prediction_id_or_duplicate_rejected(self):
        w, c, s = fixture()
        c.loc[9, "fold"] = 6
        with self.assertRaisesRegex(ValueError, "fold identifiers"):
            m.pair_deltas(w, c, s)
        w, c, s = fixture()
        with self.assertRaisesRegex(ValueError, "duplicate identity"):
            m.pair_deltas(w, pd.concat([c, c.iloc[[0]]]), s)

    def test_reference_support_mismatch_rejected(self):
        w, c, s = fixture()
        c.loc[0, "pixels"] = 99
        with self.assertRaisesRegex(ValueError, "support mismatch"):
            m.pair_deltas(w, c, s)

    def test_na_is_not_equal_and_does_not_reduce_five(self):
        w, c, s = fixture()
        c.loc[9, "error_rate"] = np.nan
        c.loc[9, "status"] = "undefined_zero_support"
        s.loc[s.band.eq(m.FAR), "delta_error_rate"] = np.nan
        pair, summary = m.pair_deltas(w, c, s)
        row = summary.iloc[0]
        self.assertEqual(pair.iloc[-1].direction, "not_calculable")
        self.assertEqual(row.n_predictions, 5)
        self.assertEqual(row.n_defined, 4)
        self.assertEqual(row.n_not_calculable, 1)
        self.assertEqual(row.n_equal, 1)
        for field in ("d_mean", "d_std", "d_min", "d_max", "gt6_delta_e_mean"):
            self.assertTrue(np.isnan(row[field]))

    def test_zero_support_and_negative_component(self):
        empty = np.zeros((3, 3), dtype=np.int64)
        z = m.soybean_components(empty, empty)
        self.assertTrue(np.isnan(z["component_sum"]))
        self.assertEqual(z["status"], "undefined_zero_support")
        within = np.array([[8, 1, 1], [2, 5, 3], [2, 3, 5]])
        cross = np.array([[8, 1, 1], [2, 5, 3], [4, 0, 6]])
        parts = m.soybean_components(within, cross)
        self.assertAlmostEqual(parts["delta_to_corn_rate"], .2)
        self.assertAlmostEqual(parts["delta_to_other_rate"], -.3)
        self.assertAlmostEqual(parts["component_sum"], -.1)
        self.assertAlmostEqual(parts["component_sum"], m.base.metrics(cross, "soybean")["error_rate"]
                               - m.base.metrics(within, "soybean")["error_rate"])

    def test_direction_uses_unrounded_value(self):
        self.assertEqual(m.direction(1e-17), "gt6_higher")
        self.assertEqual(m.direction(-1e-17), "near_higher")
        self.assertEqual(m.direction(0), "equal")
        self.assertEqual(m.direction(np.nan), "not_calculable")

    def test_overview_rejects_wrong_source_or_wrong_value(self):
        overview, sources = [], []
        for model in m.base.MODELS:
            for target in m.base.SITES:
                for pop in m.base.POPULATIONS:
                    for band in m.base.BANDS:
                        key = dict(model=model, target=target, population=pop, band=band)
                        overview.append(key | dict(delta_error_rate_three_source_mean=.2))
                        for i, source in enumerate(s for s in m.base.SITES if s != target):
                            sources.append(key | dict(source=source, delta_error_rate=(i + 1) / 10))
        o, s = pd.DataFrame(overview), pd.DataFrame(sources)
        m.validate_overview(o, s)
        bad = o.copy()
        bad.loc[0, "delta_error_rate_three_source_mean"] = .3
        with self.assertRaisesRegex(ValueError, "mean mismatch"):
            m.validate_overview(bad, s)
        s.loc[0, "source"] = s.loc[0, "target"]
        with self.assertRaisesRegex(ValueError, "source identity"):
            m.validate_overview(o, s)


if __name__ == "__main__":
    unittest.main()

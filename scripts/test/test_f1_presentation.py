"""Read-only checks for the generated two-decimal F1 presentation."""
from pathlib import Path
import re
import sys
import unittest

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_core_tables import generate_table2_cross_site_f1_paths
from plot_degradation_heatmap import PANELS, prepare_heatmap_data


class F1PresentationTests(unittest.TestCase):
    def test_table_csv_and_latex_use_raw_scale_two_decimals(self):
        expected = generate_table2_cross_site_f1_paths()
        actual = pd.read_csv(ROOT / 'tables/table2_cross_site_f1_12paths.csv', dtype=str)
        self.assertEqual(list(actual.columns), list(expected.columns))
        self.assertFalse(any('%' in col for col in actual.columns))
        for col in actual.columns[1:]:
            self.assertEqual(actual[col].tolist(), expected[col].map(lambda value: f'{value:.2f}').tolist())
        latex = (ROOT / 'tables/table2_cross_site_f1_12paths_rows.tex').read_text(encoding='utf-8')
        numbers = re.findall(r'(?<![\d.])\d\.\d{2}(?!\d)', latex)
        self.assertEqual(numbers, [f'{value:.2f}' for value in expected.iloc[:, 1:].to_numpy().ravel()])
        self.assertEqual(len(numbers), 78)

    def test_heatmap_uses_full_precision_difference(self):
        df = pd.read_csv(ROOT / 'results/summary/f1_raw_scale/crop_f1_difference_36paths.csv',
                         float_precision='round_trip')
        zeros_after_rounding = 0
        for crop, model, _ in PANELS:
            values = prepare_heatmap_data(df, model, crop).to_numpy()
            self.assertTrue(np.isnan(np.diag(values)).all())
            actual = values[np.isfinite(values)]
            expected = df[df.model == model][f'{crop}_f1_difference'].to_numpy()
            np.testing.assert_array_equal(np.sort(actual), np.sort(expected))
            self.assertTrue((actual > 0).all())
            zeros_after_rounding += sum(f'{value:.2f}' == '0.00' for value in actual)
        self.assertEqual(zeros_after_rounding, 1)

    def test_body_has_no_f1_percent_or_relative_dr(self):
        methods = (ROOT / 'sections/03_methods.tex').read_text(encoding='utf-8')
        results = (ROOT / 'sections/04_results.tex').read_text(encoding='utf-8')
        text = '\n'.join(line for line in (methods + results).splitlines() if not line.lstrip().startswith('%'))
        self.assertNotIn('mathrm{DR}', text)
        self.assertNotIn('泛化退化比例', text)
        self.assertNotIn('个百分点', text)
        self.assertNotIn('F1/\\%', text)
        self.assertIn('0.00不表示差值严格为零', text)
        self.assertIn('\\Delta F1_{\\text{玉米}}', methods)
        self.assertIn('\\overline{F1}_{\\text{跨站玉米}}', methods)


if __name__ == '__main__':
    unittest.main()

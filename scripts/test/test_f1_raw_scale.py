"""In-memory tests for raw-scale F1; never create or delete output files."""

from io import StringIO
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from calculate_f1_raw_scale import (
    CM_COLUMNS, CROSS_RAW, FULL_SITE_PIXELS, MODELS, PROCESSED, SITES, SUMMARY,
    TABLE_PATHS, WITHIN_RAW, build_tables, metrics_from_cm,
)


def synthetic_raw_frames():
    """Synthetic CM inputs exist only in memory, never in result directories."""
    unit = FULL_SITE_PIXELS // 100
    within, cross = [], []
    for model_index, model in enumerate(MODELS):
        for site_index, target in enumerate(SITES):
            matrices = []
            for fold in range(1, 6):
                corn_error = (1 + model_index + 2 * site_index + fold) * unit // 8
                soybean_error = (2 + model_index + site_index + fold) * unit // 8
                cm = np.array([[8 * unit - corn_error, corn_error, 0],
                               [0, 5 * unit, 0],
                               [0, soybean_error, 7 * unit - soybean_error]], dtype=np.int64)
                matrices.append(cm)
                within.append(dict(model=model, target=target, result_type='fold', fold=fold,
                                   **dict(zip(CM_COLUMNS, cm.ravel()))))
            pooled = np.sum(matrices, axis=0)
            within.append(dict(model=model, target=target, result_type='oof_pooled', fold=np.nan,
                               **dict(zip(CM_COLUMNS, pooled.ravel()))))
        for source_index, source in enumerate(SITES):
            for target in SITES:
                if source == target:
                    continue
                for fold in range(1, 6):
                    corn_error = (12 + model_index + source_index + fold) * unit
                    soybean_error = (10 + 2 * model_index + source_index + fold) * unit
                    cm = np.array([[40 * unit - corn_error, corn_error, 0],
                                   [0, 25 * unit, 0],
                                   [0, soybean_error, 35 * unit - soybean_error]], dtype=np.int64)
                    cross.append(dict(model=model, source=source, target=target, fold=fold,
                                      **dict(zip(CM_COLUMNS, cm.ravel()))))
    return pd.DataFrame(within), pd.DataFrame(cross)


class RawScaleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.within, cls.cross = synthetic_raw_frames()
        cls.tables = build_tables(cls.within, cls.cross)

    def test_output_shapes_and_exact_cm_preservation(self):
        self.assertEqual(list(self.tables), list(TABLE_PATHS))
        self.assertEqual([len(table) for table in self.tables.values()], [72, 180, 12, 12, 180, 36, 36])
        for input_frame, name, keys in [
            (self.within, 'within_site_metrics', ['model', 'target', 'result_type', 'fold']),
            (self.cross, 'cross_site_metrics', ['model', 'source', 'target', 'fold']),
        ]:
            actual = self.tables[f'{PROCESSED}/{name}.csv']
            pd.testing.assert_frame_equal(
                input_frame.sort_values(keys)[CM_COLUMNS].reset_index(drop=True),
                actual.sort_values(keys)[CM_COLUMNS].reset_index(drop=True),
            )
            self.assertTrue(all(np.issubdtype(actual[column].dtype, np.integer) for column in CM_COLUMNS))
            self.assertTrue(set(['corn_f1', 'soybean_f1', 'other_f1', 'oa']).issubset(actual.columns))

    def test_category_order_and_f1_formula(self):
        result = metrics_from_cm([[8, 2, 0], [4, 5, 1], [0, 3, 6]]).iloc[0]
        self.assertAlmostEqual(result.corn_f1, 16 / 22)
        self.assertAlmostEqual(result.soybean_f1, 12 / 16)
        self.assertAlmostEqual(result.other_f1, 10 / 20)
        self.assertAlmostEqual(result.oa, 19 / 29)

    def test_absent_class_and_empty_cm(self):
        result = metrics_from_cm([[0, 0, 0], [0, 8, 0], [0, 0, 0]]).iloc[0]
        self.assertEqual(result.corn_f1, 0.0)
        self.assertEqual(result.soybean_f1, 0.0)
        self.assertEqual(result.other_f1, 1.0)
        with self.assertRaisesRegex(ValueError, 'positive'):
            metrics_from_cm(np.zeros((3, 3), dtype=int))

    def test_pooled_is_not_mean_of_fold_f1(self):
        summary = self.tables[f'{SUMMARY}/within_site_crop_f1.csv'].set_index(['model', 'target'])
        stats = self.tables[f'{SUMMARY}/within_site_crop_f1_fold_stats.csv'].set_index(['model', 'target'])
        key = ('convgru', 'iw_2023')
        source = self.within[(self.within.model == key[0]) & (self.within.target == key[1])
                             & (self.within.result_type == 'fold')]
        expected = metrics_from_cm(source[CM_COLUMNS].sum().to_numpy()).iloc[0].corn_f1
        self.assertEqual(summary.loc[key, 'corn_f1'], expected)
        self.assertNotAlmostEqual(summary.loc[key, 'corn_f1'], stats.loc[key, 'corn_f1_mean'], places=10)

    def test_target_model_baseline_no_percent_scaling(self):
        baseline = self.tables[f'{SUMMARY}/within_site_crop_f1.csv'].set_index(['model', 'target'])
        cross = self.tables[f'{SUMMARY}/cross_site_crop_f1_summary.csv'].set_index(['model', 'source', 'target'])
        differences = self.tables[f'{SUMMARY}/crop_f1_difference_36paths.csv'].set_index(['model', 'source', 'target'])
        key = ('unet3d', 'ida_2023', 'iw2_2023')
        for crop in ('corn', 'soybean'):
            b = baseline.loc[(key[0], key[2]), f'{crop}_f1']
            mean = cross.loc[key, f'{crop}_f1_mean']
            result = differences.loc[key, f'{crop}_f1_difference']
            self.assertEqual(result, b - mean)
            self.assertNotEqual(result, 100 * (b - mean))
            self.assertNotEqual(result, (b - mean) / b)
            self.assertNotEqual(result, baseline.loc[(key[0], key[1]), f'{crop}_f1'] - mean)
            self.assertEqual(differences.loc[key, f'within_{crop}_f1'], b)
        self.assertFalse(any(column.endswith(('_pp', '_pct')) for column in differences.columns))

    def test_sample_standard_deviation_and_five_prediction_mean(self):
        per_fold = self.tables[f'{SUMMARY}/cross_site_crop_f1_per_fold.csv']
        summary = self.tables[f'{SUMMARY}/cross_site_crop_f1_summary.csv'].set_index(['model', 'source', 'target'])
        key = ('utae', 'iw_2023', 'il_2023')
        values = per_fold[(per_fold.model == key[0]) & (per_fold.source == key[1])
                          & (per_fold.target == key[2])].corn_f1.to_numpy()
        self.assertAlmostEqual(summary.loc[key, 'corn_f1_mean'], np.mean(values), places=15)
        self.assertAlmostEqual(summary.loc[key, 'corn_f1_std'], np.std(values, ddof=1), places=15)
        self.assertNotAlmostEqual(summary.loc[key, 'corn_f1_std'], np.std(values, ddof=0), places=10)
        within_metrics = self.tables[f'{PROCESSED}/within_site_metrics.csv']
        values = within_metrics[(within_metrics.model == key[0]) & (within_metrics.target == key[2])
                                 & (within_metrics.result_type == 'fold')].soybean_f1.to_numpy()
        within_stats = self.tables[f'{SUMMARY}/within_site_crop_f1_fold_stats.csv'].set_index(['model', 'target'])
        self.assertAlmostEqual(within_stats.loc[(key[0], key[2]), 'soybean_f1_std'], np.std(values, ddof=1), places=15)

    def test_round_trip_preserves_all_binary64_values_in_memory(self):
        for name, table in self.tables.items():
            buffer = StringIO()
            table.to_csv(buffer, index=False, float_format='%.17g')
            buffer.seek(0)
            recovered = pd.read_csv(buffer, float_precision='round_trip')
            for column in table.select_dtypes(include=[np.number]):
                np.testing.assert_equal(table[column].to_numpy(dtype=float), recovered[column].to_numpy(dtype=float),
                                        err_msg=f'{name}: {column}')

    def test_inputs_not_mutated_and_row_order_irrelevant(self):
        within, cross = self.within.copy(deep=True), self.cross.copy(deep=True)
        reordered = build_tables(within.iloc[::-1], cross.iloc[::-1])
        pd.testing.assert_frame_equal(within, self.within)
        pd.testing.assert_frame_equal(cross, self.cross)
        for name in self.tables:
            pd.testing.assert_frame_equal(self.tables[name], reordered[name])

    def test_incomplete_key_sets_are_rejected(self):
        with self.assertRaisesRegex(ValueError, '180 rows'):
            build_tables(self.within, self.cross.iloc[:-1])
        invalid = self.cross.copy()
        invalid.loc[invalid.source == 'iw_2023', 'source'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'key set'):
            build_tables(self.within, invalid)
        invalid = self.cross.copy()
        invalid.loc[0, 'source'] = invalid.loc[0, 'target']
        with self.assertRaisesRegex(ValueError, 'key set'):
            build_tables(self.within, invalid)

    def test_duplicate_or_invalid_fold_ids_are_rejected(self):
        for value in [2, 1.5, 0, np.nan]:
            with self.subTest(fold=value):
                invalid = self.cross.copy().astype({'fold': float})
                invalid.loc[0, 'fold'] = value
                with self.assertRaisesRegex(ValueError, 'fold'):
                    build_tables(self.within, invalid)

    def test_noninteger_negative_and_nonfinite_cm_are_rejected(self):
        for value in [0.5, -1, np.nan, np.inf]:
            with self.subTest(count=value):
                invalid = self.cross.copy().astype({'cm_00': float})
                invalid.loc[0, 'cm_00'] = value
                with self.assertRaisesRegex(ValueError, 'CM'):
                    build_tables(self.within, invalid)

    def test_pooled_mismatch_and_wrong_pixel_count_are_rejected(self):
        invalid = self.within.copy()
        pooled_index = invalid.index[invalid.result_type == 'oof_pooled'][0]
        invalid.loc[pooled_index, 'cm_00'] += 1
        with self.assertRaisesRegex(ValueError, 'elementwise fold sum'):
            build_tables(invalid, self.cross)
        invalid = self.cross.copy()
        invalid.loc[0, 'cm_00'] += 1
        with self.assertRaisesRegex(ValueError, '6553600'):
            build_tables(self.within, invalid)

    def test_target_supports_are_checked_not_just_total(self):
        invalid = self.cross.copy()
        invalid.loc[0, 'cm_00'] -= 1
        invalid.loc[0, 'cm_11'] += 1
        with self.assertRaisesRegex(ValueError, 'row supports'):
            build_tables(self.within, invalid)

    def test_negative_difference_is_preserved(self):
        improved = self.cross.copy()
        for i in range(5):
            source_cm = improved.loc[i, CM_COLUMNS].to_numpy(dtype=np.int64).reshape(3, 3)
            improved.loc[i, CM_COLUMNS] = np.diag(source_cm.sum(axis=1)).ravel()
        tables = build_tables(self.within, improved)
        differences = tables[f'{SUMMARY}/crop_f1_difference_36paths.csv']
        row = differences[(differences.model == improved.loc[0, 'model'])
                          & (differences.source == improved.loc[0, 'source'])
                          & (differences.target == improved.loc[0, 'target'])].iloc[0]
        self.assertLess(row.corn_f1_difference, 0)
        self.assertEqual(row.corn_f1_difference, row.within_corn_f1 - 1.0)


class RepositoryRawTests(unittest.TestCase):
    def test_real_repository_raw_in_memory(self):
        root = Path(__file__).resolve().parents[2]
        paths = [root / WITHIN_RAW, root / CROSS_RAW]
        if not all(path.is_file() for path in paths):
            self.skipTest('Repository raw CMs not present; real-data check not run')
        tables = build_tables(*(pd.read_csv(path, float_precision='round_trip') for path in paths))
        self.assertEqual([len(table) for table in tables.values()], [72, 180, 12, 12, 180, 36, 36])
        for name in ['within_site_crop_f1', 'cross_site_crop_f1_per_fold', 'cross_site_crop_f1_summary']:
            frame = tables[f'{SUMMARY}/{name}.csv']
            metrics = [column for column in frame if '_f1' in column]
            self.assertTrue(np.isfinite(frame[metrics].to_numpy()).all())
            self.assertTrue(((frame[metrics] >= 0) & (frame[metrics] <= 1)).all().all())
        difference = tables[f'{SUMMARY}/crop_f1_difference_36paths.csv']
        for crop in ['corn', 'soybean']:
            np.testing.assert_array_equal(difference[f'{crop}_f1_difference'],
                                          difference[f'within_{crop}_f1'] - difference[f'cross_{crop}_f1_mean'])
            self.assertTrue((difference[f'{crop}_f1_difference'] > 0).all())


if __name__ == '__main__':
    unittest.main()

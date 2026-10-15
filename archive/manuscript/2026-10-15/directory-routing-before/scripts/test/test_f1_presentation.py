"""Read-only regression checks for percentage/percentage-point presentation."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import re
import sys
import unittest

import numpy as np
import pandas as pd
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_core_tables import generate_table2_cross_site_f1_paths, f1_text_values
from plot_degradation_heatmap import PANELS, prepare_heatmap_data, shared_color_scale
from f1_display import f1_number, f1_mean_sd

BASE = ROOT / 'results/summary/f1_raw_scale'
SITES = {'A':'iw_2023','B':'iw2_2023','C':'ida_2023','D':'il_2023'}
MODELS = {'ConvGRU':'convgru','3D U-Net':'unet3d','U-TAE':'utae'}


def read(name):
    return pd.read_csv(BASE / name, float_precision='round_trip')


class F1PresentationTests(unittest.TestCase):
    def test_percentage_sd_signed_difference_and_rounding(self):
        self.assertEqual(f1_number(0.920283), '92.03')
        self.assertEqual(f1_mean_sd(0.8957, 0.0008), '89.57 ± 0.08')
        self.assertEqual(f1_number(0.0044147), '0.44')
        self.assertEqual(f1_number(-0.0044147), '-0.44')
        self.assertEqual(f1_number(-0.000001), '0.00')
        self.assertEqual(f1_number(np.nan), 'NA')
        self.assertEqual(shared_color_scale([-0.004, 7.39]), (-8.0, 8.0, 'RdBu_r'))

    def test_table_means_only_from_full_precision(self):
        actual = pd.read_csv(ROOT / 'tables/table2_cross_site_f1_12paths.csv', dtype=str)
        stats = read('cross_site_crop_f1_summary.csv').set_index(['model','source','target'])
        expected_cells = []
        for _, row in actual.iterrows():
            for label, model in MODELS.items():
                for name, crop in [('玉米','corn'),('大豆','soybean')]:
                    if row['迁移路径'] == '平均':
                        mean = stats.loc[model, f'{crop}_f1_mean'].mean()
                        expected = f'{100*mean:.2f}'
                    else:
                        src,tgt=row['迁移路径'].split('→')
                        ref=stats.loc[(model,SITES[src],SITES[tgt])]
                        expected=f'{100*ref[f"{crop}_f1_mean"]:.2f}'
                    self.assertEqual(row[f'{label}{name}F1（%）'],expected)
                    expected_cells.append(expected)
        latex=(ROOT/'tables/table2_cross_site_f1_12paths_rows.tex').read_text(encoding='utf-8')
        cells=[c.strip() for line in latex.splitlines() if '&' in line for c in line.removesuffix(r'\\').split('&')[1:]]
        self.assertEqual(cells,expected_cells)
        self.assertEqual(len(cells),78)
        self.assertTrue(all(re.fullmatch(r'\d+\.\d{2}', c) for c in cells))
        # The table's calculation interface itself still returns raw full precision.
        raw=generate_table2_cross_site_f1_paths()
        self.assertTrue((raw.iloc[:,1:].to_numpy()<1).all())

    def test_convgru_soybean_B_to_A(self):
        df=read('crop_f1_difference_36paths.csv')
        row=df[(df.model=='convgru')&(df.source=='iw2_2023')&(df.target=='iw_2023')].iloc[0]
        self.assertEqual(f1_number(row.within_soybean_f1),'92.03')
        self.assertEqual(f1_number(row.cross_soybean_f1_mean),'91.59')
        self.assertEqual(f1_number(row.soybean_f1_difference),'0.44')
        self.assertAlmostEqual(row.within_soybean_f1-row.cross_soybean_f1_mean,row.soybean_f1_difference,places=15)
        runs=read('cross_site_crop_f1_per_fold.csv')
        x=runs[(runs.model=='convgru')&(runs.source=='iw2_2023')&(runs.target=='iw_2023')].soybean_f1
        self.assertAlmostEqual(x.std(ddof=1),row.cross_soybean_f1_std,places=14)
        self.assertEqual(f1_number(row.cross_soybean_f1_std),'0.13')

    def test_all_heatmap_values_and_one_common_scale(self):
        df=read('crop_f1_difference_36paths.csv')
        all_values=[]
        for crop,model,tag in PANELS:
            matrix=prepare_heatmap_data(df,model,crop).to_numpy()
            self.assertTrue(np.isnan(np.diag(matrix)).all())
            actual=matrix[np.isfinite(matrix)]
            expected=df[df.model==model][f'{crop}_f1_difference'].to_numpy()*100
            np.testing.assert_array_equal(np.sort(actual),np.sort(expected))
            all_values.extend(actual)
            # Actual exported PDF annotations: no missed or double scaling.
            doc=fitz.open(ROOT/f'figures/results/fig_degradation_heatmap_{tag}.pdf')
            words=doc[0].get_text('words')
            numbers=[w[4] for w in words if re.fullmatch(r'-?\d+\.\d{2}',w[4])]
            self.assertEqual(Counter(numbers),Counter(f'{v:.2f}' for v in expected))
            self.assertEqual(len(numbers),12)
            rects=[fitz.Rect(w[:4]) for w in words if re.fullmatch(r'-?\d+\.\d{2}',w[4])]
            self.assertTrue(all(doc[0].rect.contains(r) for r in rects))
            self.assertFalse(any(a.intersects(b) for i,a in enumerate(rects) for b in rects[i+1:]))
            doc.close()
        self.assertEqual(shared_color_scale(all_values),(0.0,8.0,'YlOrRd'))
        with fitz.open(ROOT/'figures/results/fig_degradation_heatmap_cbar.pdf') as doc:
            self.assertEqual(re.findall(r'\d+\.\d{2}',doc[0].get_text()),['0.00','2.00','4.00','6.00','8.00'])

    def test_within_exported_values_and_unit(self):
        df=read('within_site_crop_f1.csv')
        for crop,tag in [('corn','a'),('soybean','b')]:
            with fitz.open(ROOT/f'figures/results/fig_within_site_f1_{tag}.pdf') as doc:
                text=doc[0].get_text()
                numbers=Counter(re.findall(r'\d+\.\d{2}',text))
                labels=Counter(f'{v*100:.2f}' for v in df[f'{crop}_f1'])
                labels.update(f'{v:.2f}' for v in np.arange(88,98.1,2))
                self.assertEqual(numbers,labels)
                self.assertIn('F1',text)
                self.assertIn('%',text)

    def test_text_values_and_body_units(self):
        macros=(ROOT/'tables/f1_text_values.tex').read_text(encoding='utf-8')
        actual=dict(re.findall(r'\\newcommand\{\\(\w+)\}\{(-?\d+\.\d{2})\}',macros))
        self.assertEqual(actual,{k:f1_number(v) for k,v in f1_text_values().items()})
        methods=(ROOT/'sections/03_methods.tex').read_text(encoding='utf-8')
        results=(ROOT/'sections/04_results.tex').read_text(encoding='utf-8')
        self.assertIn('F1下降（百分点）',results)
        self.assertIn('5次F1的算术平均',results)
        self.assertNotIn('均值±标准差',results)
        self.assertIn('F1（\\%）',results)
        self.assertNotIn('采用原始刻度',methods)
        self.assertNotIn('mathrm{DR}',methods+results)
        # Every generated numeric command used in the prose exists.
        used=set(re.findall(r'\\(F[A-Z][A-Za-z]+)',results))
        self.assertTrue(used<=actual.keys())
        self.assertIn('差值不除以站内基准',methods)

    def test_scientific_data_and_backups_unchanged(self):
        manifest=json.loads((ROOT/'output/archive/2026-10-13/f1-display-before/manifest.json').read_text(encoding='utf-8'))
        for name,expected in manifest['unchanged_data'].items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),expected,name)
        for entry in manifest['copies']:
            self.assertEqual(hashlib.sha256((ROOT/entry['backup']).read_bytes()).hexdigest(),entry['sha256'])


if __name__ == '__main__':
    unittest.main()

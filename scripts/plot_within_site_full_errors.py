"""Draw native full-site crop-reference correctness maps; keep local assets intact."""
from io import BytesIO
from pathlib import Path
import json

import numpy as np
import pandas as pd
from PIL import Image
import pymupdf

from plot_within_site_errors import COLORS, INDEX, MODELS, SITES, digest, error_rgb, path_key, read_site, write_new

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/summary/sec31_joint_boundary'
FIG = ROOT / 'figures/results'
PANEL_CM = 5.2


def main():
    paths = [FIG / f'fig_within_site_full_errors_{site}_{model}.{ext}'
             for site in SITES for model in MODELS for ext in ('pdf', 'png')]
    extra = [OUT / n for n in ['figure_manifest.json', 'full_site_grid_checks.csv', 'full_site_pixel_checks.csv']]
    if any(p.exists() for p in paths + extra):
        raise FileExistsError('Preserve existing full-site outputs before regeneration')
    index = pd.read_csv(INDEX)
    index = index[index.kind.eq('within')]
    metrics = pd.read_csv(OUT / 'within_site_position_metrics.csv')
    inputs, outputs, grids, checks = {}, [], [], []
    inputs[path_key(INDEX)] = digest(INDEX)
    for site, target in SITES.items():
        arrays, predictions, sources, grid_rows = read_site(target, index)
        grids.extend(grid_rows)
        for p in sources:
            inputs[path_key(p)] = digest(p)
        label = arrays['label']
        assert label.shape == (2560, 2560) and np.isin(label, [0, 1, 2]).all()
        crop = np.isin(label, [0, 2])
        for model in MODELS:
            rgb = error_rgb(label, predictions[model])
            for name, color, expected in [
                ('error', COLORS['error'], int((crop & (label != predictions[model])).sum())),
                ('correct', COLORS['correct'], int((crop & (label == predictions[model])).sum())),
                ('other', COLORS['other'], int((~crop).sum()))]:
                actual = int(np.all(rgb == list(bytes.fromhex(color[1:])), axis=2).sum())
                assert actual == expected
                checks.append(dict(site=site, model=model, check='color_' + name,
                                   expected_pixels=expected, actual_pixels=actual, status='Verified'))
            for crop_name, code in [('corn', 0), ('soybean', 2)]:
                for position, spatial in [('boundary', arrays['bands'] == 0), ('interior', arrays['bands'] > 0)]:
                    mask = (label == code) & spatial
                    n = int(mask.sum()); fn = int((mask & (label != predictions[model])).sum())
                    row = metrics[metrics.target.eq(target) & metrics.model.eq(model) &
                                  metrics.crop.eq(crop_name) & metrics.position.eq(position)].iloc[0]
                    assert n == row.reference_pixels and fn == row.fn
                    checks.append(dict(site=site, model=model, check=crop_name + '_' + position,
                        expected_pixels=int(row.fn), actual_pixels=fn, reference_pixels=n, status='Verified'))
            stem = FIG / f'fig_within_site_full_errors_{site}_{model}'
            stream = BytesIO()
            Image.fromarray(rgb).save(stream, format='PNG')
            png = stream.getvalue()
            with stem.with_suffix('.png').open('xb') as f:
                f.write(png)
            doc = pymupdf.open()
            side = PANEL_CM / 2.54 * 72
            page = doc.new_page(width=side, height=side)
            xref = page.insert_image(page.rect, stream=png)
            doc.xref_set_key(xref, 'Interpolate', 'false')
            doc.set_metadata(dict(title=f'{site} {model}: full-site crop-reference errors',
                                 subject='Native 2560x2560; blue correct crops, red omitted crops, grey reference other'))
            with stem.with_suffix('.pdf').open('xb') as f:
                f.write(doc.tobytes(deflate=True))
            doc.close()
            # Reopen and verify actual PDF pixels, dimensions and opacity.
            with pymupdf.open(stem.with_suffix('.pdf')) as check_doc:
                im = check_doc[0].get_images()
                assert len(im) == 1 and im[0][2:4] == (2560, 2560) and im[0][1] == 0
                pix = pymupdf.Pixmap(check_doc, im[0][0])
                assert pix.n == 3 and pix.samples == rgb.tobytes()
                assert abs(check_doc[0].rect.width - side) < .001
                assert abs(check_doc[0].rect.height - side) < .001
                assert not check_doc[0].get_drawings()
            outputs.extend([stem.with_suffix('.pdf'), stem.with_suffix('.png')])
        print(site, '3 native full-site panels and reference/FN counts verified', flush=True)
    for data, name in [(grids, 'full_site_grid_checks.csv'), (checks, 'full_site_pixel_checks.csv')]:
        p = OUT / name
        write_new(p, pd.DataFrame(data).to_csv(index=False, lineterminator='\n'))
        outputs.append(p)
    write_new(OUT / 'figure_manifest.json', json.dumps(dict(date='2026-10-17', verification='Verified',
        colors={k: COLORS[k] for k in ['correct', 'error', 'other']}, panel_cm=[PANEL_CM, PANEL_CM],
        native_pixels=[2560, 2560], interpolation=False, alpha=1, boundary_lines=False,
        script_sha256=digest(Path(__file__)), reused_reader_sha256=digest(ROOT / 'scripts/plot_within_site_errors.py'),
        input_sha256=inputs, output_sha256={path_key(p): digest(p) for p in outputs}), indent=2) + '\n')


if __name__ == '__main__':
    main()

"""Independent raw-raster checks for section 3.1 joint-position evidence."""
from pathlib import Path
import hashlib
import json
import sys
import unittest

import numpy as np
import pandas as pd
from PIL import Image
import pymupdf

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from analyze_sec31_joint_boundary import A_EDGES, S_EDGES, bin_index, compare_models, ratio
from plot_within_site_errors import INDEX, MODELS, REF, SITES, boundary_mask, read_site

OUT = ROOT / 'results/summary/sec31_joint_boundary'


class EdgeCases(unittest.TestCase):
    def test_bin_endpoints(self):
        np.testing.assert_array_equal(bin_index([0, 9.9999, 10, 50, 100, 200, 500, 1000], A_EDGES),
                                      [0, 0, 1, 2, 3, 4, 5, 5])
        np.testing.assert_array_equal(bin_index([1, 1.4999, 1.5, 2, 3, 9], S_EDGES), [0, 0, 1, 2, 3, 3])

    def test_signed_and_zero_denominators(self):
        rows = []
        for model, counts in [('convgru', [4, 6, 0]), ('utae', [0, 8, 0])]:
            for i, fn in enumerate(counts):
                rows.append(dict(target='x', crop='corn', group=str(i), position='interior',
                    model=model, reference_pixels=10 if i < 2 else 0, fn=fn,
                    whole_fn=sum(counts), whole_crop_pixels=20,
                    omission_rate=fn/10 if i < 2 else np.nan,
                    group_reference_pixels=10 if i < 2 else 0, patch_count=1 if i < 2 else 0, site='X'))
        m = pd.DataFrame(rows)
        x = compare_models(m, 'convgru', 'utae')
        np.testing.assert_array_equal(x.net_fewer_pixels, [4, -2, 0])
        np.testing.assert_allclose(x.net_reduction_share, [2, -1, 0])
        np.testing.assert_allclose(x.whole_rate_contribution_pp, [20, -10, 0])
        self.assertTrue(np.isnan(x.rate_reduction_pp.iloc[2]))
        m.loc[m.model.eq('utae'), 'whole_fn'] = 10
        self.assertTrue(compare_models(m, 'convgru', 'utae').net_reduction_share.isna().all())
        self.assertTrue(np.isnan(ratio(0, 0)))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def artifacts(compiled=False):
    checks = []

    def check(name, condition):
        assert condition, name
        checks.append(dict(check=name, status='Verified'))

    for name, script in [('manifest.json', 'scripts/analyze_sec31_joint_boundary.py'),
                         ('figure_manifest.json', 'scripts/plot_within_site_full_errors.py'),
                         ('reading_manifest.json', 'scripts/summarize_sec31_joint_boundary.py')]:
        data = json.loads((OUT / name).read_text(encoding='utf-8'))
        check(name + '/script', sha(ROOT / script) == data['script_sha256'])
        for kind in ['input_sha256', 'output_sha256']:
            for p, h in data[kind].items():
                check(name + '/' + p, sha(ROOT / p) == h)
    support = pd.read_csv(OUT / 'reference_support.csv', float_precision='round_trip')
    metrics = pd.read_csv(OUT / 'within_position_metrics.csv', float_precision='round_trip')
    contrasts = pd.read_csv(OUT / 'model_comparisons.csv', float_precision='round_trip')
    features = pd.read_csv(REF / 'reference_patch_features.csv', float_precision='round_trip')
    check('all rows including zero support', len(support) == 192 and len(metrics) == 1152 and len(contrasts) == 1152)
    check('empty position rates are NA', metrics.loc[metrics.reference_pixels.eq(0), 'omission_rate'].isna().all())
    check('same model reference supports', metrics.groupby(['target', 'crop', 'group', 'position']).reference_pixels.nunique().eq(1).all())
    check('reference support fractions', np.allclose(support.area_share, support.reference_pixels/support.whole_crop_pixels) and
          np.allclose(support.boundary_share, support.boundary_reference_pixels/support.reference_pixels, equal_nan=True))
    check('position support fractions', np.allclose(metrics.position_area_share, metrics.reference_pixels/metrics.whole_crop_pixels) and
          np.allclose(metrics.position_share_in_group, metrics.reference_pixels/metrics.group_reference_pixels, equal_nan=True))
    evidence = pd.read_csv(OUT/'prose_evidence.csv', float_precision='round_trip', dtype={'display': str})
    tex = (ROOT/'tables/sec31_spatial_text_values.tex').read_text(encoding='utf-8')
    body = (ROOT/'sections/04_results.tex').read_text(encoding='utf-8').split('\\subsection{模型跨站分类性能与泛化退化}')[0]
    used = 0
    for r in evidence.itertuples():
        x = pd.read_csv(ROOT/r.source_file, float_precision='round_trip')
        for k,v in json.loads(r.selector).items():
            x = x[x[k].isin(v if isinstance(v,list) else [v])]
        value = float(eval(r.expression, {'__builtins__':{}}, {'x':x}))
        expected_display = f'{0 if abs(value)<.005 else value:.2f}'
        check(r.macro+'/source and rounding', np.isclose(value,r.value,rtol=0,atol=1e-12) and r.display==expected_display
              and ('\\newcommand{\\'+r.macro+'}{'+expected_display+'}') in tex)
        used += ('\\'+r.macro+'{}') in body
    check('all spatial prose macros indexed', set(__import__('re').findall(r'\\(S[A-D][A-Za-z]+)\{\}',body)) <= set(evidence.macro))
    print('Verified',used,'used spatial prose values;',len(evidence),'candidate values checked',flush=True)
    # Independent direct per-pixel bin lookup from complete-patch attributes.
    index = pd.read_csv(INDEX); index = index[index.kind.eq('within')]
    image_hashes = {}
    for site, target in SITES.items():
        arrays, predictions, _, _ = read_site(target, index)
        label, ids, bands = (arrays[k] for k in ['label', 'ids', 'bands'])
        boundary = boundary_mask(label)
        cropmask = (label == 0) | (label == 2)
        check(site + '/full-reference 30m geometry', np.array_equal(boundary[cropmask], (bands == 0)[cropmask]))
        check(site + '/all interior included', np.all((bands[cropmask] == 0) | ((bands[cropmask] >= 1) & (bands[cropmask] <= 6))))
        for crop, code in [('corn', 0), ('soybean', 2)]:
            f = features[features.target.eq(target) & features.crop.eq(crop)]
            # Count crossed lower bounds instead of reusing production bin_index.
            a = np.sum(f.AREA.to_numpy()[:, None] >= np.array([10, 50, 100, 200, 500]), axis=1)
            s = np.sum(f.SHAPE.to_numpy()[:, None] >= np.array([1.5, 2, 3]), axis=1)
            lookup = np.full(int(ids.max())+1, -1, np.int16)
            lookup[f.PID.to_numpy()] = a*4+s
            mask = label == code
            group = lookup[ids[mask]]
            check(site + '/' + crop + '/complete PID coverage', np.all(group >= 0))
            jointposition = group*2 + (~boundary[mask]).astype(np.int16)
            n = np.bincount(jointposition, minlength=48).reshape(24, 2)
            patches = np.bincount(a*4+s, minlength=24)
            r = support[support.target.eq(target) & support.crop.eq(crop)].sort_values(['area_bin_order', 'shape_bin_order'])
            check(site + '/' + crop + '/raw reference and full patch counts',
                  np.array_equal(n.sum(1), r.reference_pixels) and np.array_equal(patches, r.patch_count))
            for model in MODELS:
                wrong = predictions[model][mask] != code
                fn = np.bincount(jointposition[wrong], minlength=48).reshape(24, 2)
                m = metrics[metrics.target.eq(target) & metrics.crop.eq(crop) & metrics.model.eq(model)]
                for j, position in enumerate(['boundary', 'interior']):
                    x = m[m.position.eq(position)].sort_values(['area_bin_order', 'shape_bin_order'])
                    check(site + '/' + crop + '/' + model + '/' + position + '/raw 24-cell integers',
                          np.array_equal(x.reference_pixels, n[:, j]) and np.array_equal(x.fn, fn[:, j]))
                    expected = np.divide(fn[:, j], n[:, j], out=np.full(24, np.nan), where=n[:, j] != 0)
                    check(site + '/' + crop + '/' + model + '/' + position + '/rates',
                          np.allclose(x.omission_rate, expected, equal_nan=True) and
                          np.allclose(x.error_share, fn[:, j]/fn.sum(), equal_nan=True))
                check(site + '/' + crop + '/' + model + '/whole FN denominator', (m.whole_fn == fn.sum()).all())
        for model in MODELS:
            # Independent rendering oracle uses literals, no production renderer.
            rgb = np.empty((*label.shape, 3), np.uint8); rgb[:] = [189, 189, 189]
            rgb[cropmask & (label == predictions[model])] = [55, 126, 184]
            rgb[cropmask & (label != predictions[model])] = [215, 48, 39]
            stem = ROOT / f'figures/results/fig_within_site_full_errors_{site}_{model}'
            with Image.open(stem.with_suffix('.png')) as im:
                check(site+'/'+model+'/PNG native pixels', im.size == (2560, 2560) and np.array_equal(im, rgb))
            with pymupdf.open(stem.with_suffix('.pdf')) as doc:
                p = doc[0]; im = p.get_images()
                check(site+'/'+model+'/PDF physical and pixel size', len(im) == 1 and im[0][2:4] == (2560, 2560)
                    and abs(p.rect.width - 5.2/2.54*72) < .001 and abs(p.rect.height - 5.2/2.54*72) < .001)
                samples = pymupdf.Pixmap(doc, im[0][0]).samples
                check(site+'/'+model+'/PDF exact RGB opaque no overlay', samples == rgb.tobytes()
                      and im[0][1] == 0 and not p.get_drawings()
                      and doc.xref_get_key(im[0][0], 'Interpolate')[1] == 'false')
                image_hashes[hashlib.sha256(samples).hexdigest()] = site+'/'+model
        print(site, 'raw 24-cell counts, full-reference boundary, native 3-panel pixels Verified', flush=True)
    for keys, x in contrasts.groupby(['target', 'crop', 'baseline_model', 'comparison_model']):
        target,crop,baseline,other = keys
        keycols=['group','position']
        a=metrics[metrics.target.eq(target)&metrics.crop.eq(crop)&metrics.model.eq(baseline)].set_index(keycols).sort_index()
        b=metrics[metrics.target.eq(target)&metrics.crop.eq(crop)&metrics.model.eq(other)].set_index(keycols).sort_index()
        z=x.set_index(keycols).sort_index()
        check(str(keys)+'/paired FN and reference identity',
              np.array_equal(z.fn_baseline,a.fn) and np.array_equal(z.fn_comparison,b.fn) and
              np.array_equal(a.reference_pixels,b.reference_pixels) and np.array_equal(z.reference_pixels,a.reference_pixels))
        check(str(keys)+'/paired rate and signed net',
              np.allclose(z.rate_reduction_pp,100*(a.fn/a.reference_pixels-b.fn/b.reference_pixels),equal_nan=True) and
              np.array_equal(z.net_fewer_pixels,a.fn-b.fn) and
              np.allclose(z.whole_rate_contribution_pp,100*(a.fn-b.fn)/a.whole_crop_pixels))
        net = int(x.whole_net_fewer_pixels.iloc[0])
        check(str(keys)+'/net closure', x.net_fewer_pixels.sum() == net)
        check(str(keys)+'/signed denominators', np.allclose(x.net_reduction_share, x.net_fewer_pixels / net)
              if net else x.net_reduction_share.isna().all())
        check(str(keys)+'/additive rate closure', np.isclose(x.whole_rate_contribution_pp.sum(), 100*net/x.whole_crop_pixels.iloc[0]))
    check('negative changes retained for both comparison models',
          all((contrasts[contrasts.baseline_model.eq('convgru') & contrasts.comparison_model.eq(m)].net_fewer_pixels < 0).any()
              for m in ['unet3d', 'utae']))
    if compiled:
        found = {}
        with pymupdf.open(ROOT / 'output/main.pdf') as doc:
            for p in doc:
                for im in p.get_images(full=True):
                    if im[2:4] != (2560, 2560):
                        continue
                    h = hashlib.sha256(pymupdf.Pixmap(doc, im[0]).samples).hexdigest()
                    if h in image_hashes:
                        rects = p.get_image_rects(im[0])
                        check(image_hashes[h]+'/compiled physical size', len(rects) == 1
                              and abs(rects[0].width - 5.2/2.54*72) < .03
                              and abs(rects[0].height - 5.2/2.54*72) < .03)
                        found[image_hashes[h]] = p.number+1
        check('all 12 compiled rasters unchanged on one page', len(found) == 12 and len(set(found.values())) == 1)
        print('Compiled figure4 pixel identity and dimensions Verified; page', next(iter(found.values())), flush=True)
    print('Verified', len(checks), 'artifact checks')
    return checks


if __name__ == '__main__':
    if '--artifacts' in sys.argv:
        artifacts('--compiled' in sys.argv)
    else:
        unittest.main()

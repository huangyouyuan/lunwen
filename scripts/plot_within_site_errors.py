"""Select maximum correctness-disagreement windows and draw section 3.1 maps.

Production stages: --prepare (new derived tables), --plot (new figure assets).
Existing outputs are never silently overwritten. No training or inference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import tifffile
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/summary/sec31_spatial_examples'
FIG = ROOT / 'figures/results'
REF = ROOT / 'results/processed/sec33_reference_patch_types'
INDEX = REF / 'prediction_count_index.csv'
SUBSETS = ROOT / 'results/summary/spatial_error_conditions/reading_within_spatial_subsets.csv'
WHOLE = ROOT / 'results/summary/sec13_sec31_foundations/within_site_crop_metrics.csv'
IDENTITY = ROOT / 'results/processed/model_advantage_spatial_conditions/prediction_identity_snapshot.json'
MODELS = ('convgru', 'unet3d', 'utae')
SITES = dict(A='iw_2023', B='iw2_2023', C='ida_2023', D='il_2023')
CROPS = dict(corn=0, soybean=2)
WINDOW = 256
PIXEL_M = 30
COLORS = dict(corn='#F2C14E', soybean='#4C9F70', other='#BDBDBD',
              correct='#377EB8', error='#D73027')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def path_key(path):
    p = Path(path).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def write_new(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(content)


def save_csv(rows, name):
    path = OUT / (name + '.csv')
    write_new(path, pd.DataFrame(rows).to_csv(index=False, float_format='%.17g', lineterminator='\n'))
    return path


def read_site(target, index):
    with np.load(REF / f'reference_full_{target}.npz') as z:
        arrays = {key: z[key].copy() for key in ('label', 'ids', 'bands')}
    pred, paths, grid_rows = {}, [REF / f'reference_full_{target}.npz'], []
    assert arrays['label'].ndim == 2
    common_grid = None
    for model in MODELS:
        rows = index[(index.target == target) & (index.model == model)]
        assert len(rows) == 1 and rows.iloc[0].source == target
        pp = Path(rows.iloc[0].prediction_file)
        rp = pp.parent / 'reference.tif'
        reference = tifffile.imread(rp)
        raw_pred = tifffile.imread(pp)
        assert reference.shape == raw_pred.shape == arrays['label'].shape
        assert set(np.unique(reference)) <= {1, 2, 3, 255}
        assert set(np.unique(raw_pred)) <= {1, 2, 3}, (model, 'invalid prediction')
        normalized = np.where(reference == 255, 255, reference - 1).astype(np.uint8)
        assert np.array_equal(normalized, arrays['label']), (target, model, 'reference')
        for name, p in [('reference', rp), ('prediction', pp)]:
            with tifffile.TiffFile(p) as tf:
                tags = tf.pages[0].tags
                grid = tuple(tuple(tags[k].value) for k in ('ModelPixelScaleTag', 'ModelTiepointTag'))
                assert grid[0][:2] == (30.0, 30.0)
                if common_grid is None:
                    common_grid = grid
                assert grid == common_grid, (target, model, name, 'grid')
                keys = tags.get('GeoKeyDirectoryTag')
                crs = None
                if keys is not None:
                    values = tuple(keys.value)
                    for i in range(4, len(values), 4):
                        key, location, count, value = values[i:i + 4]
                        if key == 3072 and location == 0 and count == 1:
                            crs = int(value)
                    assert crs == 5070, (target, model, name, 'CRS')
                grid_rows.append(dict(target=target, model=model, kind=name, path=path_key(p),
                    declared_epsg=crs, matching_pixel_grid=True,
                    reference_pixel_identity=True,
                    crs_basis='declared_5070' if crs else 'matching_same_site_grid_and_reference_pixels'))
        pred[model] = raw_pred - 1
        paths.extend((rp, pp))
    return arrays, pred, paths, grid_rows


def correctness_disagreement(label, predictions):
    crop = np.isin(label, (0, 2))
    count = np.zeros(label.shape, dtype=np.uint8)
    for prediction in predictions:
        assert prediction.shape == label.shape
        count += prediction == label
    return crop & (count > 0) & (count < len(predictions))


def integral(mask):
    # A complete site has 6,553,600 pixels: signed int32 is sufficient here.
    return np.pad(np.asarray(mask, dtype=np.int32), ((1, 0), (1, 0))).cumsum(
        axis=0, dtype=np.int32).cumsum(axis=1, dtype=np.int32)


def ratio_winner(n, d, indices):
    """Exact pairwise tournament; equal fractions retain the earlier index."""
    active = np.asarray(indices)
    while active.size > 1:
        pairs = active.size // 2
        left, right = active[:2 * pairs:2], active[1:2 * pairs:2]
        winners = np.where(n[left] * d[right] >= n[right] * d[left], left, right)
        active = np.concatenate((winners, active[-1:])) if active.size % 2 else winners
    return int(active[0])


def select_window(label, disagreement, size=WINDOW):
    h, w = label.shape
    if min(h, w) < size:
        raise ValueError('Window is larger than reference')
    ints = [integral(x) for x in (np.isin(label, (0, 1, 2)), label == 0,
                                  label == 2, disagreement)]
    cols = np.arange(w - size + 1)
    best, eligible_total, ties = None, 0, 0
    for row in range(h - size + 1):
        valid_n, corn, soybean, numerator = [
            (a[row + size, cols + size] - a[row, cols + size]
             - a[row + size, cols] + a[row, cols]).astype(np.int64) for a in ints]
        eligible = (valid_n == size * size) & (corn * 10 >= size * size) & (soybean * 10 >= size * size)
        ids = np.flatnonzero(eligible)
        eligible_total += int(ids.size)
        if not ids.size:
            continue
        denominator = corn + soybean
        col = ratio_winner(numerator, denominator, ids)
        n, d = int(numerator[col]), int(denominator[col])
        relation = 1 if best is None else n * best['crop_pixels'] - best['disagreement_pixels'] * d
        if relation > 0:
            best = dict(row_start=row, col_start=col, row_stop=row + size, col_stop=col + size,
                disagreement_pixels=n, crop_pixels=d, corn_pixels=int(corn[col]),
                soybean_pixels=int(soybean[col]), other_pixels=size * size - d)
            ties = int(np.sum(eligible & (numerator * d == n * denominator)))
        elif relation == 0:
            ties += int(np.sum(eligible & (numerator * d == n * denominator)))
    if best is None:
        raise ValueError('No eligible window; do not change thresholds automatically')
    best.update(window_size=size, candidate_count=(h-size+1)*(w-size+1),
        eligible_count=eligible_total, tied_maximum_count=ties,
        disagreement_ratio=best['disagreement_pixels'] / best['crop_pixels'],
        corn_share=best['corn_pixels']/(size*size), soybean_share=best['soybean_pixels']/(size*size),
        other_share=best['other_pixels']/(size*size))
    return best


def boundary_mask(label):
    """Exact <=1-pixel centre distance to valid 4-neighbour shared edges.

    Vectorized doubled-grid equivalent of the archived distance_band_analysis
    function. Endpoints are included; artificial outer/invalid edges are not.
    """
    valid = np.isin(label, (0, 1, 2))
    h, w = label.shape
    lines = np.zeros((2*h+1, 2*w+1), dtype=bool)
    vertical = valid[:, :-1] & valid[:, 1:] & (label[:, :-1] != label[:, 1:])
    horizontal = valid[:-1, :] & valid[1:, :] & (label[:-1, :] != label[1:, :])
    for offset in (0, 1, 2):
        lines[offset:offset+2*h:2, 2:2*w:2] |= vertical
        lines[2:2*h:2, offset:offset+2*w:2] |= horizontal
    if not lines.any():
        return np.zeros(label.shape, dtype=bool)
    distance = distance_transform_edt(~lines)
    return valid & (distance[1::2, 1::2] <= 2.0)


def rate(n, d):
    return n / d if d else float('nan')


def error_rgb(label, prediction):
    rgb = np.empty((*label.shape, 3), dtype=np.uint8)
    colors = {k: tuple(bytes.fromhex(v[1:])) for k, v in COLORS.items()}
    rgb[:] = colors['other']
    crop = np.isin(label, (0, 2))
    rgb[crop & (label == prediction)] = colors['correct']
    rgb[crop & (label != prediction)] = colors['error']
    return rgb


def reference_rgb(label):
    colors = np.array([tuple(bytes.fromhex(COLORS[k][1:])) for k in ('corn', 'other', 'soybean')], dtype=np.uint8)
    assert np.isin(label, (0, 1, 2)).all()
    return colors[label]


def prepare():
    names = ['selected_windows.csv', 'local_metrics.csv', 'whole_site_metrics_reused.csv',
             'local_area_shape.csv', 'old_D_window.csv', 'input_grid_checks.csv',
             'verification_checks.csv', 'manifest.json', 'README.md']
    assert not any((OUT / n).exists() for n in names), 'Existing analysis outputs: preserve before regenerating'
    index = pd.read_csv(INDEX)
    index = index[index.kind.eq('within')]
    subsets = pd.read_csv(SUBSETS, float_precision='round_trip')
    whole = pd.read_csv(WHOLE, float_precision='round_trip')
    features = pd.read_csv(REF / 'reference_patch_features.csv', float_precision='round_trip')
    identity = json.loads(IDENTITY.read_text(encoding='utf-8'))['records']
    input_paths = [INDEX, SUBSETS, WHOLE, REF / 'reference_patch_features.csv', IDENTITY,
        ROOT / 'legacy/manuscript/HLS-Crop/src/learning/distance_band_analysis.py']
    checks, chosen, local, global_rows, shapes, grids, old_d = [], [], [], [], [], [], []

    def check(name, condition, **details):
        checks.append(dict(check=name, status='Verified' if condition else 'Not verified', **details))
        if not condition:
            raise AssertionError((name, details))

    for item in identity:
        if item['kind'] != 'within':
            continue
        jp = Path(item['source_json'])
        check('prediction_identity_json_hash', digest(jp) == item['source_json_sha256'],
              target=item['target'], model=item['model'], fold=item['fold'])
        run = json.loads(jp.read_text(encoding='utf-8'))
        check('held_out_fold', run['test_fold'] not in run['train_folds']
              and run['test_fold'] != run['val_fold'], target=item['target'], model=item['model'], fold=item['fold'])
        input_paths.append(jp)
    for site, target in SITES.items():
        print(f'{site}: load original references and predictions', flush=True)
        arrays, predictions, paths, grid_rows = read_site(target, index)
        input_paths.extend(paths); grids.extend(grid_rows)
        label = arrays['label']
        disagreement = correctness_disagreement(label, list(predictions.values()))
        selection = select_window(label, disagreement)
        selection.update(site=site, target=target, coordinate_rule='zero_based_half_open')
        chosen.append(selection)
        print(f'{site}: selected ({selection["row_start"]}, {selection["col_start"]}), '
              f'disagreement {selection["disagreement_ratio"]:.6%}', flush=True)
        sl = (slice(selection['row_start'], selection['row_stop']), slice(selection['col_start'], selection['col_stop']))
        print(f'{site}: verify complete-reference 30 m geometry', flush=True)
        boundary = boundary_mask(label)
        check('full_reference_30m_mask_matches_saved', np.array_equal(boundary, arrays['bands'] == 0),
              target=target, differing_pixels=int(np.count_nonzero(boundary != (arrays['bands'] == 0))))
        for model, pred in predictions.items():
            valid = np.isin(label, (0, 1, 2))
            cm = np.bincount((3*label[valid]+pred[valid]).ravel(), minlength=9).reshape(3, 3)
            for crop, code in CROPS.items():
                full_crop = label == code
                full_n, full_fn = int(full_crop.sum()), int(np.sum(full_crop & (pred != label)))
                expected = whole[(whole.target == target) & (whole.model == model) & (whole.crop == crop)].iloc[0]
                check('whole_FN_FP_TP', (full_fn, int(cm[:, code].sum()-cm[code, code]), int(cm[code, code]))
                      == (int(expected.fn), int(expected.fp), int(expected.tp)), target=target, model=model, crop=crop)
                for position, part in [('boundary', boundary), ('interior', ~boundary)]:
                    mask = full_crop & part
                    n, fn = int(mask.sum()), int(np.sum(mask & (pred != label)))
                    sub = 'nearest' if position == 'boundary' else 'interior_gt1'
                    old = subsets[(subsets.target == target) & (subsets.model == model)
                                  & (subsets.crop == crop) & (subsets.subset == sub)].iloc[0]
                    check('whole_saved_counts_and_rates', (n, fn, full_n, full_fn) ==
                        (int(old.reference_pixels), int(old.fn), int(old.whole_pixels), int(old.whole_fn))
                        and np.allclose([n/full_n, rate(fn, n), rate(fn, full_fn)],
                                        [old.area_share, old.omission_rate, old.error_share], atol=1e-14, rtol=0),
                        target=target, model=model, crop=crop, position=position)
                    global_rows.append(dict(site=site, target=target, model=model, crop=crop, position=position,
                        reference_pixels=n, fn=fn, whole_crop_pixels=full_n, whole_crop_fn=full_fn,
                        area_share=old.area_share, omission_rate=old.omission_rate,
                        error_share=old.error_share, scope='whole_site', data_status='reused_verified_summary',
                        source=path_key(SUBSETS), source_subset=sub))
            lab, pr, bd = label[sl], pred[sl], boundary[sl]
            for crop, crop_mask in [('corn', lab == 0), ('soybean', lab == 2), ('combined', np.isin(lab, (0, 2)))]:
                total_n = int(crop_mask.sum()); total_fn = int(np.sum(crop_mask & (lab != pr)))
                for position, part in [('whole', np.ones(lab.shape, bool)), ('boundary', bd), ('interior', ~bd)]:
                    mask = crop_mask & part
                    n, fn = int(mask.sum()), int(np.sum(mask & (lab != pr)))
                    local.append(dict(site=site, target=target, model=model, crop=crop, position=position,
                        reference_pixels=n, fn=fn, whole_crop_pixels=total_n, whole_crop_fn=total_fn,
                        area_share=rate(n, total_n), omission_rate=rate(fn, n), error_share=rate(fn, total_fn),
                        scope='selected_window', row_start=selection['row_start'], col_start=selection['col_start'],
                        data_status='derived_from_original_reference_and_prediction'))
                if crop == 'combined':
                    selection[f'{model}_crop_omission_rate'] = rate(total_fn, total_n)
            if site == 'D':
                old_sl = (slice(1664, 1920), slice(1024, 1280))
                mask = np.isin(label[old_sl], (0, 2))
                old_d.append(dict(site=site, model=model, row_start=1664, col_start=1024,
                    crop_pixels=int(mask.sum()), disagreement_pixels=int(disagreement[old_sl].sum()),
                    disagreement_ratio=float(disagreement[old_sl].sum()/mask.sum()),
                    fn=int(np.sum(mask & (label[old_sl] != pred[old_sl]))),
                    omission_rate=float(np.mean(pred[old_sl][mask] != label[old_sl][mask]))))
        f = features[features.target.eq(target)].set_index('PID')
        unique_ids, counts = np.unique(arrays['ids'][sl], return_counts=True)
        for pid, n in zip(unique_ids, counts):
            row = f.loc[int(pid)]
            if row.crop not in CROPS:
                continue
            a = int(np.searchsorted([10, 50, 100, 200, 500], row.AREA, side='right'))
            s = int(np.searchsorted([1.5, 2, 3], row.SHAPE, side='right'))
            shapes.append(dict(site=site, target=target, PID=int(pid), crop=row.crop,
                AREA=row.AREA, SHAPE=row.SHAPE, area_bin=a, shape_bin=s,
                local_pixels=int(n), complete_patch_pixels=int(row.reference_pixels),
                cut_by_window=int(n) < int(row.reference_pixels),
                touches_site_outer_edge=bool(row.touches_outer_edge),
                data_status='derived_local_support_with_complete_reference_patch_features'))
        print(f'{site}: counts and geometry verified', flush=True)
    outputs = [save_csv(rows, name) for rows, name in [(chosen, 'selected_windows'), (local, 'local_metrics'),
        (global_rows, 'whole_site_metrics_reused'), (shapes, 'local_area_shape'), (old_d, 'old_D_window'),
        (grids, 'input_grid_checks'), (checks, 'verification_checks')]]
    manifest = dict(date='2026-10-16', data_status='derived', verification='Verified',
        window_size=WINDOW, stride=1, minimum_crop_share='each crop >= 1/10 window area',
        selection='maximum correctness-disagreement / reference crop pixels',
        tie_break='exact integer fraction comparison, then smallest row and column',
        boundary='full-reference valid 4-neighbour shared edges; centre distance <=30 m',
        boundary_verification='four full masks regenerated and compared pixelwise; saved count tables reused',
        input_sha256={path_key(p): digest(p) for p in dict.fromkeys(input_paths)},
        script_sha256=digest(Path(__file__)), output_sha256={path_key(p): digest(p) for p in outputs},
        scope='within-site only; selected differences are not typical-site samples or F1 decomposition')
    write_new(OUT/'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print('Prepared new analysis tables; frozen coordinates saved.', flush=True)


def plot():
    import figstyle as fs
    import matplotlib.pyplot as plt
    fs.setup()
    selections = pd.read_csv(OUT/'selected_windows.csv')
    index = pd.read_csv(INDEX); index = index[index.kind.eq('within')]
    names = [FIG/f'fig_within_site_errors_{site}_{column}.{ext}'
             for site in SITES for column in ('reference', *MODELS) for ext in ('pdf', 'png')]
    assert not any(p.exists() for p in names), 'Existing figure assets: preserve before regenerating'
    outputs = []
    for site, target in SITES.items():
        arrays, predictions, _, _ = read_site(target, index)
        selected = selections[selections.site.eq(site)].iloc[0]
        sl = (slice(int(selected.row_start), int(selected.row_stop)), slice(int(selected.col_start), int(selected.col_stop)))
        label = arrays['label'][sl]
        panels = {'reference': reference_rgb(label)} | {m: error_rgb(label, predictions[m][sl]) for m in MODELS}
        for column, rgb in panels.items():
            fig = plt.figure(figsize=(fs.UNIT*fs.CM, fs.UNIT*fs.CM))
            ax = fig.add_axes([0, 0, 1, 1])
            # PDF embeds the original 256 pixels; raster preview uses nearest-neighbour.
            ax.imshow(rgb, interpolation='none', origin='upper')
            ax.set_axis_off()
            for ext in ('pdf', 'png'):
                path = FIG/f'fig_within_site_errors_{site}_{column}.{ext}'
                # Exact 3.8 cm page; preserve native nearest-neighbour pixel map in PDF.
                fig.savefig(path, bbox_inches=None, pad_inches=0, dpi=300)
                outputs.append(path)
            plt.close(fig)
    write_new(OUT/'figure_manifest.json', json.dumps(dict(date='2026-10-16', colors=COLORS,
        panel_cm=[3.8, 3.8], alpha=1, interpolation='nearest', boundary_lines=False,
        selected_windows_sha256=digest(OUT/'selected_windows.csv'),
        script_sha256=digest(Path(__file__)), output_sha256={path_key(p): digest(p) for p in outputs}), indent=2)+'\n')
    print('Generated 16 PDF panels and 16 PNG previews.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--prepare', action='store_true')
    group.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    prepare() if args.prepare else plot()

"""Independent small-array oracles and optional read-only artifact checks."""
from pathlib import Path
import sys
import unittest

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from plot_within_site_errors import (COLORS, INDEX, MODELS, OUT, REF, SITES,
    boundary_mask, correctness_disagreement, error_rgb, rate, select_window)


def brute_window(label, disagreement, size):
    best = None
    eligible = 0
    ties = 0
    for r in range(label.shape[0] - size + 1):
        for c in range(label.shape[1] - size + 1):
            block = label[r:r+size, c:c+size]
            nc, ns = int(np.sum(block == 0)), int(np.sum(block == 2))
            if not np.isin(block, [0, 1, 2]).all() or 10*nc < size*size or 10*ns < size*size:
                continue
            eligible += 1
            n = int(disagreement[r:r+size, c:c+size].sum()); d = nc+ns
            diff = 1 if best is None else n*best[3] - best[2]*d
            if diff > 0:
                best = (r, c, n, d); ties = 1
            elif diff == 0:
                ties += 1
    if best is None:
        raise ValueError('No eligible window')
    return best, eligible, ties


def segment_oracle(label):
    # Unit squares have integer corners and half-integer centres.
    segments = []
    valid = np.isin(label, [0, 1, 2])
    for r, c in np.ndindex(label.shape):
        if not valid[r, c]:
            continue
        if c+1 < label.shape[1] and valid[r, c+1] and label[r, c] != label[r, c+1]:
            segments.append(((r, c+1), (r+1, c+1)))
        if r+1 < label.shape[0] and valid[r+1, c] and label[r, c] != label[r+1, c]:
            segments.append(((r+1, c), (r+1, c+1)))
    result = np.zeros(label.shape, bool)
    for r, c in np.ndindex(label.shape):
        if not valid[r, c]:
            continue
        p = np.array([r+.5, c+.5])
        for a, b in segments:
            a, b = np.array(a, float), np.array(b, float)
            t = np.clip(np.dot(p-a, b-a)/np.dot(b-a, b-a), 0, 1)
            if np.linalg.norm(p-(a+t*(b-a))) <= 1:
                result[r, c] = True
                break
    return result


class Algorithms(unittest.TestCase):
    def test_disagreement_semantics_and_model_order(self):
        label = np.array([[0, 0, 0, 0, 2, 1]], np.uint8)
        predictions = [np.array([x], np.uint8) for x in
                       [[0, 1, 0, 0, 2, 0], [0, 2, 1, 0, 0, 1], [0, 1, 2, 2, 1, 2]]]
        expected = np.array([[False, False, True, True, True, False]])
        np.testing.assert_array_equal(correctness_disagreement(label, predictions), expected)
        np.testing.assert_array_equal(correctness_disagreement(label, predictions[::-1]), expected)

    def test_selection_against_brute_force(self):
        rng = np.random.default_rng(31016)
        for size in (3, 4, 5):
            for _ in range(12):
                label = rng.choice([0, 1, 2, 255], size=(9, 11), p=[.4, .15, .4, .05]).astype(np.uint8)
                preds = [rng.integers(0, 3, label.shape, dtype=np.uint8) for _ in MODELS]
                disagreement = correctness_disagreement(label, preds)
                try:
                    expected, eligible, ties = brute_window(label, disagreement, size)
                except ValueError:
                    with self.assertRaises(ValueError): select_window(label, disagreement, size)
                    continue
                actual = select_window(label, disagreement, size)
                self.assertEqual(tuple(actual[k] for k in ['row_start','col_start','disagreement_pixels','crop_pixels']), expected)
                self.assertEqual(actual['eligible_count'], eligible)
                self.assertEqual(actual['tied_maximum_count'], ties)

    def test_threshold_ties_and_invalid_reference(self):
        label = np.zeros((10, 10), np.uint8)
        label.flat[:10] = 2
        selected = select_window(label, np.zeros_like(label, bool), 10)
        self.assertEqual(selected['soybean_pixels'], 10)
        label.flat[0] = 0
        with self.assertRaises(ValueError): select_window(label, np.zeros_like(label, bool), 10)
        label.flat[0] = 255
        with self.assertRaises(ValueError): select_window(label, np.zeros_like(label, bool), 10)
        label = np.indices((8, 8)).sum(0) % 2 * 2
        selected = select_window(label, np.ones_like(label, bool), 4)
        self.assertEqual((selected['row_start'], selected['col_start'], selected['tied_maximum_count']), (0, 0, 25))

    def test_shared_edge_geometry(self):
        rng = np.random.default_rng(30)
        examples = [np.zeros((4, 5), np.uint8), np.array([[0, 0, 255], [0, 0, 255]], np.uint8),
            np.array([[0, 0, 0], [0, 0, 2], [0, 0, 2]], np.uint8),
            np.tile([0, 0, 0, 2, 2, 2], (5, 1))]
        examples += [rng.choice([0, 1, 2, 255], (6, 7)).astype(np.uint8) for _ in range(12)]
        for label in examples:
            np.testing.assert_array_equal(boundary_mask(label), segment_oracle(label))
        full = np.zeros((8, 8), np.uint8); full[:, 4:] = 2
        # Crop edge at column 4 must not erase a real edge just outside the view.
        self.assertTrue(boundary_mask(full)[:, 2:4][:, -1].all())
        self.assertFalse(boundary_mask(full[:, 2:4]).any())

    def test_colors_and_zero_denominator(self):
        lab = np.array([[0, 2, 1], [0, 2, 1]], np.uint8)
        pred = np.array([[0, 2, 0], [2, 1, 2]], np.uint8)
        rgb = error_rgb(lab, pred)
        color = lambda key: np.array(list(bytes.fromhex(COLORS[key][1:])), np.uint8)
        for r, c in [(0, 0), (0, 1)]: np.testing.assert_array_equal(rgb[r,c], color('correct'))
        for r, c in [(1, 0), (1, 1)]: np.testing.assert_array_equal(rgb[r,c], color('error'))
        np.testing.assert_array_equal(rgb[:,2], np.tile(color('other'), (2,1)))
        self.assertTrue(np.isnan(rate(0, 0)))


def artifacts():
    import hashlib
    import json
    import pandas as pd
    import pymupdf
    from plot_within_site_errors import read_site, reference_rgb
    manifest = json.loads((OUT/'manifest.json').read_text(encoding='utf-8'))
    for relative, expected in manifest['input_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected, relative
    for relative, expected in manifest['output_sha256'].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest() == expected, relative
    assert hashlib.sha256((ROOT/'scripts/plot_within_site_errors.py').read_bytes()).hexdigest() == manifest['script_sha256']
    index = pd.read_csv(INDEX); index = index[index.kind.eq('within')]
    selections = pd.read_csv(OUT/'selected_windows.csv')
    local = pd.read_csv(OUT/'local_metrics.csv')
    assert len(local) == 108
    for _, g in local.groupby(['target','model','crop']):
        g = g.set_index('position')
        for col in ['reference_pixels','fn']:
            assert int(g.loc['boundary',col]+g.loc['interior',col]) == int(g.loc['whole',col])
        assert np.isclose(g.loc[['boundary','interior'],'area_share'].sum(), 1)
    for site,target in SITES.items():
        arrays, predictions, _, _ = read_site(target, index)
        label=arrays['label']; chosen=selections[selections.site.eq(site)].iloc[0]
        disagree=correctness_disagreement(label,list(predictions.values()))
        # Independent all-window array calculation, not the production row tournament.
        sums=[]
        for mask in [np.isin(label,(0,1,2)),label==0,label==2,disagree]:
            a=np.zeros((label.shape[0]+1,label.shape[1]+1),np.int64)
            a[1:,1:]=np.cumsum(np.cumsum(mask,axis=1,dtype=np.int64),axis=0,dtype=np.int64)
            sums.append(a[256:,256:]+a[:-256,:-256]-a[256:,:-256]-a[:-256,256:])
        valid=(sums[0]==256*256)&(sums[1]*10>=256*256)&(sums[2]*10>=256*256)
        comparison=sums[3]*int(chosen.crop_pixels)-(sums[1]+sums[2])*int(chosen.disagreement_pixels)
        assert not np.any(valid&(comparison>0))
        rr,cc=np.nonzero(valid&(comparison==0))
        assert (int(rr[0]),int(cc[0]))==(chosen.row_start,chosen.col_start)
        assert len(rr)==chosen.tied_maximum_count and int(valid.sum())==chosen.eligible_count
        sl=(slice(int(chosen.row_start),int(chosen.row_stop)),slice(int(chosen.col_start),int(chosen.col_stop)))
        panels={'reference':reference_rgb(label[sl])}|{m:error_rgb(label[sl],predictions[m][sl]) for m in MODELS}
        for column,expected_rgb in panels.items():
            p=ROOT/f'figures/results/fig_within_site_errors_{site}_{column}.pdf'
            with pymupdf.open(p) as doc:
                assert len(doc)==1
                assert abs(doc[0].rect.width-3.8/2.54*72)<.01
                assert abs(doc[0].rect.height-3.8/2.54*72)<.01
                images=doc[0].get_images()
                assert len(images)==1 and images[0][2:4]==(256,256)
                pix=pymupdf.Pixmap(doc,images[0][0])
                actual=np.frombuffer(pix.samples,np.uint8).reshape(256,256,pix.n)
                transform=doc[0].get_image_info()[0]['transform']
                assert transform[0]>0 and transform[1]==transform[2]==0 and transform[3]<0
                # Matplotlib stores bottom-up rows and places them with negative y scale.
                np.testing.assert_array_equal(actual[::-1],expected_rgb)
                assert images[0][1]==0, 'Unexpected transparency mask'
                drawings=doc[0].get_drawings()
                assert len(drawings)==1 and drawings[0]['type']=='f'
                assert drawings[0]['fill']==(1.,1.,1.) and drawings[0]['seqno']==0
                assert drawings[0]['rect']==doc[0].rect, 'Unexpected boundary/overlay lines'
        print(site, 'all-window maximum, tie rule, local closure and 4 PDF raster pixels verified',flush=True)


if __name__ == '__main__':
    if '--artifacts' in sys.argv:
        artifacts()
    else:
        unittest.main()

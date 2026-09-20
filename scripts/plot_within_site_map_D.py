#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：D 站三种模型站内交叉验证分类结果对比

布局（通栏，两行四列，子图各 3.8×3.8 cm，LaTeX subcaption 拼）：
  第 1 行：全站 2560×2560，(a) 参考标签 (b) ConvGRU (c) 3D U-Net (d) U-TAE；每幅标同一红框窗口
  第 2 行：红框窗口放大，(e)(f)(g)(h) 对应上一行
八子图同配色；子图题、底部图例、图名都是 LaTeX 文本。

输入：D:/20il/2023{model}ilresults/summary/maps/{reference,oof_prediction}.tif
      oof_prediction 为五折交叉验证拼接，每个图块的预测来自未训练过它的模型
      值：1=玉米 2=其它 3=大豆
输出：figures/results/fig_within_site_map_D_{a..h}.pdf / .png（每子图一个，LaTeX 拼 2×4）
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import hashlib
import numpy as np
import tifffile
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Rectangle
import figstyle as fs

fs.setup()

SITE_DIR = 'D:/20il'
SITE_TAG = 'il'
MODELS = [(k, fs.MODEL_LABELS[k]) for k in fs.MODEL_ORDER]

# 窗口选择：在 20×20 图块网格上搜索 2×2 / 3×3 窗口，指标只看真实为玉米、大豆的像元：
#   score = [作物像元错误率(ConvGRU) − 另两模型均值] + [类别边界带(约 2 像元)错误率(ConvGRU) − 另两模型均值]
# (13,8) 2×2 得分最高：作物像元错误 12.1% / 5.8% / 4.8%，边界带错误 32.0% / 15.3% / 13.4%，
# 玉米↔大豆互混 6.8% / 2.6% / 2.2%（ConvGRU / 3D U-Net / U-TAE）。
WIN_TILE_ROW, WIN_TILE_COL, WIN_TILES = 13, 8, 2
TILE = 128

CLASS_COLORS = fs.CLASS_COLORS
CLASS_NAMES = fs.CLASS_NAMES
LEGEND_ORDER = fs.CLASS_LEGEND_ORDER


def load(model, name):
    return tifffile.imread(f'{SITE_DIR}/2023{model}{SITE_TAG}results/summary/maps/{name}.tif')


def main():
    refs = {m: load(m, 'reference') for m, _ in MODELS}
    shas = {m: hashlib.sha256(r.tobytes()).hexdigest() for m, r in refs.items()}
    assert len(set(shas.values())) == 1, f'三模型参考标签不一致: {shas}'
    ref = refs['utae']
    preds = {m: load(m, 'oof_prediction') for m, _ in MODELS}
    for m, p in preds.items():
        assert p.shape == ref.shape and set(np.unique(p)) <= {1, 2, 3}, m

    r0, c0 = WIN_TILE_ROW * TILE, WIN_TILE_COL * TILE
    size = WIN_TILES * TILE
    sl = (slice(r0, r0 + size), slice(c0, c0 + size))

    full = [('参考标签', ref)] + [(f'{lab}分类结果', preds[m]) for m, lab in MODELS]
    cmap = ListedColormap([CLASS_COLORS[k] for k in (1, 2, 3)])
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5], cmap.N)

    # 8 个子图各出一个 PDF（图框 3.8×3.8 cm），LaTeX 用 subcaption 排 2 行 4 列；子图题、图例是文本
    #   a–d 全站（黑框，红框标窗口）  e–h 局部窗口（红框）
    letters = 'abcdefgh'
    for j, (name, arr) in enumerate(full):
        fig, axes = fs.grid(1, 1, w=1, h=1, margin=(0.1, 0.1, 0.1, 0.1))
        ax = axes[0, 0]
        ax.imshow(arr, cmap=cmap, norm=norm, interpolation='nearest')
        ax.add_patch(Rectangle((c0, r0), size, size, fill=False, edgecolor='red', linewidth=1.0))
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_linewidth(0.6)
        fs.save(fig, f'fig_within_site_map_D_{letters[j]}')

        fig, axes = fs.grid(1, 1, w=1, h=1, margin=(0.1, 0.1, 0.1, 0.1))
        ax = axes[0, 0]
        ax.imshow(arr[sl], cmap=cmap, norm=norm, interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_edgecolor('red'); s.set_linewidth(1.0)
        fs.save(fig, f'fig_within_site_map_D_{letters[4 + j]}')

    win_err = {lab: float((preds[m][sl] != ref[sl]).mean()) for m, lab in MODELS}
    full_err = {lab: float((preds[m] != ref).mean()) for m, lab in MODELS}
    print('Generated: figures/results/fig_within_site_map_D_{a..h}.pdf / .png')
    print(f'window: tiles ({WIN_TILE_ROW},{WIN_TILE_COL}) {WIN_TILES}x{WIN_TILES}, px rows {r0}-{r0+size} cols {c0}-{c0+size}')
    print('window err:', {k: round(v, 4) for k, v in win_err.items()})
    print('full err:  ', {k: round(v, 4) for k, v in full_err.items()})
    print('reference sha256:', shas['utae'][:16])


if __name__ == '__main__':
    main()

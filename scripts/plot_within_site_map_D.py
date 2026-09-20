#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：D 站三种模型站内交叉验证分类结果对比

布局（单栏宽，两行四列）：
  第 1 行：全站 2560×2560，(a) 参考标签 (b) ConvGRU (c) 3D U-Net (d) U-TAE；每幅标同一红框窗口
  第 2 行：红框窗口放大，(e)(f)(g)(h) 对应上一行
四子图同范围、同配色、共用底部图例；子图题在各子图下。
图名写在正文 caption。

输入：D:/20il/2023{model}ilresults/summary/maps/{reference,oof_prediction}.tif
      oof_prediction 为五折交叉验证拼接，每个图块的预测来自未训练过它的模型
      值：1=玉米 2=其它 3=大豆
输出：figures/results/fig_within_site_map_D.png / .pdf
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import hashlib
import numpy as np
import tifffile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle
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

    # 通栏 16 cm × 8 cm（4 模 × 2 模）
    fig, axes = plt.subplots(2, 4, figsize=(fs.FULL_W, 2 * fs.MODULE))
    letters = 'abcdefgh'
    for j, (name, arr) in enumerate(full):
        ax = axes[0, j]
        ax.imshow(arr, cmap=cmap, norm=norm, interpolation='nearest')
        ax.add_patch(Rectangle((c0, r0), size, size, fill=False, edgecolor='red', linewidth=1.0))
        ax.set_xlabel(f'（{letters[j]}）{name}', fontsize=fs.FS_SUBTITLE, labelpad=1.5)

        ax = axes[1, j]
        ax.imshow(arr[sl], cmap=cmap, norm=norm, interpolation='nearest')
        for s in ax.spines.values():
            s.set_edgecolor('red'); s.set_linewidth(1.0)
        ax.set_xlabel(f'（{letters[4 + j]}）{name}', fontsize=fs.FS_SUBTITLE, labelpad=1.5)

    for ax in axes.ravel():
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_linewidth(max(s.get_linewidth(), 0.5))

    handles = [Patch(facecolor=CLASS_COLORS[k], edgecolor='black', linewidth=0.4, label=CLASS_NAMES[k])
               for k in LEGEND_ORDER]
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.0), handlelength=1.4, columnspacing=1.8)

    plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.115, wspace=0.05, hspace=0.20)
    plt.savefig('figures/results/fig_within_site_map_D.png')
    plt.savefig('figures/results/fig_within_site_map_D.pdf')
    plt.close()

    win_err = {lab: float((preds[m][sl] != ref[sl]).mean()) for m, lab in MODELS}
    full_err = {lab: float((preds[m] != ref).mean()) for m, lab in MODELS}
    print('Generated: figures/results/fig_within_site_map_D.png / .pdf')
    print(f'window: tiles ({WIN_TILE_ROW},{WIN_TILE_COL}) {WIN_TILES}x{WIN_TILES}, px rows {r0}-{r0+size} cols {c0}-{c0+size}')
    print('window err:', {k: round(v, 4) for k, v in win_err.items()})
    print('full err:  ', {k: round(v, 4) for k, v in full_err.items()})
    print('reference sha256:', shas['utae'][:16])


if __name__ == '__main__':
    main()

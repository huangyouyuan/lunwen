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

import hashlib
import numpy as np
import tifffile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch, Rectangle

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

SITE_DIR = 'D:/20il'
SITE_TAG = 'il'
MODELS = [('convgru', 'ConvGRU'), ('unet3d', '3D U-Net'), ('utae', 'U-TAE')]

WIN_TILE_ROW, WIN_TILE_COL, WIN_TILES = 5, 7, 3
TILE = 128

CLASS_COLORS = {1: '#F2C14E', 2: '#BDBDBD', 3: '#4C9F70'}
CLASS_NAMES = {1: '玉米', 2: '其它', 3: '大豆'}
LEGEND_ORDER = (1, 3, 2)   # 玉米、大豆在前，其它在后


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

    # 通栏宽：A4 正文宽 21 − 1.8×2 = 17.4 cm ≈ 6.85 in；四列图各 ≈ 1.6 in
    fig, axes = plt.subplots(2, 4, figsize=(6.85, 3.85))
    letters = 'abcdefgh'
    for j, (name, arr) in enumerate(full):
        ax = axes[0, j]
        ax.imshow(arr, cmap=cmap, norm=norm, interpolation='nearest')
        ax.add_patch(Rectangle((c0, r0), size, size, fill=False, edgecolor='red', linewidth=1.0))
        ax.set_xlabel(f'（{letters[j]}）{name}', fontsize=8, labelpad=2)

        ax = axes[1, j]
        ax.imshow(arr[sl], cmap=cmap, norm=norm, interpolation='nearest')
        for s in ax.spines.values():
            s.set_edgecolor('red'); s.set_linewidth(1.0)
        ax.set_xlabel(f'（{letters[4 + j]}）{name}', fontsize=8, labelpad=2)

    for ax in axes.ravel():
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_linewidth(max(s.get_linewidth(), 0.5))

    handles = [Patch(facecolor=CLASS_COLORS[k], edgecolor='black', linewidth=0.4, label=CLASS_NAMES[k])
               for k in LEGEND_ORDER]
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, 0.0), fontsize=8, handlelength=1.4, columnspacing=1.8)

    plt.subplots_adjust(left=0.005, right=0.995, top=0.995, bottom=0.10, wspace=0.05, hspace=0.22)
    plt.savefig('figures/results/fig_within_site_map_D.png', dpi=300, bbox_inches='tight', pad_inches=0.02)
    plt.savefig('figures/results/fig_within_site_map_D.pdf', bbox_inches='tight', pad_inches=0.02)
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

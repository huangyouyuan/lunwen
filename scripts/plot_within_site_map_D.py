#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3.1 用图：D 站三种模型站内交叉验证分类结果对比（局部窗口）

(a) 参考标签  (b) ConvGRU  (c) 3D U-Net  (d) U-TAE
四子图同一空间范围、同一配色、共用图例；子图题在下方。
图名、图注写在正文 caption。

输入：D:/20il/2023{model}ilresults/summary/maps/{reference,oof_prediction}.tif
      oof_prediction 为五折交叉验证拼接结果，每个图块的预测来自未训练过它的模型
      值：1=玉米 2=其它 3=大豆（源标签，未减 1）
输出：figures/results/fig_within_site_map_D.png / .pdf
"""

import hashlib
import numpy as np
import tifffile
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
from matplotlib.patches import Patch

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

SITE_DIR = 'D:/20il'
SITE_TAG = 'il'
MODELS = [('convgru', 'ConvGRU'), ('unet3d', '3D U-Net'), ('utae', 'U-TAE')]

# 局部窗口：128 图块网格上的 (row, col) 起点与边长（图块数）
WIN_TILE_ROW, WIN_TILE_COL, WIN_TILES = 5, 7, 3
TILE = 128

# 类别配色：1 玉米、2 其它、3 大豆
CLASS_COLORS = {1: '#F2C14E', 2: '#BDBDBD', 3: '#4C9F70'}
CLASS_NAMES = {1: '玉米', 2: '其它', 3: '大豆'}


def load(model, name):
    return tifffile.imread(f'{SITE_DIR}/2023{model}{SITE_TAG}results/summary/maps/{name}.tif')


def main():
    refs = {m: load(m, 'reference') for m, _ in MODELS}
    shas = {m: hashlib.sha256(r.tobytes()).hexdigest() for m, r in refs.items()}
    assert len(set(shas.values())) == 1, f'三模型参考标签不一致: {shas}'
    ref = refs['utae']
    preds = {m: load(m, 'oof_prediction') for m, _ in MODELS}
    for m, p in preds.items():
        assert p.shape == ref.shape, m
        assert set(np.unique(p)) <= {1, 2, 3}, m

    r0, c0 = WIN_TILE_ROW * TILE, WIN_TILE_COL * TILE
    size = WIN_TILES * TILE
    sl = (slice(r0, r0 + size), slice(c0, c0 + size))
    panels = [('（a）参考标签', ref[sl])] + \
             [(f'（{chr(98 + i)}）{label}分类结果', preds[m][sl]) for i, (m, label) in enumerate(MODELS)]

    cmap = ListedColormap([CLASS_COLORS[k] for k in (1, 2, 3)])
    norm = BoundaryNorm([0.5, 1.5, 2.5, 3.5], cmap.N)

    fig, axes = plt.subplots(2, 2, figsize=(3.4, 3.9))
    for ax, (title, arr) in zip(axes.ravel(), panels):
        ax.imshow(arr, cmap=cmap, norm=norm, interpolation='nearest')
        ax.set_xticks([]); ax.set_yticks([])
        for s in ax.spines.values():
            s.set_linewidth(0.5)
        ax.set_xlabel(title, fontsize=8, labelpad=3)

    handles = [Patch(facecolor=CLASS_COLORS[k], edgecolor='black', linewidth=0.4, label=CLASS_NAMES[k])
               for k in (1, 2, 3)]
    fig.legend(handles=handles, loc='lower center', ncol=3, frameon=False,
               bbox_to_anchor=(0.5, -0.005), fontsize=8, handlelength=1.2, columnspacing=1.5)

    plt.tight_layout(rect=[0, 0.05, 1, 1], h_pad=0.6, w_pad=0.6)
    plt.savefig('figures/results/fig_within_site_map_D.png', dpi=300, bbox_inches='tight')
    plt.savefig('figures/results/fig_within_site_map_D.pdf', bbox_inches='tight')
    plt.close()

    win_err = {label: float((preds[m][sl] != ref[sl]).mean()) for m, label in MODELS}
    full_err = {label: float((preds[m] != ref).mean()) for m, label in MODELS}
    print('Generated: figures/results/fig_within_site_map_D.png / .pdf')
    print(f'window: tiles ({WIN_TILE_ROW},{WIN_TILE_COL}) size {WIN_TILES}x{WIN_TILES}  px rows {r0}-{r0+size}, cols {c0}-{c0+size}')
    print('window error rate:', {k: round(v, 4) for k, v in win_err.items()})
    print('full-site error rate:', {k: round(v, 4) for k, v in full_err.items()})
    print('reference sha256:', shas['utae'][:16])


if __name__ == '__main__':
    main()

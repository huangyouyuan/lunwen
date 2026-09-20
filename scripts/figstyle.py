#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表统一规格（所有绘图脚本 import 此文件）。用户 2026-09-20 定：

尺寸  只算图框内有效面积。基本单元 UNIT = 3.8 cm 见方，其它尺寸取整数倍或 0.5 倍
      （3.8 / 5.7 / 7.6 / 11.4 / 15.2）。同一张图的子图一样大。
文字  与正文同：中文宋体、字母数字 Times New Roman、小五 9 pt。
图名  图名、子图题都是 LaTeX 文本（subcaption），不画进图片；图片里只有图框、刻度、数值、轴标签。
输出  每个子图单独一个 PDF（LaTeX 按原尺寸放，不缩放）+ 同名 PNG 预览。
配色  三模型紫 / 青 / 橘；三类地物玉米黄 / 大豆绿 / 其它灰。LaTeX 图例用同一组色（main.tex 定义）。
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

CM = 1 / 2.54
UNIT = 3.8                          # cm，图框基本边长

MODEL_COLORS = {
    'convgru': '#7B3FA0',   # 紫
    'unet3d':  '#1B9E9E',   # 青
    'utae':    '#E8731A',   # 橘
}
MODEL_LABELS = {'convgru': 'ConvGRU', 'unet3d': '3D U-Net', 'utae': 'U-TAE'}
MODEL_ORDER = ['convgru', 'unet3d', 'utae']

CLASS_COLORS = {1: '#F2C14E', 3: '#4C9F70', 2: '#BDBDBD'}   # 玉米 / 大豆 / 其它
CLASS_NAMES = {1: '玉米', 3: '大豆', 2: '其它'}
CLASS_LEGEND_ORDER = (1, 3, 2)

SITE_MAP = {'iw_2023': 'A', 'iw2_2023': 'B', 'ida_2023': 'C', 'il_2023': 'D'}
SITES = ['A', 'B', 'C', 'D']

FS = 9                              # 小五

OUT_DIR = 'figures/results'


def setup():
    plt.rcParams.update({
        # 回退列表必须写在 font.family：字母数字 Times New Roman，中文落到宋体
        'font.family': ['Times New Roman', 'SimSun'],
        'axes.unicode_minus': False,
        'font.size': FS,
        'axes.labelsize': FS,
        'axes.labelpad': 3,
        'xtick.labelsize': FS,
        'ytick.labelsize': FS,
        'legend.fontsize': FS,
        'xtick.major.size': 2.5, 'ytick.major.size': 2.5,
        'xtick.major.pad': 2, 'ytick.major.pad': 2,
        'axes.linewidth': 0.6,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'pdf.fonttype': 42,         # TrueType 嵌入，文字可选可搜
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.02,
    })


def grid(nrows=1, ncols=1, w=1.0, h=1.0, wgap=0.5, hgap=0.8, margin=(1.2, 1.2, 0.3, 0.3)):
    """
    建一张图，每个 axes 的图框恰好 w×UNIT 乘 h×UNIT cm（w、h 取整数或 0.5）。
    wgap / hgap 为子图间距（cm），margin=(left, bottom, right, top) cm；多余白边由 bbox tight 裁掉，
    图框尺寸不受影响。返回 fig, axes（二维 ndarray）。
    """
    for v in (w, h):
        assert abs(v * 2 - round(v * 2)) < 1e-9, '尺寸只能取 UNIT 的整数或 0.5 倍'
    aw, ah = w * UNIT, h * UNIT
    left, bottom, right, top = margin
    W = left + ncols * aw + (ncols - 1) * wgap + right
    H = bottom + nrows * ah + (nrows - 1) * hgap + top
    fig = plt.figure(figsize=(W * CM, H * CM))
    axes = np.empty((nrows, ncols), dtype=object)
    for i in range(nrows):
        for j in range(ncols):
            x0 = (left + j * (aw + wgap)) / W
            y0 = (bottom + (nrows - 1 - i) * (ah + hgap)) / H
            axes[i, j] = fig.add_axes([x0, y0, aw / W, ah / H])
    return fig, axes


def save(fig, stem):
    """保存 figures/results/{stem}.pdf（LaTeX 用，原尺寸）和 .png（预览）。"""
    fig.savefig(f'{OUT_DIR}/{stem}.pdf')
    fig.savefig(f'{OUT_DIR}/{stem}.png')
    plt.close(fig)
    return f'{OUT_DIR}/{stem}.pdf'

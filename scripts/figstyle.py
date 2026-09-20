#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表统一规格（所有绘图脚本 import 此文件）

尺寸以 4 cm 为模数：
  单栏宽 8 cm（2 模）  通栏宽 16 cm（4 模）
  高度取 8 / 12 / 16 cm
配色：三模型固定紫 / 青 / 橘；三类地物固定玉米黄 / 大豆绿 / 其它灰
字号：图内文字 8 pt（≈ 小五），子图题 8.5 pt，轴刻度 7.5 pt
"""

import matplotlib.pyplot as plt

CM = 1 / 2.54
MODULE = 4 * CM                     # 4 cm

COL_W = 2 * MODULE                  # 8 cm 单栏
FULL_W = 4 * MODULE                 # 16 cm 通栏

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

FS_TEXT = 8
FS_SUBTITLE = 8.5
FS_TICK = 6.5
FS_ANNOT = 6.5


def setup():
    plt.rcParams.update({
        # 回退列表必须写在 font.family（写在 font.sans-serif 不回退）：数字、字母用 Arial，中文落到黑体
        'font.family': ['Arial', 'SimHei'],
        'axes.unicode_minus': False,
        'font.size': FS_TEXT,
        'axes.labelsize': FS_TEXT,
        'axes.labelpad': 2,
        'xtick.labelsize': FS_TICK,
        'ytick.labelsize': FS_TICK,
        'xtick.major.size': 2, 'ytick.major.size': 2,
        'xtick.major.pad': 1.5, 'ytick.major.pad': 1.5,
        'legend.fontsize': FS_TEXT,
        'axes.linewidth': 0.6,
        'xtick.major.width': 0.5,
        'ytick.major.width': 0.5,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.01,
    })

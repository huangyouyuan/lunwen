# 退化热力图

```
python scripts/plot_degradation_heatmap.py
```

输入：`results/summary/crop_f1_degradation_36paths.csv`（`corn_loss_pp`、`soybean_loss_pp`）
输出：`fig_degradation_heatmap.png`（300 dpi）、`fig_degradation_heatmap.pdf`

规格：2 行（玉米/大豆）× 3 列（ConvGRU/3D U-Net/U-TAE）；行=源站，列=目标站（A–D）；对角线留空；单元格标两位小数；YlOrRd，共用色标（自动取全局范围，当前 0–8 pp）；图内只有子图序号和轴标签，图名、图注、英文均不在图内。

图题与图注文本见 `figures/data-manifest.md`。

脚本运行后打印六组 mean/std/min/max，应与 csv 一致（2026-09-18 已核对）。

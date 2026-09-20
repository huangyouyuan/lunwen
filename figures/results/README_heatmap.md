# 退化热力图

```
python scripts/plot_degradation_heatmap.py
```

输入：`results/summary/crop_f1_degradation_36paths.csv`（`corn_loss_pp`、`soybean_loss_pp`）
输出：`fig_degradation_heatmap_{a..f}.pdf`（每子图一个，LaTeX subcaption 拼）+ `fig_degradation_heatmap_cbar.pdf`；同名 PNG 只作预览

命令行参数 = 子图图框边长的 UNIT（3.8 cm）倍数：`1` → 3.8 cm（2 行 3 列），`1.5` → 5.7 cm（3 行 2 列，当前 tex 用此版）

规格：每子图图框 3.8 或 5.7 cm 见方（figstyle.grid），色标另出一个 PDF 放最右；行=源站，列=目标站（A–D）；对角线留空；单元格标两位小数；YlOrRd，共用色标（自动取全局范围，当前 0–8 pp）；子图题在各子图下；图内只有子图序号和轴标签，图名、图注、英文均不在图内。

图题与图注文本见 `figures/data-manifest.md`。

脚本运行后打印六组 mean/std/min/max，应与 csv 一致（2026-09-18 已核对）。

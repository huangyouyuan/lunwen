# F1 差值热力图

```
python scripts/plot_degradation_heatmap.py
```

输入：`results/summary/f1_raw_scale/crop_f1_difference_36paths.csv`（`corn_f1_difference`、`soybean_f1_difference`）
输出：`fig_degradation_heatmap_{a..f}.pdf`（每子图一个，LaTeX subcaption 拼）+ `fig_degradation_heatmap_cbar.pdf`；同名 PNG 只作预览

命令行参数 = 子图图框边长的 UNIT（3.8 cm）倍数：默认 `1` → 3.8 cm，正文按两行三列排布（上玉米、下大豆，列依次为 ConvGRU、3D U-Net、U-TAE）；`1.5` → 5.7 cm，当前正文未使用。

规格：每子图图框见方（figstyle.grid）；行=源站，列=目标站（A–D）；对角线留空；单元格标两位小数的原尺度 F1 差值；YlOrRd 共用色标，范围由数据自动取整到 0.01，当前为 0.00–0.08；色标单独出一个 PDF，宽 2 UNIT（7.6 cm）横向排在两排子图下方，色标文字“F1差值”由 LaTeX 排版，不附百分号或百分点。内部网格与外框统一为黑色 0.6 pt，只绘制一次，外框不裁切。子图题在各子图下；图内只有数值、刻度和轴标签，图名、图注、英文均不在图内。

数值为同模型目标站站内汇总 F1 减跨站五次均值；显示 0.00 不表示真实差值为零。脚本按正差值设计，若数据出现负值会报错并要求重新审查色标。

图题与图注文本见 `figures/data-manifest.md`。

脚本运行后打印六组 mean/std/min/max，应与输入 CSV 一致（2026-10-01 已核对）。

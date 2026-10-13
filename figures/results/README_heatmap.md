# F1 差值热力图

```
python scripts/plot_degradation_heatmap.py
```

输入：`results/summary/f1_raw_scale/crop_f1_difference_36paths.csv`（`corn_f1_difference`、`soybean_f1_difference`）
输出：`fig_degradation_heatmap_{a..f}.pdf`（每子图一个，LaTeX subcaption 拼）+ `fig_degradation_heatmap_cbar.pdf`；同名 PNG 只作预览

命令行参数 = 子图图框边长的 UNIT（3.8 cm）倍数：默认 `1` → 3.8 cm，正文按两行三列排布（上玉米、下大豆，列依次为 ConvGRU、3D U-Net、U-TAE）；`1.5` → 5.7 cm，当前正文未使用。

规格：每子图图框见方（figstyle.grid）；行=源站，列=目标站（A–D）；对角线留空。输入保留完整精度原尺度，绘图时乘100；单元格标两位小数的百分点差值。六幅子图共用相同色标，当前YlOrRd范围为0.00～8.00个百分点（原0.00～0.08等比例转换），刻度为0.00、2.00、4.00、6.00、8.00。色标单独出一个PDF，宽2 UNIT（7.6 cm），文字“F1下降（百分点）”由LaTeX排版。内部网格与外框统一为黑色0.6 pt，只绘制一次，外框不裁切。子图题在各子图下；图内只有数值、刻度和轴标签，图名、图注不画入图片。字体为9 pt宋体/Times New Roman。

数值为同模型目标站站内汇总F1减跨站五次均值，不除以基准，不从显示值反算。保留正负值；若今后输入有负值，所有子图一起切换为以0为中心的共同发散色标，不截断负值，不分别拉伸颜色范围。仅将舍入产生的−0.00写为0.00。

本站图由`plot_within_site_f1.py`绘制五折汇总F1（%），不把折间标准差当作汇总F1的误差线。当前正式稿没有F1误差线。跨站表由`generate_core_tables.py`将已有均值与样本标准差同步乘100，显示“均值±标准差”；格式函数共用`f1_display.py`。正文数值由同一表生成器写入`tables/f1_text_values.tex`；计算仍读取正式summary，展示CSV不得作为计算输入。

图题与图注文本见 `figures/data-manifest.md`。

脚本运行后打印六组 mean/std/min/max，应与输入 CSV 一致（2026-10-01 已核对）。

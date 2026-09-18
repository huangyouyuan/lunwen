# 图表生成说明

## 图X：玉米/大豆泛化退化热力图

### 快速运行

```bash
cd D:\AI\lunwen
python scripts/plot_degradation_heatmap.py
```

### 输出文件

- `figures/results/fig_degradation_heatmap.png`（300 dpi，用于正文）
- `figures/results/fig_degradation_heatmap.pdf`（矢量版本，用于最终投稿）

### 图表规格

**布局**：
- 2行×3列，共6个子图
- 第1行：玉米（ConvGRU、3D U-Net、U-TAE）
- 第2行：大豆（ConvGRU、3D U-Net、U-TAE）
- 子图标号：(a)~(f)

**每个子图**：
- 4×4热力图
- 行=源站（A/B/C/D）
- 列=目标站（A/B/C/D）
- 对角线留空（NaN，显示为空白）
- 数值标注：保留2位小数
- 色标：YlOrRd（浅色=小退化，深色=大退化）

**全局色标**：
- 六个子图共用同一色标
- 范围由数据自动确定（全局最小值→全局最大值）

**标题与图注**：
- 总标题："图X 不同源—目标区域组合下三种模型的玉米和大豆F1泛化退化"
- 每个子图标题：如"(a) ConvGRU玉米泛化退化"
- 底部图注："注：行为源站，列为目标站；数值为目标站站内OOF F1减去跨站平均F1，单位为百分点（pp）；对角线不适用。六个子图共用同一色标。"

### 数据来源

- **输入文件**：`results/summary/crop_f1_degradation_36paths.csv`
- **关键字段**：
  - `model`：convgru / unet3d / utae
  - `source`：iw_2023 / iw2_2023 / ida_2023 / il_2023
  - `target`：iw_2023 / iw2_2023 / ida_2023 / il_2023
  - `corn_loss_pp`：玉米泛化退化（百分点）
  - `soybean_loss_pp`：大豆泛化退化（百分点）

### 关键发现（将体现在图中）

1. **玉米泛化较稳定**：退化范围约 0~6 pp
2. **大豆泛化不稳定**：出现负退化（ConvGRU），方差较大
3. **共同困难路径**：D→B 在两类作物上均最困难
4. **模型差异**：ConvGRU 大豆出现异常负退化

### 与论文正文对应

- **对应章节**：3.3.1 源—目标区域组合差异
- **对应表格**：表2（跨站分类性能汇总）
- **分析重点**：方向不对称性（A→B vs B→A），困难路径识别

### 如果遇到中文显示问题

脚本已配置三个备选字体：
1. SimHei（黑体）
2. Microsoft YaHei（微软雅黑）
3. Arial Unicode MS（跨平台）

如果中文仍显示为方框，可手动修改脚本第18行：
```python
plt.rcParams['font.sans-serif'] = ['你的系统字体名称']
```

### 验证输出

运行成功后，脚本会输出：
- 已保存文件路径
- 全局退化范围（vmin ~ vmax）
- 各模型-作物组合的统计摘要（mean, std, min, max）

检查输出的统计数据是否与以下一致：
- ConvGRU玉米：mean≈2.79, std≈1.55
- ConvGRU大豆：mean≈-3.25, std≈5.35（注意负值）
- 3D U-Net玉米：mean≈3.93, std≈0.96
- U-TAE玉米：mean≈3.97, std≈0.92
- U-TAE大豆：mean≈0.04, std≈2.19

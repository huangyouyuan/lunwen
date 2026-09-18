# Figures Data Manifest

每张科研图的数据映射。

| Figure | Purpose | Source data | Generation method | Script | Status |
|--------|---------|-------------|-------------------|--------|--------|
| 图 1 | 研究区 4 站点分布图 | 站点坐标 + 底图 | 待确认（GIS/Python） | — | 旧稿已有，待提取 |
| 图 2 | 地物组成统计 | CDL 2023 统计 | 待确认 | — | 旧稿已有，待提取 |
| 图 4 | U-TAE 模型结构示意图 | 模型架构 | 手绘/绘图工具 | — | 旧稿已有，待提取 |
| 图 5 | L-TAE 时序注意力模块 | 模型架构 | 手绘/绘图工具 | — | 旧稿已有，待提取 |
| 图 6 | 3D U-Net 结构示意图 | 模型架构 | 手绘/绘图工具 | — | 旧稿已有，待提取 |
| 图 7 | ConvGRU 门控循环单元 | 模型架构 | 手绘/绘图工具 | — | 旧稿已有，待提取 |
| 图 8 | 实验流程图 | 实验设计 | 手绘/绘图工具 | — | 旧稿已有，待提取 |
| 图 9 | ConvGRU 分类结果空间分布 | 预测结果栅格 | Python/GIS | — | 旧稿已有，待提取 |

## 新建图（已完成）

| Figure | Purpose | Source data | Generation method | Script | Status |
|--------|---------|-------------|-------------------|--------|--------|
| fig_transfer_heatmaps.png | 跨站点 Crop-mIoU 热力图（3个模型） | results/summary/generalization_degradation_36paths.csv | Python (seaborn heatmap) | scripts/plot_heatmaps.py | ✓ 已生成 |
| fig_degradation_heatmaps.png | 泛化退化热力图（3个模型，对角线留空） | results/summary/generalization_degradation_36paths.csv | Python (seaborn heatmap, YlOrRd, 0-10 pp) | scripts/plot_heatmaps.py | ✓ 已生成 |
| 图X 玉米/大豆泛化退化热力图 | 6子图：三模型×两作物的跨站泛化退化 | results/summary/crop_f1_degradation_36paths.csv | Python (matplotlib+seaborn, 2行3列，共用色标) | scripts/plot_degradation_heatmap.py | 脚本已就绪 |

**fig_degradation_heatmaps.png 说明**（旧版，基于Crop-mIoU）：
- 行：源站（A/B/C/D）
- 列：目标站（A/B/C/D）
- 数值：泛化退化 ΔCrop-mIoU (pp) = 100 × (站内OOF - 跨站平均)
- 对角线留空（无意义）
- 色标：0-10 pp，YlOrRd（越深表示退化越严重）
- 三个子图共享统一色标

**图X 玉米/大豆泛化退化热力图说明**（新版，基于类别F1）：
- 布局：2行（玉米/大豆）× 3列（ConvGRU/3D U-Net/U-TAE）
- 每个子图：4×4热力图，行=源站，列=目标站，对角线留空
- 数值：泛化退化 (pp) = 100 × (站内OOF F1 - 跨站平均F1)
- 子图标号：(a)~(f)，从左到右、从上到下编号
- 六个子图共用同一色标（YlOrRd）
- 图题："图X 不同源—目标区域组合下三种模型的玉米和大豆F1泛化退化"
- 图注：行为源站，列为目标站；数值单位为百分点（pp）；对角线不适用

## 待新建图

- 距离-边界精度曲线
- 模型对比雷达图（如需要）

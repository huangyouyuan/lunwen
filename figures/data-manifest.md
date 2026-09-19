# Figures Data Manifest

| Figure | Purpose | Source data | Generation | Script | Status |
|--------|---------|-------------|------------|--------|--------|
| 研究区分布图 | 4 站点位置 | 旧稿 `word/media/image1.jpeg` | 从旧 Word 提取 | — | 已提取 `figures/study_area/study_area.jpg`，已插入 1.1 |
| 地物组成 | CDL 2023 各站占比 | CDL 统计 | 待确认 | — | 旧稿已有，待提取或重绘 |
| 模型结构图 ×3、L-TAE 模块、实验流程图 | 方法章节 | — | 旧稿 emf | — | 待提取（emf 需转换） |
| 站内玉米/大豆 F1 分组柱状图 | 3.1 | `results/summary/within_site_crop_f1.csv` | matplotlib；1×2 子图 (a) 玉米 (b) 大豆，sharey；横轴 A–D，每站 ConvGRU/3D U-Net/U-TAE 三柱；纵轴 F1（%）80–100；柱顶标两位小数；顶部共用图例；图内无图名 | `scripts/plot_within_site_f1.py` | 已生成 `figures/results/fig_within_site_f1.png` / `.pdf`；已插入 04_results.tex 3.1（2026-09-19） |
| 玉米/大豆泛化退化热力图 | 3.3.1 | `results/summary/crop_f1_degradation_36paths.csv` | matplotlib+seaborn；2 行（玉米/大豆）× 3 列（ConvGRU/3D U-Net/U-TAE）；行=源站，列=目标站；对角线留空；单元格标数值；YlOrRd，共用色标 0–8 pp；图内无图名、图注、英文 | `scripts/plot_degradation_heatmap.py` | 已生成 `figures/results/fig_degradation_heatmap.png` / `.pdf`；脚本输出统计与 csv 一致（2026-09-18） |

## 站内 F1 柱状图图题（已写入 04_results.tex caption）

三种模型在四个站点的站内玉米和大豆分类精度。（a）玉米F1；（b）大豆F1

## 热力图图题（写在正文 caption，小五号宋体）

图 X 不同源—目标区域组合下三种模型的玉米和大豆 F1 泛化退化

注：行为源站，列为目标站；数值为目标站站内 OOF F1 减去跨站平均 F1，单位为百分点（pp）；对角线不适用；六个子图共用同一色标。子图 (a)–(f) 依次为 ConvGRU 玉米、3D U-Net 玉米、U-TAE 玉米、ConvGRU 大豆、3D U-Net 大豆、U-TAE 大豆。

## 已删除

`fig_transfer_heatmaps.png`、`fig_degradation_heatmaps.png`、`fig_model_comparison_cropmIoU.png`、`fig_degradation_boxplot.png`、`fig_asymmetry_scatter.png`——Crop-mIoU 体系，2026-09-18 删除；对应脚本 `plot_heatmaps.py`、`plot_generalization_figures.py` 于 2026-09-19 删除。

## 待新建

3.3.2 空间特征与退化的关系图，待数据。

# Figures Data Manifest

| Figure | Purpose | Source data | Generation | Script | Status |
|--------|---------|-------------|------------|--------|--------|
| 研究区分布图 | 4 站点位置 | 旧稿 `word/media/image1.jpeg` | 从旧 Word 提取 | — | 已提取 `figures/study_area/study_area.jpg`，已插入 1.1 |
| 地物组成 | CDL 2023 各站占比 | CDL 统计 | 待确认 | — | 旧稿已有，待提取或重绘 |
| 模型结构图 ×3、L-TAE 模块、实验流程图 | 方法章节 | — | 旧稿 emf | — | 待提取（emf 需转换） |
| 站内玉米/大豆 F1 条形图 | 3.1 | `results/summary/within_site_crop_f1.csv` | matplotlib；两子图各一个 PDF，图框各 7.6×5.7 cm（2×1.5 UNIT），LaTeX subcaption 上下拼；(a) 四站点玉米分类精度 (b) 四站点大豆分类精度；横向条形：纵轴"站点"A–D，每站 ConvGRU/3D U-Net/U-TAE 三条，横轴 F1/% 88–98.5；条末端标两位小数（每条一行）；子图题、图例（`\modellegend`，最后子图题之后、图名之前）、图名为 LaTeX 文本，宋体+Times 小五 | `scripts/plot_within_site_f1.py` | 已生成 `fig_within_site_f1_{a,b}.pdf/.png`；已插入 04_results.tex 3.1；2026-09-20 改横向条形、逐子图 PDF |
| D 站三模型站内分类结果对比 | 3.1 | `D:/20il/2023{model}ilresults/summary/maps/reference.tif`、`oof_prediction.tif`（五折交叉验证拼接，每图块预测来自未训练过它的模型；三模型 reference sha256 一致） | matplotlib；8 个子图各一个 PDF，图框各 3.8×3.8 cm，LaTeX subcaption 拼通栏 `figure*` 2 行 4 列；上行 (a)–(d) 全站 2560×2560 各标同一红框，下行 (e)–(h) 红框窗口放大；同一配色（玉米黄/大豆绿/其它灰）；子图题、图例（`\classlegend`，最后子图题之后）、图名为 LaTeX 文本。窗口 = 图块网格 (13,8) 起 2×2，像元行 1664–1920、列 1024–1280；选窗只看真实玉米/大豆像元：作物像元错误率 12.1/5.8/4.8%，类别边界带错误率 32.0/15.3/13.4%，玉米↔大豆互混 6.8/2.6/2.2%（ConvGRU/3D U-Net/U-TAE） | `scripts/plot_within_site_map_D.py` | 已生成 `fig_within_site_map_D_{a..h}.pdf/.png`；已插入 04_results.tex 3.1 第二段后（2026-09-20 换窗、逐子图 PDF） |
| 玉米/大豆泛化退化热力图 | 3.3.1 | `results/summary/crop_f1_degradation_36paths.csv` | matplotlib+seaborn；6 个子图各一个 PDF + 色标 PDF，LaTeX subcaption 拼；子图边长为脚本参数（1 → 3.8 cm 排 2×3；1.5 → 5.7 cm 排 3×2，**排法待用户定**，tex 当前为 3×2）；行=源站，列=目标站，轴标签"源站""目标站"；对角线留空；单元格标两位小数；YlOrRd 共用色标 0–8 pp 放最右；子图题、图名为 LaTeX 文本 | `scripts/plot_degradation_heatmap.py` | 已生成 `fig_degradation_heatmap_{a..f,cbar}.pdf/.png`（5.7 cm 版）；已插入 04_results.tex 3.3.1；脚本输出统计与 csv 一致（2026-09-18） |

## 3.1 图题（已写入 04_results.tex caption）

- 三种模型在四个站点的站内玉米和大豆分类精度
- D站点三种模型站内交叉验证分类结果的局部对比

## 图内规范（2026-09-19 用户要求）

- 子图题、图例放图**下方**；图名只在 caption，也在图下方（表名才在上方）
- 双子图上下排列，占单栏宽
- 子图题写全：如"（a）四站点玉米分类精度"，不写"（a）玉米"

## 热力图图题（写在正文 caption，小五号宋体）

图 X 不同源—目标区域组合下三种模型的玉米和大豆 F1 泛化退化

注：行为源站，列为目标站；数值为目标站站内 OOF F1 减去跨站平均 F1，单位为百分点（pp）；对角线不适用；六个子图共用同一色标。子图 (a)–(f) 依次为 ConvGRU 玉米、3D U-Net 玉米、U-TAE 玉米、ConvGRU 大豆、3D U-Net 大豆、U-TAE 大豆。

## 已删除

`fig_transfer_heatmaps.png`、`fig_degradation_heatmaps.png`、`fig_model_comparison_cropmIoU.png`、`fig_degradation_boxplot.png`、`fig_asymmetry_scatter.png`——Crop-mIoU 体系，2026-09-18 删除；对应脚本 `plot_heatmaps.py`、`plot_generalization_figures.py` 于 2026-09-19 删除。

## 待新建

3.3.2 空间特征与退化的关系图，待数据。

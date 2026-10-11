# Figures Data Manifest

| Figure | Purpose | Source data | Generation | Script | Status |
|--------|---------|-------------|------------|--------|--------|
| 研究区分布图 | 4 站点位置 | 旧稿 `word/media/image1.jpeg` | 从旧 Word 提取 | — | 已提取 `figures/study_area/study_area.jpg`，已插入 1.1 |
| 地物组成 | 1.3 四站三类面积占比 | `results/summary/sec13_sec31_foundations/reference_composition.csv`；2023 年整站分母 | 旧 Word 三类分组柱形图的排布；单栏横排，图框 7.6×5.7 cm，字体 9 pt | `scripts/generate_sec13_figure_table.py`（历史图件生成入口） | 组成图 `figures/study_area/fig_sec13_composition.pdf/.png` 沿用并保留在 1.3；既有数据与图件核查见 `verification/sec13-figure-table-v2-2026-10-11.json` |
| 斑块级、类别级与景观级整表 | 1.3 四站三类地物 AREA、SHAPE、PD、AI 与整站 ED | `results/processed/sec33_reference_patch_types/reference_patch_features.csv`；`results/summary/sec13_sec31_foundations/crop_patch_distribution_reading.csv`（仅两作物已有分布汇总）、`class_background_full_scope.csv`、`landscape_background_full_scope.csv` | 12行、通栏三线表；AREA和SHAPE为斑块等权中位数（最小值～最大值），“其它地类”从逐斑块底表派生；ED跨同站三类合并 | `scripts/generate_sec13_spatial_tables.py` | 当前正文引用 `tables/sec13_spatial_metrics_rows.tex`；三类底表与排版核查见 `verification/sec13-spatial-tables-2026-10-11.md` |
| 分立的斑块级与类别级／景观级表（历史） | 1.3上一版两表排布 | 同上 | AREA、SHAPE最小值／中位数／最大值分列；PD、AI、ED另表 | `scripts/generate_sec13_spatial_tables.py`（上一版生成） | `tables/sec13_patch_extrema_rows.tex`与`tables/sec13_landscape_metrics_rows.tex`原位保留，不再由当前正文引用；上一版8页PDF的第2至4页预览见下文 |
| 双权重斑块分布表（历史） | 1.3上一版 AREA、SHAPE 中位数（Q25～Q75） | `results/summary/sec13_sec31_foundations/crop_patch_distribution_reading.csv` | 斑块等权与参考像元面积加权并列 | `scripts/generate_sec13_figure_table.py --table-only`（历史入口） | `tables/sec13_patch_distribution_rows.tex` 原位保留，不再由当前1.3引用；旧核查见 `verification/sec13-figure-table-v2-2026-10-11.md` |
| 模型结构图 ×3、L-TAE 模块、实验流程图 | 方法章节 | — | 旧稿 emf | — | 待提取（emf 需转换） |
| 站内玉米/大豆 F1 条形图 | 3.1 | `results/summary/f1_raw_scale/within_site_crop_f1.csv` | matplotlib；两子图各一个 PDF，图框各 7.6×5.7 cm（2×1.5 UNIT），LaTeX subcaption 上下拼；(a) 四站点玉米分类精度 (b) 四站点大豆分类精度；横向条形：纵轴"站点"A–D，每站 ConvGRU/3D U-Net/U-TAE 三条，横轴“玉米 F1”或“大豆 F1”，原尺度 0.88–0.985；条末端标两位小数（每条一行）；子图题、图例（`\modellegend`，最后子图题之后、图名之前）、图名为 LaTeX 文本，宋体+Times 小五 | `scripts/plot_within_site_f1.py` | 已生成 `fig_within_site_f1_{a,b}.pdf/.png`；已插入 04_results.tex 3.1；2026-09-20 改横向条形、逐子图 PDF |
| D 站三模型站内分类结果对比 | 3.1 | `D:/20il/2023{model}ilresults/summary/maps/reference.tif`、`oof_prediction.tif`（五折交叉验证拼接，每图块预测来自未训练过它的模型；三模型 reference sha256 一致） | matplotlib；8 个子图各一个 PDF，图框各 3.8×3.8 cm，LaTeX subcaption 拼通栏 `figure*` 2 行 4 列；上行 (a)–(d) 全站 2560×2560 各标同一红框，下行 (e)–(h) 红框窗口放大；同一配色（玉米黄/大豆绿/其它地类为灰色）；子图题、图例（`\classlegend`，最后子图题之后）、图名为 LaTeX 文本。窗口 = 图块网格 (13,8) 起 2×2，像元行 1664–1920、列 1024–1280；选窗只看真实玉米/大豆像元：作物像元错误率 12.1/5.8/4.8%，类别边界带错误率 32.0/15.3/13.4%，玉米↔大豆互混 6.8/2.6/2.2%（ConvGRU/3D U-Net/U-TAE） | `scripts/plot_within_site_map_D.py` | 已生成 `fig_within_site_map_D_{a..h}.pdf/.png`；已插入 04_results.tex 3.1 第二段后（2026-09-20 换窗、逐子图 PDF） |
| 玉米/大豆 F1 差值热力图 | 3.2 | `results/summary/f1_raw_scale/crop_f1_difference_36paths.csv` | matplotlib+seaborn；6 个子图各一个 PDF + 色标 PDF，LaTeX subcaption 拼两行三列，上玉米、下大豆，列依次为 ConvGRU、3D U-Net、U-TAE；图框各 3.8×3.8 cm（1 UNIT）；行=源站，列=目标站，轴标签"源站""目标站"；对角线留空；单元格标两位小数，内外网格均为黑色 0.6 pt；YlOrRd 共用横向色标 0.00–0.08，宽 7.6 cm（2 UNIT），放在两排子图下方；子图题、色标文字“F1差值”、图名均为 LaTeX 文本，间距 3 pt | `scripts/calculate_f1_raw_scale.py` → `scripts/plot_degradation_heatmap.py 1` | 已生成 `fig_degradation_heatmap_{a..f,cbar}.pdf/.png`（3.8 cm 版），已插入 04_results.tex 3.2（2026-09-23） |

`output/preview-manifest.json`对应7页双权重分布表历史版本。`output/sec13-current-20261011-2.png`至`-4.png`对应随后8页双表版本，`output/sec13-combined-20261011-2.png`及`-3.png`对应8行整表历史版本；12行整表的旧预览为`output/sec13-threeclass-20261011-3.png`，本次图表顺序调整后的第2、3页预览为`output/sec13-layout-inline-2.png`和`-3.png`，核查见`verification/sec13-spatial-tables-2026-10-11.md`。

## 3.1 图题（已写入 04_results.tex caption）

- 三种模型在四个站点的站内玉米和大豆分类精度
- D站点三种模型站内交叉验证分类结果的局部对比

## 图内规范（2026-09-19 用户要求）

- 子图题、图例放图**下方**；图名只在 caption，也在图下方（表名才在上方）
- 双子图上下排列，占单栏宽
- 子图题写全：如"（a）四站点玉米分类精度"，不写"（a）玉米"

## 热力图图题（写在正文 caption，小五号宋体）

图 4 不同源—目标区域组合下三种模型的玉米和大豆 F1 差值

注：行为源站，列为目标站；数值为同模型目标站站内汇总 F1 − 跨站 F1 五次均值，不乘 100、不除基准；对角线不适用；六个子图共用同一色标。显示两位小数，0.00 不表示真实差值严格为零。子图 (a)–(f) 依次为 ConvGRU 玉米、3D U-Net 玉米、U-TAE 玉米、ConvGRU 大豆、3D U-Net 大豆、U-TAE 大豆。

2026-10-01—02：图 2、图 4 已在主干按新数据重绘，随后按用户要求编译为 6 页 PDF；第 2—5 页 PNG 及表图预览副本已更新，当前绑定见 `output/preview-manifest.json`。

## 已删除

`fig_transfer_heatmaps.png`、`fig_degradation_heatmaps.png`、`fig_model_comparison_cropmIoU.png`、`fig_degradation_boxplot.png`、`fig_asymmetry_scatter.png`——Crop-mIoU 体系，2026-09-18 删除；对应脚本 `plot_heatmaps.py`、`plot_generalization_figures.py` 于 2026-09-19 删除。

## 待新建

3.3 空间特征与退化的关系图，待数据。

# Figures Data Manifest

2026-10-12后续样式统一：图2与图3两个子图的条形厚度均为3.705 mm，组内、组间距及浅灰虚线网格一致；图框保持7.6×5.7 cm，文字仍为小五9 pt。已重绘、编译并查看第3、5页，见[样式核查](../verification/figure23-bars-2026-10-12.md)。此前图件和生成源码已保留在`output/archive/2026-10-12/source-backups/figure23-bars-20261012-before/`，下面字体记录对应本次重绘前的PDF。

2026-10-12：当前正文5幅图、2张表的字体已逐项核查，源图及正文PDF中的文字均为小五9 pt宋体与Times New Roman；表2的数学箭头已统一为Times New Roman文本箭头。图件未重新生成，见[字体核查](../verification/figure-table-fonts-2026-10-12.md)。本次核查PDF为8页、表1在第4页；下方7页、表1在第3页的描述对应上一轮通栏排版预览。

| Figure | Purpose | Source data | Generation | Script | Status |
|--------|---------|-------------|------------|--------|--------|
| 四站地物分类图 | 1.1 四站地物分布；正文用中心经纬度定位 | `legacy/figures/four_site_classification/four_site_maize_soybean.png`、`site_coordinates.csv`；源图及站点身份核查见同目录 `verification.json` | 从已核验拼图无损裁出四个完整分类面板，在1.1尾部按单栏两行两列排版；图例按源图配色，子图排列不代表地理方位 | `scripts/prepare_study_area_classification.py` | 当前正文图1引用 `figures/study_area/fig_study_area_{A,B,C,D}.png`；原拼图与坐标说明原位保留 |
| 旧研究区分布图（历史） | 旧稿四站行政区位置示意 | 旧稿 `word/media/image1.jpeg` | 从旧 Word 提取 | — | `figures/study_area/study_area.jpg`原位保留，不再由正文引用 |
| 地物组成 | 1.3 四站三类面积占比 | `results/summary/sec13_sec31_foundations/reference_composition.csv`；2023 年整站分母 | 单栏横排，图框7.6×5.7 cm，字体9 pt；与图3共用条形厚度、间距和虚线网格 | `scripts/plot_sec13_composition.py`（当前图件入口，不写历史斑块表） | 当前`figures/study_area/fig_sec13_composition.pdf/.png`；2026-10-12重绘及核查见上方样式记录；旧生成器`scripts/generate_sec13_figure_table.py`及其历史成果保留 |
| 斑块级、类别级与景观级整表 | 1.3.2 四站玉米、大豆的斑块数、AREA、SHAPE、ENN、PD、AI及整站ED | `results/processed/sec33_reference_patch_types/reference_patch_features.csv`；`results/summary/sec13_sec31_foundations/`的组成、分布、支持及整站背景表；`results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv` | 8行9列、双栏通栏三线表，铺满17.4 cm版心；小五号9 pt宋体与Times New Roman，均匀分配剩余列宽、行距系数1.2，PD/ED指标及单位同行；AREA、SHAPE为参考像元面积加权中位数，ENN为斑块等权中位数，均附全体最小值～最大值；斑块数归入斑块级表头，PD/AI为类别级，ED跨同站两作物行合并且覆盖三类 | `scripts/generate_sec13_spatial_tables.py` | 正文引用 `tables/sec13_spatial_metrics_enn_equal_rows.tex`；口径及后续排版核查见 `verification/sec13-enn-patch-equal-2026-10-12.md`，实测版宽见 `verification/sec13-fullwidth-layout-2026-10-12.json`。当前稿件7页、表1在第3页；三条主横线均为17.4 cm，无溢出，字体9 pt；旧14.84 cm窄表预览保留为历史 |
| ENN面积加权整表（历史） | 1.3.2上一版三指标均面积加权 | 同上，ENN使用`weighting=reference_pixel_area` | 8行9列；曾使用9 pt及10.5 pt两次预览，后按作者最新决定将ENN改为等权并统一9 pt | `scripts/generate_sec13_spatial_tables.py`的历史版本 | `tables/sec13_spatial_metrics_enn_rows.tex`原位保留，不再由正文引用或当前脚本写入；核查见 `verification/sec13-spatial-enn-2026-10-12.md`，放大前快照在 `output/sec13-enn-20261012-before-large/` |
| 未含斑块数与ENN的整表（历史） | 1.3上一版 AREA、SHAPE、PD、AI 与整站ED | 同上基础目录，不使用ENN | 8行7列、通栏三线表；AREA和SHAPE为面积加权中位数（全体斑块最小值～最大值） | `scripts/generate_sec13_spatial_tables.py`的历史版本 | `tables/sec13_spatial_metrics_rows.tex`原位保留，不再由正文引用或当前脚本写入；历史核查见 `verification/sec13-spatial-tables-2026-10-11.md` |
| 分立的斑块级与类别级／景观级表（历史） | 1.3上一版两表排布 | 同上 | AREA、SHAPE最小值／中位数／最大值分列；PD、AI、ED另表 | `scripts/generate_sec13_spatial_tables.py`（上一版生成） | `tables/sec13_patch_extrema_rows.tex`与`tables/sec13_landscape_metrics_rows.tex`原位保留，不再由当前正文引用；上一版8页PDF的第2至4页预览见下文 |
| 双权重斑块分布表（历史） | 1.3上一版 AREA、SHAPE 中位数（Q25～Q75） | `results/summary/sec13_sec31_foundations/crop_patch_distribution_reading.csv` | 斑块等权与参考像元面积加权并列 | `scripts/generate_sec13_figure_table.py --table-only`（历史入口） | `tables/sec13_patch_distribution_rows.tex` 原位保留，不再由当前1.3引用；旧核查见 `verification/sec13-figure-table-v2-2026-10-11.md` |
| 模型结构图 ×3、L-TAE 模块、实验流程图 | 方法章节 | — | 旧稿 emf | — | 待提取（emf 需转换） |
| 站内玉米/大豆 F1 条形图 | 3.1 | `results/summary/f1_raw_scale/within_site_crop_f1.csv` | matplotlib；两子图各一个 PDF，图框各 7.6×5.7 cm（2×1.5 UNIT），LaTeX subcaption 上下拼；(a) 四站点玉米分类精度 (b) 四站点大豆分类精度；横向条形：纵轴"站点"A–D，每站 ConvGRU/3D U-Net/U-TAE 三条，横轴“玉米 F1”或“大豆 F1”，原尺度 0.88–0.985；条末端标两位小数（每条一行）；子图题、图例（`\modellegend`，最后子图题之后、图名之前）、图名为 LaTeX 文本，宋体+Times 小五 | `scripts/plot_within_site_f1.py` | 已生成 `fig_within_site_f1_{a,b}.pdf/.png`；已插入 04_results.tex 3.1；2026-09-20 改横向条形、逐子图 PDF |
| D 站三模型站内分类结果对比 | 3.1 | `D:/20il/2023{model}ilresults/summary/maps/reference.tif`、`oof_prediction.tif`（五折交叉验证拼接，每图块预测来自未训练过它的模型；三模型 reference sha256 一致） | matplotlib；8 个子图各一个 PDF，图框各 3.8×3.8 cm，LaTeX subcaption 拼通栏 `figure*` 2 行 4 列；上行 (a)–(d) 全站 2560×2560 各标同一红框，下行 (e)–(h) 红框窗口放大；同一配色（玉米黄/大豆绿/其它地类为灰色）；子图题、图例（`\classlegend`，最后子图题之后）、图名为 LaTeX 文本。窗口 = 图块网格 (13,8) 起 2×2，像元行 1664–1920、列 1024–1280；选窗只看真实玉米/大豆像元：作物像元错误率 12.1/5.8/4.8%，类别边界带错误率 32.0/15.3/13.4%，玉米↔大豆互混 6.8/2.6/2.2%（ConvGRU/3D U-Net/U-TAE） | `scripts/plot_within_site_map_D.py` | 已生成 `fig_within_site_map_D_{a..h}.pdf/.png`；已插入 04_results.tex 3.1 第二段后（2026-09-20 换窗、逐子图 PDF） |
| 玉米/大豆 F1 差值热力图 | 3.2 | `results/summary/f1_raw_scale/crop_f1_difference_36paths.csv` | matplotlib+seaborn；6 个子图各一个 PDF + 色标 PDF，LaTeX subcaption 拼两行三列，上玉米、下大豆，列依次为 ConvGRU、3D U-Net、U-TAE；图框各 3.8×3.8 cm（1 UNIT）；行=源站，列=目标站，轴标签"源站""目标站"；对角线留空；单元格标两位小数，内外网格均为黑色 0.6 pt；YlOrRd 共用横向色标 0.00–0.08，宽 7.6 cm（2 UNIT），放在两排子图下方；子图题、色标文字“F1差值”、图名均为 LaTeX 文本，间距 3 pt | `scripts/calculate_f1_raw_scale.py` → `scripts/plot_degradation_heatmap.py 1` | 已生成 `fig_degradation_heatmap_{a..f,cbar}.pdf/.png`（3.8 cm 版），已插入 04_results.tex 3.2（2026-09-23） |

`output/archive/2026-10-12/preview-index/preview-manifest.json`对应7页双权重分布表历史版本。`output/archive/2026-10-12/sec13-layout/sec13-current-20261011-2.png`至`-4.png`对应随后8页双表版本，`output/archive/2026-10-12/sec13-layout/sec13-combined-20261011-2.png`及`-3.png`对应8行整表历史版本；12行整表的旧预览为`output/archive/2026-10-12/sec13-layout/sec13-threeclass-20261011-3.png`，图表顺序调整后的旧第2、3页预览为`output/archive/2026-10-12/sec13-layout/sec13-layout-inline-2.png`和`-3.png`，含其它地类的面积加权预览为`output/archive/2026-10-12/sec13-layout/sec13-weighted-20261011-2.png`和`-3.png`。未含斑块数与ENN的双作物面积加权版预览为`output/archive/2026-10-12/sec13-layout/sec13-dualcrop-clearpage-2.png`和`-3.png`，历史核查见`verification/sec13-spatial-tables-2026-10-11.md`；2026-10-12新版无编译预览。

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

2026-10-01—02：图 2、图 4 已在主干按新数据重绘，随后按用户要求编译为 6 页 PDF；第 2—5 页 PNG 及表图预览副本已更新，当前绑定见 `output/archive/2026-10-12/preview-index/preview-manifest.json`。

## 已删除

`fig_transfer_heatmaps.png`、`fig_degradation_heatmaps.png`、`fig_model_comparison_cropmIoU.png`、`fig_degradation_boxplot.png`、`fig_asymmetry_scatter.png`——Crop-mIoU 体系，2026-09-18 删除；对应脚本 `plot_heatmaps.py`、`plot_generalization_figures.py` 于 2026-09-19 删除。

## 待新建

3.3 空间特征与退化的关系图，待数据。

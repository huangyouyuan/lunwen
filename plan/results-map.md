# Results Map

论文小节 → 科学问题 → 数据 → 表 → 图。主线见 `plan/paper-context.md`：站内基准 → 跨站退化 → 空间解释，每节回答一个问题。表格文件名中的 table1/2/3 是工作编号，论文编号写作时按出现顺序分配。

## 3.1 模型站内分类性能

**问题**：三模型在拥有当地训练数据时能达到什么水平？玉米和大豆是否存在难度差异？训练是否稳定？

**数据**：
- `results/summary/f1_raw_scale/within_site_crop_f1.csv`（汇总口径玉米 F1 / 大豆 F1 / OA，12 组）
- `results/summary/f1_raw_scale/within_site_crop_f1_fold_stats.csv`（五折 mean±std；计算不按显示精度舍入）

**表**：`tables/table1_within_site_baseline.csv`、`tables/table1b_within_site_fold_stability.csv`（数据备查，正文用图不用表）

**图**：
- `figures/results/fig_within_site_f1_{a,b}.pdf`——两子图上下排横向条形图，图框各 7.6×5.7 cm，(a) 四站点玉米分类精度 (b) 四站点大豆分类精度；子图题、图例、图名为 LaTeX 文本
- `figures/results/fig_within_site_map_D_{a..h}.pdf`——D 站分类结果对比，通栏 2 行 4 列、图框各 3.8×3.8 cm：上行全站（红框）、下行局部放大，(a)/(e) 参考标签 (b)/(f) ConvGRU (c)/(g) 3D U-Net (d)/(h) U-TAE

**正文状态**：第 1、2 段已写（2026-09-19，用户草稿，数字全部核对）；图 2、图 3 已插入

**位置**：第一段 → 图 2 → 第二段 → 图 3；图 3 必须在 3.2 标题之前。图 2 随文排版，3.2 前用浮动体边界约束图 3。

**要点**：见 claims.md C1–C3

## 3.2 模型跨站分类性能与泛化退化

**问题**：跨站后玉米和大豆 F1 实际多高、相对目标站当地训练基准差多少？哪些模型和源—目标组合表现不同？

**数据**：
- `results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv`（36 个模型—路径组合，每组合 5 次预测的均值与标准差）
- `results/summary/f1_raw_scale/cross_site_crop_f1_per_fold.csv`（180 行，逐次追溯用）
- `results/summary/f1_raw_scale/crop_f1_difference_36paths.csv`（同模型目标站站内汇总 F1 减跨站五次均值，图 4 与正文数据；原尺度，两位显示）
- 旧 `crop_f1_relative_degradation_36paths.csv` 与 `crop_f1_degradation_36paths.csv` 保留历史追溯，不作为当前正文数据。

**正文表**：`tables/table2_cross_site_f1_12paths.csv`。12 行完整迁移路径、6 个模型—作物精度列，末行给出 12 条路径平均；每格为 5 次完整目标站预测的 F1 均值，不列退化值。

**分析备查**：`tables/table2_cross_site_summary.csv` 用于核对模型平均跨站 F1；`tables/table3_significance_tests.csv` 只供追溯，正文不作显著性结论（2026-09-27 作者决定）。二者均不排表。

**图**：`figures/results/fig_degradation_heatmap_{a..f}.pdf` + `_cbar.pdf`。两行三列，上排玉米、下排大豆，各列依次为 ConvGRU、3D U-Net、U-TAE；图框各 3.8×3.8 cm（1 UNIT），两排下方共用横向色标，LaTeX 标签“F1差值”，黑色内外网格统一 0.6 pt，YlOrRd 色标为 0.00～0.08。图示原尺度 F1 差值，用于比较源—目标组合差异及不同模型对迁移方向的响应，不据此判断区域组合与模型的影响主次。

**正文组织**（2026-09-29 收紧，保留三段，不用第三级标题）：
1. 跨站绝对 F1 范围，36 个组合全部低于同一模型目标站站内基准，A、C 站表现及与站内结果的对应（引表）；不据此推断分类难度，不声称差值消除了目标站差异 —— C4
2. 12 条路径平均，ConvGRU 跨站 F1 最低、平均差值最小；差值较小不代表跨站绝对精度更高。仅保留两类模型均值，不重复逐路径排名或站内外差距数字 —— C5、C6
3. 源—目标组合与模型间的退化差异（引图 4）：固定目标站 D 的 ConvGRU 大豆例子、B↔D 两模型方向不同的证据；明确五次预测均值口径，不推广为普遍规律，以一句话衔接空间分析 —— C7

**位置与核查**：源码顺序仍为 3.2 标题 → 第一段 → 表 → 第二、三段 → 图 4 → `\FloatBarrier` → 3.3。Verified（2026-10-01—02）：按用户要求编译，PDF 6 页，第 3 页站内结果、第 4 页分类图与 3.2、第 5 页完整表与热力图、第 6 页起 3.3；无 Overfull/Underfull。第 2—5 页预览已重建并与 PDF 绑定，见 `output/preview-manifest.json`。

**要点**：见 claims.md C4–C7。

## 3.3 模型跨站泛化差异的空间解释

**问题**：① 目标站在哪些空间条件下退化较大；② 同一目标站的退化随源站的变化与站点之间哪些差异相对应。覆盖全部站点和 12 条路径，不只围绕 C 站和 B、D 组合；只讲对应关系，不写因果机制。

**数据**（已生成，未入库）：
- 站点级：`D:/label/fragstats_results/完整标签景观级指标.csv`、`完整标签类别级指标.csv`（2023 年完整标签；ED、PD、AREA_MN、AI）
- 图块级：`D:/cross_site_all_20260916/paper_tables/Patch级空间误差底表/` 下 `patch_spatial_features.csv`、`within_patch_oof.csv`、`cross_patch_fold.csv`、`cross_patch_summary.csv`

**方法**：按空间特征分组后汇总混淆矩阵再算类别 F1；跨站逐次计算后汇总 5 次结果，站内以同组图块为参照；不平均图块 F1，不把错误率变化当作 F1 退化。

**主要证据**：地物占比、ED、AREA_MN、AI 等景观指标，以及按空间特征分组后由汇总混淆矩阵计算的分类结果。表图设计待数据验证后确定。

**正文组织**：不用第三级标题。先给空间条件与退化的总体对应关系，再比较模型和作物差异。

**要点**：见 claims.md C8（未验证）。

## 分析备查（不进入正文；本文不设补充材料）

Crop-mIoU 体系：`results/summary/generalization_degradation_36paths.csv`、`within_site_oof_baseline.csv`、`model_significance_analysis.csv`、`results/processed/generalization_analysis.csv`。

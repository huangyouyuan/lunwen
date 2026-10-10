# Results Map

论文小节 → 科学问题 → 数据 → 表 → 图。主线见 `plan/paper-context.md`：研究区空间背景 → 站内基准 → 跨站退化 → 空间解释，每节回答一个问题。总体安排见 [outline.md](outline.md)。表格文件名中的 table1/2/3 是工作编号，论文编号写作时按出现顺序分配。

## 1.3 研究区空间特征

**问题**：四站三类组成及两作物完整参考斑块的大小、形状与景观背景有何差异？只描述参考条件，不含分类误差或退化归因。

**数据**：
- `results/summary/sec33_indicator_grading_preparation/all_class_reference_support.csv`：四站三类像元与面积，计算整站有效参考范围内的占比；与1.1多年农作物面积内占比区分。
- `results/summary/sec33_reference_patch_types/background_class.csv`与`background_landscape.csv`：整图类别级AREA_MN、PD、AI及景观级ED，不混用层级。
- `results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv`及`reference_support_reading.csv`：八组作物分布与截断等支持；斑块等权和像元面积加权分别阅读，不平均旧分位数。
- 原指标及完整斑块身份见`results/processed/sec33_reference_patch_types/reference_patch_features.csv`与对应数据字典。

**状态与安排**：两个小节目前为空。先整理最必要的参考表和段落证据，不等待分级或条件对照；具体核查见[1.3与3.1计划](tasks/2026-10-10-sec13-sec31-foundations.md)。本次只写计划，尚未新增表图或正文。

## 3.1 模型站内分类性能

**问题**：三模型在拥有当地训练数据时能达到什么水平？玉米和大豆的F1差异伴随哪些主要错分？折间指标波动多大？

**数据**：
- `results/summary/f1_raw_scale/within_site_crop_f1.csv`（汇总口径玉米 F1 / 大豆 F1 / OA，12 组）
- `results/summary/f1_raw_scale/within_site_crop_f1_fold_stats.csv`（五折 mean±std；计算不按显示精度舍入）
- `results/processed/sec33_directional_confusion_closeout/crop_metrics_per_prediction.csv`（筛本站，TP/FN/FP、Precision、Recall、F1与状态）和`results/summary/sec33_directional_confusion_closeout/directional_summary.csv`（验证来源重复行一致后提取六向本站字段）；12个独立基准，不能把按来源关联的行当作新实验。
- `results/processed/sec33_crop_spatial_context/whole_cm.csv`的12个本站矩阵用于整数闭合。补充证据提取尚未执行，计划不代表新核查通过。

**表**：`tables/table1_within_site_baseline.csv`、`tables/table1b_within_site_fold_stability.csv`（数据备查，正文用图不用表）

**图**：
- `figures/results/fig_within_site_f1_{a,b}.pdf`——两子图上下排横向条形图，图框各 7.6×5.7 cm，(a) 四站点玉米分类精度 (b) 四站点大豆分类精度；子图题、图例、图名为 LaTeX 文本
- `figures/results/fig_within_site_map_D_{a..h}.pdf`——D 站分类结果对比，通栏 2 行 4 列、图框各 3.8×3.8 cm：上行全站（红框）、下行局部放大，(a)/(e) 参考标签 (b)/(f) ConvGRU (c)/(g) 3D U-Net (d)/(h) U-TAE

**正文状态**：第1、2段及图2、图3已有历史核查。2026-10-10计划核查现稿并最小补充全域本站主要错分，不重做章节；现有D站窗口只作示例，不代替四站全域结果。

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

**数据**（已有探索已入库，正文证据尚待选择）：
- 总览：`results/summary/sec33_evidence_overview.md`；整站六向错分、指标与互斥接触组修正见`results/summary/sec33_directional_confusion_closeout/`及其processed目录。
- 完整参考斑块：`results/processed/sec33_reference_patch_types/reference_patch_features.csv`、`prediction_count_index.csv`及其索引的192份整数计数。按`target,PID`连接，不使用旧切片景观属性。
- 参考分布见`results/summary/sec33_indicator_grading_preparation/`；共同五档候选见`results/summary/sec33_common_five_grades/`。K2/K4分析保留为探索证据，不预定为正文主体。

**方法**：整站F1使用完整混淆矩阵；真实作物斑块分组以对应参考像元为分母计算漏分与定向错分及其跨站增量，不称完整类别F1。跨站五次分别计算再汇总，模型与来源使用相同目标参考集合。边界与距离用于定位，旧图块分组只供历史追溯。

**当前顺序**：先完成1.3背景与3.1本站错误参照，再针对3.2具体差异选择定向与空间证据。新分级和条件对照待判断实际缺项后开展，不以参考分布排序预定跨站增量规律。

**正文组织**：不用第三级标题。先给空间条件与退化的总体对应关系，再比较模型和作物差异。

**要点**：见 claims.md C8（未验证）。

## 分析备查（不进入正文；本文不设补充材料）

Crop-mIoU 体系：`results/summary/generalization_degradation_36paths.csv`、`within_site_oof_baseline.csv`、`model_significance_analysis.csv`、`results/processed/generalization_analysis.csv`。

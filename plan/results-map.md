# Results Map

论文小节 → 科学问题 → 数据 → 表 → 图。主线见 `plan/paper-context.md`：站内基准 → 跨站退化 → 空间解释，每节回答一个问题。表格文件名中的 table1/2/3 是工作编号，论文编号写作时按出现顺序分配。

## 3.1 模型站内分类性能

**问题**：三模型在拥有当地训练数据时能达到什么水平？玉米和大豆是否存在难度差异？训练是否稳定？

**数据**：
- `results/summary/within_site_crop_f1.csv`（汇总口径玉米 F1 / 大豆 F1 / OA，12 组）
- `results/summary/within_site_crop_f1_fold_stats.csv`（五折 mean±std）

**表**：`tables/table1_within_site_baseline.csv`、`tables/table1b_within_site_fold_stability.csv`（数据备查，正文用图不用表）

**图**：
- `figures/results/fig_within_site_f1_{a,b}.pdf`——两子图上下排横向条形图，图框各 7.6×5.7 cm，(a) 四站点玉米分类精度 (b) 四站点大豆分类精度；子图题、图例、图名为 LaTeX 文本
- `figures/results/fig_within_site_map_D_{a..h}.pdf`——D 站分类结果对比，通栏 2 行 4 列、图框各 3.8×3.8 cm：上行全站（红框）、下行局部放大，(a)/(e) 参考标签 (b)/(f) ConvGRU (c)/(g) 3D U-Net (d)/(h) U-TAE

**正文状态**：第 1、2 段已写（2026-09-19，用户草稿，数字全部核对）；图 2、图 3 已插入

**位置**：第一段 → 图 2 → 第二段 → 图 3；图 3 必须在 3.2 标题之前。图 2 随文排版，3.2 前用浮动体边界约束图 3。

**要点**：见 claims.md C1–C3

## 3.2 模型跨站分类性能与泛化退化

**问题**：跨站后玉米和大豆 F1 下降多少？哪些模型和源—目标区域组合表现不同？

**数据**：
- `results/summary/cross_site_crop_f1_summary.csv`（36 路径，每条路径 5 次预测的均值与标准差）
- `results/summary/cross_site_crop_f1_per_fold.csv`（180 行，显著性检验和追溯用）
- `results/summary/crop_f1_degradation_36paths.csv`（目标站站内基准、跨站 F1 与泛化退化）
- `results/summary/crop_f1_relative_degradation_36paths.csv`（以目标站站内 F1 为分母的相对退化比例，%，图 4 数据）

**正文表**：`tables/table2_cross_site_f1_12paths.csv`。12 行完整迁移路径、6 个模型—作物精度列，末行给出 12 条路径平均；每格为 5 次完整目标站预测的 F1 均值，不列退化值。

**分析备查**：`tables/table2_cross_site_summary.csv` 用于核对模型平均跨站 F1 与平均退化；`tables/table3_significance_tests.csv` 用于正文显著性判断，二者均不单独排表。

**图**：`figures/results/fig_degradation_heatmap_{a..f}.pdf` + `_cbar.pdf`。两行三列，上排玉米、下排大豆，各列依次为 ConvGRU、3D U-Net、U-TAE；图框各 3.8×3.8 cm（1 UNIT），两排下方共用横向色标，LaTeX 标签“泛化退化比例/%”。图示相对退化比例，支持路径难度和方向不对称判断；原百分点差值仅作另一口径备查。

**正文组织**：不用第三级标题。完整精度表回答“实际识别精度多高”，热力图回答“相对目标站当地训练下降多少”；正文提炼主要发现，不逐条复述 12 条路径。

**位置**：表 1、图 4 排在 3.2 标题之后、3.3 标题之前；图 4 的三列容器按 Word 正文通栏 17.4 cm 均分，图框保持 3.8 cm。当前 3.2 无正文，标题随表同页；补正文后应把标题放回段首。

**要点**：见 claims.md C4–C7。

## 3.3 模型跨站泛化差异的空间解释

**问题**：泛化退化与哪些地物组成和景观结构条件相对应？这种对应是否因模型或作物而异？

**数据**：待补
- 站点级：玉米/大豆/其它占比、ED、AREA_MN、AI
- 图块级：`patch_spatial_features.csv`、`cross_patch_summary.csv`、`within_patch_oof.csv`、`cross_patch_fold.csv`（位置待确认）

**方法**：按空间特征分组后汇总混淆矩阵再算类别 F1；`cross_patch_summary.csv` 只用于散点和描述性关系

**主要证据**：地物占比、ED、AREA_MN、AI 等景观指标，以及按空间特征分组后由汇总混淆矩阵计算的分类结果。表图设计待数据验证后确定。

**正文组织**：不用第三级标题。先给空间条件与退化的总体对应关系，再比较模型和作物差异。

**要点**：见 claims.md C8（未验证）。

## 补充材料（不控制正文结构）

Crop-mIoU 体系：`results/summary/generalization_degradation_36paths.csv`、`within_site_oof_baseline.csv`、`model_significance_analysis.csv`、`results/processed/generalization_analysis.csv`。

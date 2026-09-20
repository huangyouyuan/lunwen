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

**要点**：见 claims.md C1–C3

## 3.2.1 模型跨站玉米、大豆分类性能

**问题**：离开训练区域后，玉米和大豆分别能达到什么水平？三模型差异是否显著？

**数据**：
- `results/summary/cross_site_crop_f1_summary.csv`（36 路径，5 模型 mean±std）
- `results/summary/cross_site_crop_f1_per_fold.csv`（180 行，追溯用）

**表**：`tables/table2_cross_site_summary.csv`、`tables/table3_significance_tests.csv`

**图**：无

**要点**：见 claims.md C4、C5

## 3.2.2 模型泛化退化

**问题**：哪个模型玉米/大豆下降少？各折模型间是否稳定？"下降少"是否只是基准低？

**数据**：`results/summary/crop_f1_degradation_36paths.csv`

**表**：`tables/table2_cross_site_summary.csv`（退化列）

**图**：无

**要点**：见 claims.md C6

## 3.3.1 模型在不同源—目标区域组合下的退化差异

**问题**：哪些迁移路径困难？困难路径是否因作物而异？A→B 与 B→A 是否对称？

**数据**：`results/summary/crop_f1_degradation_36paths.csv`

**表**：36 路径明细可作补充材料；正文不放（3.1 已给站内基准，读者可由 ΔF1 倒算跨站绝对值）

**图**：`figures/results/fig_degradation_heatmap_{a..f}.pdf` + `_cbar.pdf`（6 子图，排法待定：2×3 各 3.8 cm 或 3×2 各 5.7 cm，见 figures/data-manifest.md）

**要点**：见 claims.md C7

## 3.3.2 模型退化与空间特征的关系

**问题**：各模型的退化与图块内地物占比、ED、AREA_MN、AI 是否对应？这种对应是否因模型而异？（回答论文研究问题的后半句）

**数据**：待补
- 站点级：玉米/大豆/其它占比、ED、AREA_MN、AI
- 图块级：`patch_spatial_features.csv`、`cross_patch_summary.csv`、`within_patch_oof.csv`、`cross_patch_fold.csv`（位置待确认）

**方法**：按空间特征分组后汇总混淆矩阵再算类别 F1；`cross_patch_summary.csv` 只用于散点和描述性关系

**表/图**：待定

**要点**：见 claims.md C8（未验证）

## 补充材料（不控制正文结构）

Crop-mIoU 体系：`results/summary/generalization_degradation_36paths.csv`、`within_site_oof_baseline.csv`、`model_significance_analysis.csv`、`results/processed/generalization_analysis.csv`。

# Table Schema

正式表格定义。文件名中的 table1/1b/2/3 为工作编号，论文编号在写作时按出现顺序分配。

## 站内分类性能（OOF pooled）

**Purpose**：建立站内基准。
**Source**：`tables/table1_within_site_baseline.csv` ← `results/summary/within_site_crop_f1.csv`
**Rows**：模型 × {玉米 F1, 大豆 F1, OA}，9 行
**Columns**：A | B | C | D | Mean
**口径**：五折测试 CM 逐元素求和后计算
**Status**：已生成，已验证（2026-09-18）

## 站内五折稳定性

**Purpose**：说明训练稳定性。
**Source**：`tables/table1b_within_site_fold_stability.csv` ← `results/summary/within_site_crop_f1_fold_stats.csv`
**Cells**：mean±std（各测试折指标的算术统计）
**排版**：可与上表合并，pooled 值后括号注 std；写作时定
**Status**：已生成，已验证

## 12 条迁移路径跨站分类性能（正文表）

**Purpose**：完整报告各源—目标组合的实际跨站识别精度。
**Source**：`tables/table2_cross_site_f1_12paths.csv`、`tables/table2_cross_site_f1_12paths_rows.tex` ← `results/summary/cross_site_crop_f1_summary.csv`
**Rows**：12 条有向迁移路径 + 末行“平均”
**Columns**：迁移路径 | ConvGRU 玉米 F1 | ConvGRU 大豆 F1 | 3D U-Net 玉米 F1 | 3D U-Net 大豆 F1 | U-TAE 玉米 F1 | U-TAE 大豆 F1
**口径**：每格为源站 5 个折模型分别预测目标站全部 400 个图块所得 F1 的算术平均；“平均”为 12 条路径均值的算术平均；单位为百分数，保留两位小数
**Status**：已生成，已验证

## 跨站分类性能与泛化退化（分析备查）

**Source**：`tables/table2_cross_site_summary.csv` ← `results/summary/crop_f1_degradation_36paths.csv`
**Rows**：模型 × 作物，6 行
**Columns**：跨站 F1 mean±std | ΔF1 mean±std（pp）
**Status**：已生成；只供正文数字核对，不作为正文表

## 模型显著性检验

**Purpose**：判断架构差异是否稳定；检验结果写入正文，不单独排表。
**Source**：`tables/table3_significance_tests.csv` ← `results/summary/cross_site_crop_f1_per_fold.csv`
**Rows**：玉米、大豆
**Columns**：Friedman χ² | p | ConvGRU vs 3D U-Net | ConvGRU vs U-TAE | 3D U-Net vs U-TAE（Holm 校正）
**配对单位**：12 条路径的五折均值
**Status**：已生成，已验证 n=12

## 研究区景观格局指数（第 1 章）

**Purpose**：描述 4 站点空间异质性，供 3.3.2 解释。
**Source**：CDL 2021–2024 + FRAGSTATS 4.3（旧稿表 1）
**Columns**：站点 | 地物类型 | PD | AREA_MN | AI | ED
**Status**：旧稿已有，需数据验证

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

## 跨站分类性能与泛化退化（模型汇总）

**Purpose**：描述跨站表现与退化。
**Source**：`tables/table2_cross_site_summary.csv` ← `results/summary/crop_f1_degradation_36paths.csv`
**Rows**：模型 × 作物，6 行
**Columns**：跨站 F1 mean±std（该模型 12 条路径的路径均值统计）| ΔF1 mean±std（pp）
**Status**：已生成，已验证

## 36 路径明细（候选补充表）

**Source**：`results/summary/crop_f1_degradation_36paths.csv`
**Columns**：模型 | 源→目标 | 站内 F1 | 跨站 F1 mean±std | ΔF1，玉米、大豆各一组
**Status**：数据就绪；短文正文用热力图，明细放补充材料

## 模型显著性检验

**Purpose**：判断架构差异是否稳定。
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

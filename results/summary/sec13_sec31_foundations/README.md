# 1.3 与 3.1 基础证据阅读入口

本目录是对既有结果的只读整理，不是新实验。它为 1.3 的四站参考空间背景和 3.1 的本站分类基准提供可追溯阅读表，也为 3.2 到 3.3 的最小衔接保留一条已验证的条件性线索。

## 范围

- `reference_composition.csv`：四站三类参考像元、面积及整站占比。
- `class_background_full_scope.csv` 与 `landscape_background_full_scope.csv`：只保留 `scope=full` 的类别级和景观级背景；景观级 ED 不属于作物专属指标。
- `crop_patch_distribution_reading.csv` 与 `crop_patch_support_and_limitations.csv`：八个站点—作物组的 AREA、SHAPE 两种权重分布，以及微小斑块、无内部区域和研究窗口外框截断的支持量。
- `within_site_crop_metrics.csv`、`within_site_crop_gap_diagnostic.csv`、`within_site_directional_errors.csv`、`within_site_dominant_error_direction.csv`：12 个独立本站模型—目标站基准的两作物指标、作物差异和六向错分。
- `within_site_matrix_checks.csv` 与 `verification_checks.csv`：原始五折矩阵、已处理整图矩阵、参考支持、TP/FN/FP、方向性闭合和正式 F1 的本次核对。
- `sec32_to_sec33_evidence_bridge.csv`：用于决定后续 3.3 必要证据的内部衔接表，不是正文结论。

本站基准由五折测试混淆矩阵逐元素求和后计算；跨站结果仍按五次完整目标站预测分别计算后取均值。本站方向性记录在上游汇总中按三个来源站重复，本次先验证其数值一致，再折叠为 72 条方向记录，绝不把它们当作 36 次独立本站实验。

所有输出均为 `derived` 或 `reused_verified_summary`。输入、脚本和输出 SHA-256 见 `manifest.json`。`paragraph_evidence_outline.md` 仅为正文作者提供证据路由，不替代正文，也不赋予景观指标因果解释。

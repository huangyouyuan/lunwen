# 空间条件发现提炼：结果入口

2026-10-12，起点HEAD `427fc89`。结果性质为 **derived / exploratory**。本轮执行[任务计划](../../../plan/tasks/2026-10-12-spatial-findings-refinement.md)，在已有全路径分析上检验一个明确候选：本站高SHAPE组较高的漏分，是否必然对应更多跨站额外漏分。没有修改论文或图表。

先读[提炼报告](refinement-report.md)。各站主要面积—形状分布直接引用[气泡图v3原汇总](../area_shape_joint_bubbles_v3/area_shape_joint_bins.csv)，本轮没有重做该统计。SHAPE=2二分是条件对照，不是形态分类。

后续[模型优势空间分析](../model_advantage_spatial_conditions/README.md)把单模型错误转成U-TAE/3D U-Net相对ConvGRU的差额，核对同编号划分，并在同一支持范围内比较统一距离前后。此处原表及权重保留，C/D细分结果由后续直接复用。

| 阅读目的 | 文件 |
|---|---|
| 共同A/B来源、三模型的精简对照，含三套分层 | [core_common_source_comparisons.csv](core_common_source_comparisons.csv)（36行） |
| 本站条件错误率；跨站五次均值、标准差和方向 | [within_standardized_rates.csv](within_standardized_rates.csv)、[cross_standardized_rates.csv](cross_standardized_rates.csv) |
| 主要方向是否依赖分层、门槛或来源集合 | [candidate_consistency.csv](candidate_consistency.csv) |
| 参考支持、被排除面积、残余AREA和ENN差异 | [coverage_and_reference_balance.csv](coverage_and_reference_balance.csv)、[common_support_weights.csv](common_support_weights.csv)、[reference_cells.csv](reference_cells.csv) |
| 完整大豆面积下的两组实际计数与贡献 | [within_natural_shape_counts.csv](within_natural_shape_counts.csv)、[cross_natural_shape_counts.csv](cross_natural_shape_counts.csv) |
| 同一来源模型、同一预测编号下的C/D对照 | [paired_C_D_summary.csv](paired_C_D_summary.csv) |
| 对照差来自哪些面积×距离层 | [stratum_gap_contributions.csv](stratum_gap_contributions.csv)；这是标准化差的分解，不是全站错误贡献 |
| 保留四站、两作物全部72个候选对照 | [all_paths_candidate_context.csv](all_paths_candidate_context.csv)，复用旧逐站权重口径 |
| 与完整F1、FN及FP相联系 | [whole_F1_context.csv](whole_F1_context.csv)；其余四站全路径见[上一轮入口](../spatial_error_conditions/README.md) |

全部逐次表保存在[processed目录](../../processed/spatial_findings_refinement/)。主结论读取`scope=joint_CD, rule=primary`及共同A/B来源；三套分层按`scheme`区分，不能混合计数。精简表中的自然面积/净增量贡献为便于阅读而重复附列，不应跨方案相加。

## 复现

从仓库根目录执行：

```powershell
python -B scripts/refine_spatial_findings.py
python -B scripts/test/check_spatial_findings_refinement.py
```

第一条使用现有Python、NumPy和pandas，读取保存特征、96份计数及上一轮底表，只更新本轮目录中的生成CSV、配置和manifest。它不重训、不推理、不重算距离或景观指标，也不调用绘图入口；不会重写人工报告。第二条只读核查。没有外部影像目录依赖。

数据定义见[字段说明](data_dictionary.md)，验证范围见[核查说明](verification.md)。[manifest.json](manifest.json)记录输入、生成结果和生产脚本哈希，不包括人工文档；[analysis_config.json](analysis_config.json)保存固定分档、门槛和权重定义。原气泡表及旧错误表原位保留。

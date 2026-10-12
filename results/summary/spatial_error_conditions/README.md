# 四站空间条件与分类错误：结果入口

2026-10-12；基于 HEAD `d37695a` 的保存数据，derived / exploratory。本轮暂停1.3正文、表格和气泡图修改，只新增统计、阅读表与报告，没有训练、推理、制图或编译。

先读[分析报告](analysis-report.md)，统计定义见[数据字典](data_dictionary.md)，本次范围与历史限制见[核查说明](verification.md)。这批分档和对照是针对明确问题的探索，不替代既有K2/K4成果，不把展示区间冻结为形态类型。

## 建议阅读顺序

| 要回答的问题 | 主要表 |
|---|---|
| 本站F1、漏分和误分入；跨站绝对F1与差距 | [本站完整类别指标](within_whole_crop.csv)、[跨站完整类别指标](cross_whole_crop.csv)、[目标站三源均值](reading_target_cross_means.csv) |
| 六条错分通道，哪条净增最多 | [本站六向错分](within_six_directions.csv)、[跨站六向错分](cross_six_directions.csv) |
| 含其它地类的错误在何处 | [本站三段距离定位](within_direction_location.csv)、[跨站三段距离定位](cross_direction_location.csv) |
| 小斑块、远邻斑块、边界和内部实际贡献多少 | [本站空间子集阅读表](reading_within_spatial_subsets.csv)、[跨站空间子集阅读表](reading_cross_spatial_subsets.csv) |
| 面积、形状、ENN的条件对应是否稳定 | [条件对应概览](reading_condition_consistency.csv)、[本站条件对照](within_conditional_contrasts.csv)、[跨站条件对照](cross_conditional_contrasts.csv) |
| 站间差异是条件占比不同，还是相近条件下错误率不同 | [本站共同权重](within_site_common_weights.csv)、[本站差距分解](within_site_gap_decomposition.csv)、[跨站共同权重](cross_site_common_weights.csv) |
| 全部分档的支持和统计 | [参考支持](reference_group_support.csv)、[本站分组](within_group_metrics.csv)、[跨站分组](cross_group_metrics.csv) |
| 被共同支持排除的条件 | [条件对照权重](conditional_support_weights.csv)、[四站共同支持权重](site_common_support_weights.csv) |
| 整站组成、AI、NP/PD、ED背景 | [类别背景](site_class_background.csv)、[景观背景](site_landscape_background.csv) |

逐次数据保存在 [`results/processed/spatial_error_conditions/`](../../processed/spatial_error_conditions/)，包括12个本站汇总预测和180个跨站完整预测；每条路径的五次均保留。`group_metrics_per_prediction.csv`有82,176行，不能把行数当作独立样本数。未新增图件。

## 复现

从仓库根目录执行：

```powershell
python -B scripts/analyze_spatial_error_conditions.py
python -B scripts/test/check_spatial_error_conditions.py
```

第一条仅写入本批独立的processed/summary目录；不运行历史生产脚本，不改变原始特征、计数、正式F1和论文。它会更新本脚本生成的CSV、配置、manifest；不重写本目录人工撰写的报告和说明。第二条只读检查。环境使用现有Python、NumPy、pandas，无需外部影像路径。

溯源：[原完整斑块字典](../sec33_reference_patch_types/data_dictionary.md) → [`reference_patch_features.csv`](../../processed/sec33_reference_patch_types/reference_patch_features.csv) + [`prediction_count_index.csv`](../../processed/sec33_reference_patch_types/prediction_count_index.csv)及192份NPZ → 本批分组和条件对照。全站指标和六向统计复用[定向混淆收尾](../sec33_directional_confusion_closeout/README.md)，重新闭合到保存整数矩阵和[正式F1链](../f1_raw_scale/)。

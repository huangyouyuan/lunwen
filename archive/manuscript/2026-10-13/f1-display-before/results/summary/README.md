# 当前结果阅读入口

科学数字以经过核查的summary为准；本目录是阅读入口，不将整理旧表当作新实验。类别顺序为corn=0、other=1、soybean=2。当前主线见 [总体计划](../../plan/outline.md)。

## 正式F1链

输入为 `results/raw/within_site_confusion_matrices.csv`和`cross_site_confusion_matrices.csv`，经 `scripts/calculate_f1_raw_scale.py`及 `results/processed/f1_raw_scale/`生成：

| 文件 | 内容 |
|---|---|
| [本站F1](f1_raw_scale/within_site_crop_f1.csv) | 12个独立模型—目标站汇总基准 |
| [本站折间统计](f1_raw_scale/within_site_crop_f1_fold_stats.csv) | 各折指标mean/std，仅说明折间波动 |
| [跨站逐次F1](f1_raw_scale/cross_site_crop_f1_per_fold.csv) | 180次完整目标预测 |
| [跨站F1汇总](f1_raw_scale/cross_site_crop_f1_summary.csv) | 36个模型—路径组合，各五次 |
| [原尺度ΔF1](f1_raw_scale/crop_f1_difference_36paths.csv) | 本站减跨站五次均值 |
| [来源清单](f1_raw_scale/run_manifest.json) | 原运行输入、脚本和产物哈希 |

计算保存17位有效数字，F1及ΔF1采用原尺度；显示两位小数不用于重新计算。本站先加总折矩阵，跨站先逐次计算再汇总，不能混用。

## 基础材料与解释证据

| 入口 | 用途与边界 |
|---|---|
| [1.3与3.1基础证据](sec13_sec31_foundations/README.md) | 四站组成、完整参考斑块背景、12个本站基准及其本次闭合核查；1.3 已据此补充正文、组成图和 AREA/SHAPE 分布表 |
| [整图参考字典](sec33_reference_patch_types/data_dictionary.md) | 完整斑块特征、背景、参考数组和192份预测计数 |
| [参考分布](sec33_indicator_grading_preparation/README.md) | 数量与面积加权分布，为1.3提供背景；不是正式等级 |
| [定向混淆收尾](sec33_directional_confusion_closeout/README.md) | 完整FN/FP、六向混淆、模型分层、互斥边界与距离案例 |
| [七带漏分率与净贡献](sec33_round3_distance/band_metrics_summary.csv) | 全路径三类/全体的本站率、五次跨站率、像元占比和贡献；[逐次底表](../processed/sec33_round3_distance/band_metrics_cross_fold.csv) |
| [正确配对的Δe两端对照](sec33_round3_closeout/nearest_vs_gt6_delta_e_summary.csv) | 最近带与`>6`带的额外漏分差；[逐次表](../processed/sec33_round3_closeout/nearest_vs_gt6_delta_e_per_fold.csv)按预测编号配对 |
| [完整F1错分分量](sec33_crop_spatial_context/whole_f1_error_components_summary.csv) | 两种漏分与两种误分入共同连接F1；[逐次底表](../processed/sec33_crop_spatial_context/whole_f1_error_components_per_prediction.csv)使用F1自身分母 |
| [距离共同权重与条件错误](sec33_crop_spatial_context/distance_common_weights.csv) | 参考分布权重；[逐次标准化表](../processed/sec33_crop_spatial_context/distance_weighted_per_prediction.csv)是描述性漏分率对照，不是F1或因果分解 |
| [3.3证据总览](sec33_evidence_overview.md) | 对照3.2的现象、证据和限制 |
| [完整斑块K2](sec33_reference_patch_types/type_error_summary.csv)与[K4](sec33_k4_sensitivity/type_error_summary.csv) | 全部类型逐次结果、参考支持和冻结归属已恢复；作为既有条件探索 |
| [五档候选支持](sec33_common_five_grades/grade_support.csv) | 待审阅方案；没有等级误差统计，未批准冻结 |
| [分层复用与源码索引](reuse-status.md) | 当前证据、补充探索、候选与历史方法的使用边界 |

先恢复27份，2026-10-11再恢复413份，累计440份原文件回到原路径，没有重算或修改其数值。两端对照和D站逐次诊断还见`sec33_round3_closeout/`，六向两端对照见`sec33_crop_spatial_context/`。定义及历史核查也一并恢复：[七带字典](sec33_round3_distance/data_dictionary.md)、[配对字典](sec33_round3_closeout/data_dictionary.md)、[空间对照字典](sec33_crop_spatial_context/data_dictionary.md)。混合字典中旧图块匹配条目仍是历史定义，当前使用范围以[复用索引](reuse-status.md)为准，原历史验证状态不升级。

已按 [1.3与3.1基础材料计划](../../plan/tasks/2026-10-10-sec13-sec31-foundations.md) 完成本次底表整理与闭合核查，见[基础证据目录](sec13_sec31_foundations/README.md)。1.3 已补充正文、组成图和 AREA/SHAPE 分布表；3.1 的正文补充和后续 3.3 证据取舍仍未完成。

过时口径与旧方案仍在 [独立归档](../../archive/2026-10-10-mainline/README.md)。原清单的历史路径与核验状态保持不变；不运行归档源码恢复旧流程。

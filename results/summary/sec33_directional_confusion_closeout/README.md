# 定向混淆与空间定位：当前阅读入口

本目录保留已经修正的定向混淆、互斥直接接触边界、六向组成对照和模型分层结果，支持3.1本站错分参照及3.3对3.2的解释。结果是derived / exploratory，不是机制证明。

| 表格 | 用途 |
|---|---|
| [六向混淆](directional_summary.csv) | 本站计数及率、跨站五次变化与方向；包含其他类误分入 |
| [模型—作物指标](model_crop_metrics_summary.csv) | 12条路径等权的Precision、Recall、F1及变化 |
| [路径级指标](model_crop_path_diagnostics.csv) | 完整路径和例外，不以总体均值代替每种模型 |
| [互斥边界支持](exclusive_boundary_reference_support.csv)与[结果](exclusive_boundary_summary.csv) | 最近带中的纯接触、混合接触和非直接接触，零支持记NA |
| [D站距离对照](case_D_distance_all_sources.csv) | 三模型、三来源的大豆→玉米七带定位 |
| [六向组成对照](source_composition_direction_contrast.csv) | 整站组成与六向变化，只作描述性对照 |

逐次结果在`results/processed/sec33_directional_confusion_closeout/`。定义见[数据字典](data_dictionary.md)，科学判断见[原报告](exploration-report.md)，原运行核查见[verification](verification.md)。错误率增量为跨站减本站，显示为百分点；ΔF1为本站减跨站，原尺度。完整类别F1不按空间区或方向相加。

2026-10-10只整理入口和修复脚本依赖，没有重算这些结果。原报告、CSV、清单及其原哈希保持不变；旧报告的“原位保留”是原交付状态，此后历史上游和旧图件的现址见[迁移清单](../../../archive/2026-10-10-mainline/archive-manifest.csv)。

保留的收尾脚本改为导入只读`sec33_metrics.py`，历史生成脚本已归档。脚本主入口会写结果，未经要求不要重跑；可只读表格或运行相关测试。既有清单中的脚本哈希对应原交付版本，当前脚本修订记录见[整理核查](../../../verification/mainline-archive-2026-10-10.md)。距离生成状态没有升级。

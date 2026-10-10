# 3.3 景观指标分级准备：表格阅读入口

本轮为参考统计准备，不产生新的预测误差结论、图件或正式等级归属。分析对象为整幅标签的完整参考连通斑块，不是128×128图块或真实农业田块。结果性质为derived / exploratory。本目录保留可复用分布表；历史聚类、候选等级与生产源码已按迁移清单归档。

| 阅读顺序 | 表格 | 用途 |
|---|---|---|
| 1 | [已有成果与缺项](existing_gap_inventory.csv) | 哪些已有、哪些确实缺失、为何补充 |
| 2 | [统一指标分布](indicator_distribution_reading.csv) | 四站两作物、单作物合并及总体；数量等权与面积权重并列 |
| 3 | [集中取值](concentrated_values.csv) | 每域每指标数量或面积排名前5的实际取值，不舍入合并 |
| 4 | [完整取值及累计覆盖](../../processed/sec33_indicator_grading_preparation/value_frequency_cumulative.csv) | 全量频率、两种累计分布及单像元/无内部/截断支持 |
| 5 | [共同数值区间支持诊断](diagnostic_value_intervals.csv) | 合并面积ECDF覆盖切段后查看各层支持；不是候选正式等级 |
| 6 | [分层分布重叠](stratum_distribution_overlap.csv) | 28个层间对照×3指标；范围覆盖与两种ECDF最大差值 |
| 7 | [参考支持](reference_support_reading.csv) | 复用K4整数支持求和；单像元、无内部及截断数量/面积分开 |
| 8 | [旧成果用途索引](results_use_index.csv) | 可直接复用、未来需重新汇总及历史探索的区别 |

辅助入口：[指标可用性](indicator_availability.csv)、[旧等权分布](reused_indicator_distributions.csv)、[旧相关性](reused_indicator_correlations.csv)、[旧K2/K4支持](reused_type_reference_support.csv)、[三类参考支持](all_class_reference_support.csv)、[计数结构核查](count_reuse_schema.csv)。后者保留其他类，不把作物漏分率当成包含完整FP的F1。

解释、算法与本次核查分别见[简短判断](preparation-report.md)、[数据字典](data_dictionary.md)、[核查记录](verification.md)。此处只读表格。原生产源码已停用归档，不是活动运行入口；[迁移清单](../../../archive/2026-10-10-mainline/archive-manifest.csv)记录历史路径与现址。

原交付记录为6项专项测试、生产191条和交付552条检查通过，本次归档未重复这些科学核查。来源记录见[运行清单](run_manifest.json)，最终脚本、任务和产物哈希见[交付清单](delivery_manifest.json)；核查结论不升级历史距离生成或FRAGSTATS工程配置的状态。

`domain=all/crop/site_crop`是三种不同阅读视图，不能把它们加在一起。AREA单位ha，SHAPE无量纲，ENN单位m。频率保持保存值精度，比例为0—1，NA为空字段；显示值相同不构成合并依据。这些表为1.3背景及按需空间条件分析提供分布信息。已产生的共同五档候选另行归档，既有候选不等于正式等级或当前必做方案。本次不冻结断点，不生成错误结果。旧CSV索引、报告和清单中的路径是原运行记录；被移动的文件按迁移清单定位，不据此运行历史生产流程。

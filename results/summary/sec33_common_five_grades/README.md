# 3.3 共同五档候选与参考支持量

活动入口为本目录。2026-10-10，基线`0562e08`。本轮只形成参考分布驱动的共同等级候选，**待作者审阅，未批准冻结**；没有计算等级错误、绘图或改正文。

先读[推荐说明](report.md)，再看以下三张核心表：

| 表 | 阅读用途 |
|---|---|
| [grade_definitions.csv](grade_definitions.csv) | AREA/SHAPE共同阈值、Ⅰ—Ⅴ方向、端点归属、整数像元端点及待审阅状态 |
| [grade_support.csv](grade_support.csv) | 总体及八个站点×作物的逐档数量、面积、标记和边界/内部支持 |
| [five_grade_coverage_comparison.csv](five_grade_coverage_comparison.csv) | 并列八层数量和面积占比；[coverage_diagnostics.csv](coverage_diagnostics.csv)给出实际最小支持及集中程度，无人为充分性阈值 |

`scheme=recommended`为推荐方案；`area_ecdf_alternative`仅把AREA换成总体面积加权五分位切点，SHAPE与推荐方案完全相同。两指标独立，两方案及`all/site_crop`视图不能重复合计。

其他入口：

- [逐斑块归属](../../processed/sec33_common_five_grades/patch_grade_assignments.csv)：唯一键`target,PID`，保留两套AREA和两份同一SHAPE标签，带原指标、位置支持及斑块标记。
- [候选配置](candidate_config.json)、[切点分位数依据](cutpoint_reference_quantiles.csv)：参考分布及变换规则；不读取模型错误来定阈值。
- [小值段诊断](area_small_interval_support.csv)、[小值段完整频数](area_small_value_frequency.csv)：后者直接摘录旧精确频数，前者是本轮细段汇总，均不是另一套主体等级。
- [ENN集中值诊断](enn_concentration_diagnostic.csv)：解释为何本轮不提出ENN五档。
- [排除支持](excluded_reference_support.csv)、[无效记录](../../processed/sec33_common_five_grades/invalid_metric_records.csv)：当前均无排除，空底表保留列头，不把缺失当成零。
- [三类参考总量](all_class_reference_inventory.csv)：保留其他类和相应位置支持，不把其他类混入作物等级分母。
- [数据字典及计数接口](data_dictionary.md)、[实际核查范围](verification.md)、[生产核查](production_checks.csv)、[交付核查](delivery_checks.csv)、[辅助参考表复核](reference_diagnostic_checks.csv)。

复用来源仍在原位：[上轮分级准备](../sec33_indicator_grading_preparation/README.md)。其中完整频数、分布和历史诊断区间继续可用；旧诊断区间没有改名冒充本轮等级。旧K2/K4冻结归属用于历史追溯，未修改，也未按其汇总比例拆出本轮支持量。

脚本为`scripts/prepare_sec33_common_five_grades.py`。默认生产拒绝覆写现有目录；`--audit`和`--finalize`也拒绝覆写已有同名核查表/清单。运行与最终哈希分别见`run_manifest.json`和`delivery_manifest.json`。

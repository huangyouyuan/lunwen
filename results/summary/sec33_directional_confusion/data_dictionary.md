# 定向混淆与空间定位数据字典

本目录结果为 derived / exploratory。计数来自已核验的完整混淆矩阵、七距离带和边界类型底表；跨站五次先逐次计算，再取均值和样本标准差。

| 文件 | 内容 |
|---|---|
| `directional_per_prediction.csv` | 全站六种有向错分的本站/跨站逐次值；`delta_rate` 和 `delta_rate_pp` 均为跨站减本站。 |
| `directional_summary.csv` | 固定模型、来源、目标站和方向后的五次汇总、方向统计和本站基准。 |
| `crop_metrics_per_prediction.csv` / `crop_metrics_summary.csv` | 玉米、大豆及其他类的 TP、FN、FP、Precision、Recall、F1 及五次摘要。 |
| `crop_f1_difference.csv` | 玉米 F1 减大豆 F1，以及 `cross = within + soybean_delta - corn_delta` 核对。 |
| `distance_direction_*` | 原七距离带的有向错误率和增量；`d>6` 为开放远内部带。 |
| `boundary_type_direction_*` | 三种已有边界类型与七距离带的有向错误率；多类型像元遵循历史类型表规则。 |
| `k4_c3_c4_type_error_per_prediction.csv` | K4-C3/C4 主要作物图斑内的漏分、错向另一作物和错向其他类；不计算类型内 F1。 |
| `k4_c3_c4_feature_support.csv` | C3/C4 的参考图斑特征与支持量，不能解释为单一形态效应。 |
| `source_target_composition.csv` | 四站整站参考组成的来源—目标描述性对照。 |
| `case_D_soybean_to_corn_by_distance_all_sources.csv` | D 站大豆→玉米距离带核对实例，保留 A/B/C 三个来源和三个模型。 |
| `case_D_soybean_to_other_by_distance_all_sources.csv` | D 站大豆→其他类距离带核对实例，保留 A/B/C 三个来源和三个模型。 |
| `case_D_soybean_to_corn_by_boundary_type_all_sources.csv` | D 站大豆→玉米最近带边界类型核对实例，保留 A/B/C 三个来源和三个模型。 |
| `case_D_soybean_k4_c3_c4_all_sources.csv` | D 站大豆 K4-C3/C4 图斑类型条件对照，保留全来源和模型。 |

定向错误率定义为真实来源类别被预测为指定目标类别的像元数除以同一真实来源类别像元数。漏分率是两个定向错分方向之和；误分入按真实来源类别统计。错误计数差是净变化，不是逐像元配对的新增错误数。`ΔF1` 仍为本站 F1 减跨站五次 F1 均值，不与错误率增量混用。

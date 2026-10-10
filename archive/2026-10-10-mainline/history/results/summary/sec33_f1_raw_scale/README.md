# AREA_MN 原尺度 ΔF1 探索数据字典

本目录为2026-10-05生成的 derived / exploratory 结果，不自动成为论文结论。阅读入口为[探索报告](exploration-report.md)。历史DR结果保留在相邻 `sec33_exploration/`，本目录不读取历史DR数值作为精度依据。

## 运行与来源

从仓库根目录执行 `python -B scripts/explore_sec33_f1_raw_scale.py --check-only`，在内存中完成重建及核查，不写文件；去掉 `--check-only` 才保存结果。输入、脚本和输出相同的再次执行只核验、不改写；已有产物发生变化时拒绝覆盖。

冻结归属与阈值来自 `results/processed/sec33_exploration/`；已有组CM经外部 `patch_spatial_features.csv`、`within_patch_oof.csv`、`cross_patch_fold.csv` 重新关联核对，输出整数矩阵位于 `results/processed/sec33_f1_raw_scale/`。全站对照来自 `results/raw/` 整数矩阵和 `results/summary/f1_raw_scale/`。绝对输入路径及SHA-256见 [run_manifest.json](run_manifest.json)。外部训练目录及G盘元数据只在身份/闭合异常时回溯，本次未触发。

## 键、单位和缺失

- 站点：iw_2023=A、iw2_2023=B、ida_2023=C、il_2023=D；模型：convgru、unet3d、utae；crop：corn=玉米、soybean=大豆。other=其它地类。
- 组键 `G=(target,crop,group)`；本目录主分组固定为AREA_MN，因此主表不重复metric列。`group_features.metric`明确为AREA_MN。组标签low/mid/high/missing；missing不参与有序趋势，但参与所有CM闭合。
- 本站键 `W=(model,G)`；路径组键 `P=(model,source,G)`；逐次键为`P+fold`。fold是源站模型编号1～5，不是目标图块分组。
- 混淆矩阵 `cm_ij` 为非负整数，行真实、列预测，0玉米、1其它、2大豆。各组求和才是全站CM，F1和ΔF1不能用于组间加权闭合。
- F1、标准差和ΔF1采用原尺度；比例0～1，AREA_MN为ha，ED为m/ha，AI为0～100。数据保存17位有效数字，推荐 `pd.read_csv(..., float_precision='round_trip')`。`NA`是不可计算或不适用，不是零。最终显示两位小数，显示相同不代表全精度相等。
- 每张CSV的`data_status=derived`、`analysis_status=exploratory`明确产物属性。检查结果为Verified；空间指标未从标签重建的限制由清单和核查报告单列。

## 表及字段

| 文件 | 行数与键 | 内容 |
|---|---|---|
| `group_f1_difference.csv` | 252，P | 统一主表；216有序组+36缺类组 |
| `group_features.csv` | 28，G | 分组阈值、实际特征统计、参考组成；通过G与主表多对一关联 |
| `within_group_f1.csv` | 84，W | 组OOF CM计算的本站F1、真实/预测像元数、假阳性/假阴性、F1状态 |
| `cross_group_per_prediction.csv` | 1260，P+fold | 每次跨站组F1、本站基准、逐次ΔF1及混淆计数；先计算这些F1再取五次均值 |
| `three_source_means.csv` | 84，W | 三个来源的跨站均值等权平均及相应ΔF1；n_sources固定3，有任一来源不可计算时不缩减分母 |
| `group_contrasts.csv` | 72，model/source/target/crop | 保留三组指标、相邻组与高低组差及趋势 |
| `model_comparisons.csv` | 72，source+G | 三模型精度、ΔF1、排序、极差及ConvGRU是否最低F1/最小ΔF1 |
| `model_pair_differences.csv` | 216，source+G+model_a/model_b | 三模型逐对比较，各字段均为a减b |
| `source_comparisons.csv` | 72，W | 三来源跨站F1、ΔF1、F1排序和极差 |
| `source_pair_differences.csv` | 216，W+source_a/source_b | 来源逐对差，跨站F1差与ΔF1差互为相反数，不是两个独立发现 |
| `source_group_changes.csv` | 24，model/target/crop | 三组来源极差、排序、高低极差变化及排序是否改变 |
| `composition_changes.csv` | 8，target/crop | 三组全部三类占比、AREA_MN/ED/AI中位数，以及高减低变化 |
| `area_ai_rank_redundancy.csv` | 8，target/crop | 有限值配对的有效样本数及平均秩Spearman相关；不含P值 |
| `site_features.csv` | 8，site/crop | 完整站点标签的ED、作物AREA_MN/AI、三类占比；不能等同于图块尺度指标 |
| `source_target_feature_differences.csv` | 144，source/target/crop/site_feature | 全站特征源值、目标值、有符号差source-target与绝对差；三类占比有两个独立维度 |
| `source_feature_pair_comparisons.csv` | 1296，W+source_a/source_b/site_feature | 固定目标条件的来源逐对比较，检视绝对特征差更小是否对应跨站F1更高 |
| `source_feature_counts.csv` | 255，target/crop/model/site_feature/outcome | 上表按三组、三个来源对累计的描述计数；未发生的outcome不输出，不能作为独立观测或变量重要性 |
| `full_site_f1_difference.csv` | 72，model/source/target/crop | 从恢复的全站CM计算的当前口径F1与差值；没有平均组指标 |
| `cm_closure_checks.csv` | 384，kind+crop+实验键 | 2作物分组分别恢复12本站及180跨站逐次矩阵，最大元素误差均0 |
| `full_site_reference_checks.csv` | 600，kind+实验键+crop | 本站24、跨站逐次360、跨站均值72、标准差72、差值72项对照；绝对容差1e-12 |
| `checks.csv` | 290，check | 本次输入哈希、身份、集合、参考像元、分组、闭合及比较条件检查 |
| `exceptions.csv` | 228，kind+对应结果键 | 所有缺类结果及不可计算值、有效零F1、负差值的追溯入口；不等于228个独立问题 |

`group_features`：`q1/q2`为冻结导出值，`actual_cuts`保存实际切点，`lower_bound/upper_bound`为右闭区间边界，不适用的端点为NA；精确图块归属仍以冻结文件为准。`feature_min/median/max`从原始可用指标计算。`patches`为图块数，`valid_pixels`及三类`*_pixels`为参考像元数，`*_ratio`为像元数除以有效总像元；`patch_set_sha256`对排序后UID逐行连接计算摘要。ED与AI只作组内补充，`*_n_defined`记录其可用数量。

主表：`within_f1`为本站组汇总F1；`cross_f1_mean/std/min/max`为五次分别计算F1后的统计量，标准差ddof=1；`delta_f1`为本站减跨站均值，`delta_f1_min/max`为五次差值范围，非置信区间。`within_status/cross_status/delta_status`分别描述各部分的可计算性；基准为0不被排除。`n_predictions=5`，`n_defined_f1`可小于5，但此时均值及标准差为NA。`false_positive_pixels_mean/false_negative_pixels_mean`为五次计数均值，不是F1的替代指标。

趋势标签increasing/decreasing表示三个组间无反向变化；本次有关主趋势均为严格升降。nonmonotonic保留方向反转，undefined表示有缺值。排序使用未舍入值；`>`表示F1降序，`<`表示ΔF1升序，完全相等时以`=`连接。`convgru_lowest_cross/convgru_smallest_delta`允许数值并列，本次有序组没有模型并列。

来源特征逐对比较：consistent表示特征绝对差较小者跨站F1较高，opposite为相反，tie为任一比较量相等，invalid为不可计算。未通过跨目标相关或多变量模型估计来源效应。

# 3.3 定向混淆收尾数据字典

本目录为 `derived / exploratory` 定点修订。活动入口为本目录的 `exploration-report.md`、生产脚本 `scripts/explore_sec33_directional_confusion_closeout.py` 和绘图脚本 `scripts/plot_sec33_directional_confusion_closeout.py`。原 `sec33_directional_confusion` 目录及重叠边界图保持原位，作为历史与补充对照，不能替代本轮互斥主视图。

## 身份与统计口径

逐次身份 `RUN = kind, model, source, target, fold`：本站 `kind=within, source=target, fold=0`，共12个独立模型—目标站基准；跨站 `kind=cross, source!=target, fold=1..5`，共180次预测。A/B/C/D分别对应 `iw_2023/iw2_2023/ida_2023/il_2023`。三类矩阵行是真实类别、列是预测类别，编码0玉米、1其他类、2大豆。

定向率 `rate=errors/reference_pixels`，分母是同组真实来源类别像元数，两个错分方向之和为该类漏分率。`within_rate` 与 `within_errors` 来自同模型、同目标、同参考组本站矩阵。`delta_rate=跨站率−本站率`，`delta_errors=跨站计数−本站计数`；后者为净计数变化，不是逐像元配对的实际新增错误数。`*_pp` 为原尺度率差乘100，单位百分点。`share_of_nearest_class` 以同站同真实类最近带支持量为分母，`share_of_full_class` 以整站同真实类支持量为分母。

`cross_*_mean/std/min/max`、`delta_*_mean/std/min/max` 均先按明确的 `fold` 身份收集五次计算值。标准差为样本标准差（`ddof=1`），仅描述五次源模型预测波动，不是置信区间或五个独立地理样本。`*_n_valid/n_na/positive/negative/zero` 保留有效性及未舍入方向；五次不全或存在NA时，均值、标准差、范围均为NA，不减少分母。`*_direction` 为 `all_positive/all_negative/all_zero/mixed/not_calculable`。计数仍保留零，零支持率为空单元格NA，状态为 `no_true_support`。不可计算方向不标为相等。

F1直接按 `2TP/(2TP+FP+FN)` 计算；仅该分母为0时为NA。Precision分母 `TP+FP`、Recall分母 `TP+FN` 分别判断，互不代替F1状态。`delta_f1=本站F1−跨站F1`；Precision、Recall变化为跨站减本站。各次独立计算F1后取五次平均，不合并跨站矩阵，不平均图斑或分区F1。

## 互斥边界定义

仅在原最近带 `0<d<=1` 内归组，使用参考标签四邻域直接异类接触位掩膜：bit1=玉米—其他、bit2=玉米—大豆、bit4=其他—大豆。数字是位值，不是新类别编码。研究区外框不提供异类接触位；不重新分配最近边界，不向内部传播类型，无边段ID。

| 真实类别 | contact_1_only | contact_2_only | mixed | nearest_no_direct |
|---|---|---|---|---|
| 玉米 | 仅直接接触大豆（2） | 仅直接接触其他类（1） | 两种异类同时接触（3） | 最近带无四邻域异类直接接触（0） |
| 大豆 | 仅直接接触玉米（2） | 仅直接接触其他类（4） | 两种异类同时接触（6） | 同左（0） |
| 其他类 | 仅直接接触玉米（1） | 仅直接接触大豆（4） | 两种作物同时接触（5） | 同左（0） |

`nearest_no_direct` 是已知、必须保留的第四组，不是未知类型。`boundary_group_mapping.csv` 列出全部3×8映射及 `admissible_bitmask`；不属于该真实类的接触位必须对应零矩阵行，本次逐行实际核查。重叠某类边界视图由该真实类相应仅接触组加混合组恢复，混合组只在补充重叠视图中重复出现，互斥主视图不重复。

## 文件与连接键

以下P指 `results/processed/sec33_directional_confusion_closeout/`，S指本目录。

| 文件 | 内容及唯一键 |
|---|---|
| P `crop_metrics_per_prediction.csv` | 576行；`RUN+crop`；整站TP/FN/FP、分母、F1/Precision/Recall及各自状态。本轮重算与历史有效数值核对。 |
| P `crop_metrics_summary_path_level.csv` | 108行；`model, source, target, crop`；五次指标和变化范围、方向；`larger_drop` 仅比较Recall和Precision的降幅，不是F1贡献比例。 |
| P `directional_per_prediction.csv` / S `directional_summary.csv` | 1152逐次/216汇总；`RUN+true_class+predicted_class` / 去掉`kind,fold`；六向计数及增量，完整重算并连接原主表。 |
| S `boundary_group_mapping.csv` | 24行；`true_class, bitmask`；互斥映射、接触对象及可行位组合。 |
| P `exclusive_boundary_per_prediction.csv` | 13824行；`RUN+band+bitmask+true_class+predicted_class`；最近带完整9个整数单元，`count`含对角线，不能把对角线当错误。 |
| P `exclusive_boundary_row_counts.csv` | 2304行；`RUN+band+true_class+exclusive_boundary_group`；分组完整真实类行 `pred_corn/other/soybean` 及支持量。 |
| P `exclusive_boundary_grouped_per_prediction.csv` | 4608行；上键再加`predicted_class`；四互斥组六向逐次率、本站基准和净变化。 |
| P `exclusive_boundary_leakage_per_prediction.csv` | 2304行；不含`predicted_class`的互斥组键；两个定向错误之和，率和增量均保持同一真实类分母，不是F1。 |
| S `exclusive_boundary_summary.csv` | 864行；`model, source, target, band, true_class, predicted_class, exclusive_boundary_group`；五次均值、标准差、范围、方向及参考占比。 |
| S `exclusive_boundary_reference_support.csv` | 48行；`target, true_class, exclusive_boundary_group`；只保留一份共享参考支持量。 |
| P `overlap_reconstruction_per_prediction.csv` | 3456行；`RUN+boundary_type+band+true_class+predicted_class`；由互斥组重组并核对原重叠视图；无支持率仍为NA。 |
| S `source_target_composition.csv` / `source_composition_direction_contrast.csv` | 12/216行；`source,target` / 再加`model,true_class,predicted_class`；三类整站参考像元数及占比，与六向主表一一连接。 |
| S `composition_source_order_diagnostic.csv` | 72行；`model,target,true_class,predicted_class`；固定目标比较三个来源的预测目标类整站占比与方向增量排序。`same_order/opposite_order/no_monotonic_order`仅是严格排序诊断，无相关系数或P值。 |
| S `model_crop_metrics_summary.csv` | 9行（两作物6行，其他类3行）；`model,crop`；12条路径等权；本站基准仅4个独立目标站，来源关联使每个本站值重复3次。 |
| S `model_crop_path_diagnostics.csv` / `pooled_model_influence.csv` | 72行路径级作物例外 / 8行省略一种模型的描述性均值。`leave_one_path_out_*`仅省略一条路径检查均值方向，不删除主分析预测、不作独立性检验。 |
| S `case_B_to_D_exclusive_boundary.csv` / `case_D_exclusive_all_sources.csv` | 12/36行；B→D或全部A/B/C→D的大豆→玉米四互斥组，保留三模型。 |
| S `case_D_distance_all_sources.csv` | 63行；沿用原七带大豆→玉米的全来源摘要；内部类型不外推接触位，`d>6`是开放区间。 |
| S `case_D_C3_C4_interior_all_sources.csv` | 18行；三个模型×三个来源×两种既有K4类型；`interior`为`d>1`，`delta_other_crop_rate`是大豆→玉米。类型非图斑一一配对，不代表控制组成或单个形态指标。 |
| S `case_B_D_ConvGRU_crop_metrics.csv` / P `case_B_D_soybean_to_corn_per_prediction.csv` | 3类路径指标摘要 / 五次大豆→玉米净计数变化，用于同一方向连接大豆FN和玉米FP。 |
| S `exclusive_boundary_checks.csv` / `verification.md` / `analysis_manifest.json` | 实际核查、测试与视觉检查记录；输入、脚本、产物SHA-256。清单不对自身计算哈希。 |

图件及同名数据底表位于 `figures/exploratory/sec33_directional_confusion_closeout/`；`figure_data_checks.csv`记录底表往返数值一致及同类模型面板统一纵轴。科学比较均使用17位有效数字CSV中的未舍入值。

本轮只核验已有整数矩阵及派生统计。边界位语义、标签及距离数组生成沿用历史记录，未重新读取原始空间数组或重做距离变换；距离原始生成状态继续为 `Partially verified`。

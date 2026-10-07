# K=4补充敏感性分析：来源、身份与分母

本轮为K=2主分析之后、2026-10-07开展的补充敏感性分析，性质为 **derived / exploratory**。既有K=4归属与变换未修改，未重新拟合；K=2仍为主分析。CSV保存17位有效数字，空字段为NA；方向和排序使用未舍入值，显示0.00不等于真实值为0。

## 来源与共同配置

| 输入 | 用途 |
|---|---|
| `../sec33_reference_patch_types/`对应processed目录的`cluster_candidates.csv` | 按`target,PID`读取既有`k4=1..4`，不按行序连接 |
| `cluster_parameters.json` | 既有log(AREA)、log(SHAPE)、log(ENN)、共同标准化、八个站点×作物层等权、随机种子及K=4中心 |
| `reference_patch_features.csv` | 完整参考斑块像元、五项指标、位置和外框截断标记；不使用旧128×128景观特征 |
| `frozen_patch_assignments.csv`、`frozen_configuration.json` | K=2归属与冻结状态对照 |
| `reference_full_{target}.npz` | 保存的完整标签、PID及原七距离带；验证参考支持量与代表斑块 |
| `prediction_count_index.csv`及192份`counts_*.npz` | 12份本站OOF、180份跨站；直接复用图斑级整数计数 |
| `sec33_crop_spatial_context/whole_cm.csv` | 192份恢复的完整三类矩阵对照 |

上述输入均保留原位。本轮[analysis_settings.json](../../processed/sec33_k4_sensitivity/analysis_settings.json)保存共同参数副本、日期、分析动机、归属来源及选定文件哈希。阶段`*_manifest.json`记录执行当时的输入与脚本哈希；最终`delivery_manifest.json`记录交付文件的当前字节哈希，不将阶段记录倒写为最终脚本版本。

## 参考身份与特征表

- `target`：A=`iw_2023`，B=`iw2_2023`，C=`ida_2023`，D=`il_2023`；`site`是显示用站点字母。`crop`为corn/soybean，其他类不聚类但参与计数闭合。
- `PID`是整图参考ID图中的斑块编号；`target,PID`是连接键。`patch_uid`用于额外身份核对。它不是训练图块ID，斑块也不等同于真实农业田块。
- `selected_assignments.csv`每行一个参考作物斑块，共149234行；`spatial_type=K4-C1..C4`，`k2_type=K2-T1/T2`。数值`k2,k4`仅保留源表编码。
- `reference_pixels`：完整参考斑块像元数；30 m分辨率，1像元=0.09 ha。AREA为ha，ENN及GYRATE为m，SHAPE、CONTIG无量纲。SHAPE是周长复杂程度，不是长宽比；GYRATE不是纯狭长度。类型共同涉及AREA、SHAPE及ENN，不能称为独立形状效应或识别难度等级。
- `boundary_pixels,interior_pixels,far_interior_pixels`分别为原带1、带2—7、带7的支持量；`no_interior`表示无`d>1`像元，不能填内部率0。
- `touches_outer_edge`是外框截断标记；所有斑块保留。`oof_fold_count`表示完整斑块可跨不同测试折，本站仍为既有OOF预测，不能称整块独立留出。
- `type_reference_support.csv`以`domain,target,crop,spatial_type`为键。`domain=all/crop/site_crop`分别是四站两作物合计、单作物跨站合计、单站单作物；这些视图不能重复相加。
- `n_patches,pixels,area_ha`为图斑数、像元面积、ha面积。`patch_fraction,area_fraction`的分母是同一domain、target、crop的全部四类；`singleton_fraction,no_interior_fraction,edge_patch_fraction`以该类型斑块数为分母；`boundary_share,edge_area_fraction`以该类型像元数为分母。截断覆盖不是截断造成的误差估计。
- `feature_distributions.csv`加`metric`为键，保存五项指标的最小值、5/25/50/75/95分位数、最大值及缺失数，均由实际值计算。
- `k2_k4_crosstab.csv`另以`k2_type,k4_type`区分交叉归属，同时保留图斑数和像元面积，比例以对应参考域全部作物为分母。K=4不是K=2的严格嵌套细分。
- `representative_patches.csv`的`selection_domain=crop/site_crop`区分全局作物代表和逐站候选。仅依据参考特征距保存的K4中心最近选择，外框截断斑块不作为代表图；并列时按明确身份排序。代表图不按预测误差挑选。

## 整数计数与空间位置

`prediction_index.csv`的唯一运行键为`kind,model,source,target,fold`：within为本站、source=target、fold=0；cross为跨站、source≠target、fold=1..5。它保留192份原计数文件的路径、SHA-256和`array_index`。

`k4_run_type_class_band_cm.npz`的`counts`轴为`[array_index, type, true_class, band, predicted_class]`，形状192×5×3×7×3。type=0单独存放未聚类其他类，1..4为K4；类别0/1/2为玉米/其他/大豆，band=0..6对应原七带。本轮以原`patch_band_prediction_counts[PID,band,predicted_class]`重新汇总，未把K2的`type_band_bit_cm`直接换标签；后者仅用于总体七带闭合对照。

`region=all,boundary,interior,far_interior,band_1..band_7`：

- all是全部七带；boundary为`0<d≤1`；interior为`d>1`；far_interior为`d>6`。
- band_1..7依次为`(0,1]、(1,2]、(2,3]、(3,4]、(4,5]、(5,6]、>6`像元。
- 这些是相互包含的视图，不能把所有region相加。只有边界+内部或原七带可闭合到all。
- 距离沿用历史完整参考标签共享边数组，直邻像元中心距共享边0.5像元；外框不自动当作类别边界。本轮没有重新生成距离，也没有新增边界接触类型分析。

`type_error_counts.csv`以运行键+`crop,spatial_type,region`为键，保留整数`pred_corn,pred_other,pred_soybean`。`pixels=N`是同条件真实作物支持量，`correct`是正确数，`errors=N-correct`；`other_crop_errors`是错成另一作物，`other_errors`是错成其他类，两者相加恢复errors。`n_patches_with_support`表示该位置实际有像元的斑块数，与类型斑块总数`n_patches`区分。

## 率、增量、数量与贡献

- `recall=correct/N`，`leakage=errors/N`，`other_crop_rate=other_crop_errors/N`，`other_rate=other_errors/N`。零支持量计数为0、率为NA。这些均以真实作物像元为分母，不是完整类别F1。
- `type_error_per_prediction.csv`保留所有跨站逐次值及同模型、目标、作物、类型、位置的`within_*`本站基准；`delta_*`一律为跨站减本站。两个定向率增量之和恢复漏分增量。
- `net_errors,net_other_crop_errors,net_other_errors`是对应错误数量之差，可正可负。它们不是“原本站正确、跨站变错”的配对像元数。
- `class_pixels`是目标站该作物四类总像元；`type_pixels`是该作物该类型总像元。`contribution_errors=net_errors/class_pixels`，两个定向贡献同理，表示对全站该作物漏分率差的带符号贡献。不能据此解释完整ΔF1。
- `type_error_summary.csv`按`model,source,target,crop,spatial_type,region`汇总五次；保留全部来源，不把15次当作独立地理重复。
- `*_mean,std,min,max,n_valid,positive,negative,zero,direction`分别为五次算术均值、样本标准差(ddof=1)、范围、有效次数及方向。任一次NA则均值、标准差和范围均为NA，不缩减分母。`direction=all_positive/all_negative/all_zero/mixed/not_calculable`按未舍入值判断，NA不叫相等；标准差不是置信区间。
- `valid_status`来自逐次真实支持量；汇总是否完整以每个指标的`n_valid,direction`判断，不用支持量状态替代五次指标状态。
- `C4_minus_C3_*`固定模型、来源、目标、作物、位置和预测编号，保留C3/C4支持量、基准率和逐次率，再计算C4−C3。两类属于不同参考斑块集合，是条件对照，不是图斑一一配对。
- `C4_minus_C3_within_leakage`：绝对本站难度差；`C4_minus_C3_leakage`：绝对跨站难度差；`C4_minus_C3_delta_leakage`：跨站增量差；`C4_minus_C3_net_errors`：净增数量差。其含义和权重不能互换。
- `crop_comparison_*`为同类型、位置下大豆漏分率减玉米漏分率，仍是不同真实作物集合。`crop_C3_C4_order_changes.csv`保留C3/C4下作物差及是否反向，不称调整后的F1。
- `model_source_comparisons.csv`固定目标条件后给出三模型或三来源的均值极差与顺序；未把不同目标条件混合。完整值仍在分源、分模型主表。

## 例外、图表与核查入口

- `C4_C3_nonpositive_or_mixed_inventory.csv`保留C4增量不高于C3或五次不是全正的条件；它不是删除清单。`C4_C3_main_regions_complete.csv`保留四个主位置的完整C3/C4对照。
- `comparison_direction_counts,target_crop_direction_counts,source_sign_consistency,boundary_interior_sign_patterns,direction_disagreements,crop_order_counts`是描述性覆盖统计，不能当作独立样本的显著性证据。
- `na_negative_inventory.csv`保留各位置的NA、负值、零值及混合方向；本轮K4-C1原带4—7及远内部无支持，均保留NA。C3/C4所有主位置可计算。
- `D_soybean_review.csv`及逐次表保留四类全部模型、来源；`D_C3_C4_diagnostic_per_prediction.csv`提供C3/C4四个主位置的完整五次诊断。
- `figure1_distribution_data.csv`对应图1实际分位数；`figure2_plot_data.csv`对应图2的432个条件格及五次方向。颜色按全精度，格中文字按两位小数；●表示五次严格同向，不是显著性标记。
- `*_checks.csv`只记录本次实际执行的检查；完整范围与历史限制见[核查记录](../../../verification/sec33-k4-sensitivity-2026-10-07.md)。

# 章节与证据路由

数值以 `results/summary/` 为准，定义见 [experiment-protocol.md](experiment-protocol.md)。以下路径省略 `results/` 前缀，历史核查不等于本次重验。

| 章节/问题 | 活动数据 | 使用方式 |
|---|---|---|
| 1.3组成 | `summary/sec33_indicator_grading_preparation/all_class_reference_support.csv` | 四站三类，分母为整站有效参考像元 |
| 1.3景观背景 | `summary/sec33_reference_patch_types/background_class.csv`、`background_landscape.csv` | 只用 `scope=full`，类别与景观层级分开 |
| 1.3斑块分布 | `summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv`、`reference_support_reading.csv` | 八组 `site_crop`，数量和面积权重分开 |
| 1.3.2现行表1及联合图 | `summary/sec13_landscape_display/`、`summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv` | 表1选NP、AI、ENN等权P90与整站ED；联合图复用六档AREA×四档SHAPE，分母为本站该作物总面积；不定义形态类型 |
| 3.1本站F1 | `summary/f1_raw_scale/within_site_crop_f1.csv` | 12个独立本站汇总基准 |
| 3.1折间波动 | `summary/f1_raw_scale/within_site_crop_f1_fold_stats.csv` | 不替代本站汇总F1 |
| 3.1本站错分 | `processed/sec33_directional_confusion_closeout/crop_metrics_per_prediction.csv`、`summary/sec33_directional_confusion_closeout/directional_summary.csv` | 筛本站，重复方向基准验证后去重 |
| 3.2跨站F1 | `summary/f1_raw_scale/cross_site_crop_f1_per_fold.csv`、`cross_site_crop_f1_summary.csv` | 五次分别算，再均值与样本标准差 |
| 3.2差距 | `summary/f1_raw_scale/crop_f1_difference_36paths.csv` | ΔF1=本站−跨站，存储原尺度、展示百分点 |
| 3.3方向与模型 | `summary/sec33_directional_confusion_closeout/directional_summary.csv`、`model_crop_metrics_summary.csv`、`model_crop_path_diagnostics.csv` | 六向计数、率及指标，保留逐次和路径例外 |
| 3.3位置与来源 | `summary/sec33_directional_confusion_closeout/exclusive_boundary_summary.csv`、`case_D_distance_all_sources.csv` | 互斥最近带与七带定位，不传播直接接触类型 |
| 3.3全路径七带 | `summary/sec33_round3_distance/band_metrics_summary.csv`、`summary/sec33_round3_closeout/nearest_vs_gt6_delta_e_summary.csv` | 类内漏分增量、像元权重与净贡献；最近和远内部逐次配对，均非F1 |
| 3.3完整F1分量与环境分布 | `summary/sec33_crop_spatial_context/whole_f1_error_components_summary.csv`、`distance_common_weights.csv` | 分量沿F1自身分母；共同权重只作描述性距离标准化 |
| 3.3组成限制 | `summary/sec33_directional_confusion_closeout/source_composition_direction_contrast.csv` | 固定模型目标比较来源，不等同局部邻接 |
| 3.1/3.3空间条件与错误定位 | `summary/spatial_error_conditions/`、`processed/spatial_error_conditions/` | 全路径分档、共同权重与空间子集实际贡献；条件对应与反例，边界和距离仅作定位 |
| 3.3条件性发现（C/D大豆） | `summary/spatial_findings_refinement/`、`processed/spatial_findings_refinement/` | 共同A/B来源下，高SHAPE组跨站额外漏分对照C为正、D为负；三套分层不可混合，不称独立形状效应 |
| 3.1/3.3模型优势与跨站保持 | `summary/model_advantage_spatial_conditions/`、`processed/model_advantage_spatial_conditions/` | 优势=ConvGRU漏分率减对照模型漏分率；本站16比较、48条跨站路径；完整F1见`complete_F1_comparisons.csv`，不以漏分排序替代 |
| 完整斑块条件探索 | `summary/sec33_reference_patch_types/`、`summary/sec33_k4_sensitivity/` | 配置、逐次、支持和图件原位恢复；作为已有补充探索，不自动确定论文主方案 |
| 共同五档候选 | `summary/sec33_common_five_grades/` | 仅参考支持、待审阅；没有等级错误结果 |

当前顺序见 [outline.md](outline.md)，判断见 [3.3证据总览](../results/summary/sec33_evidence_overview.md)。

## 正式图表

| 内容 | 保留产物 |
|---|---|
| 景观格局表1 | `tables/sec13_landscape_context_rows.tex`；`scripts/generate_sec13_landscape_display.py` |
| 面积—形状联合分布 | `figures/study_area/fig_sec13_area_shape_joint{,_a,_b}.pdf`及同名`.tex`拼版；旧v3保留 |
| 本站F1 | `figures/results/fig_within_site_f1_{a,b}.pdf` |
| D站本站示例 | `figures/results/fig_within_site_map_D_{a..h}.pdf` |
| 12路径跨站F1 | `tables/table2_cross_site_f1_12paths.csv`及 `_rows.tex` |
| ΔF1 | `figures/results/fig_degradation_heatmap_{a..f,cbar}.pdf` |

正文在 `sections/04_results.tex` 引用；F1及标准差显示百分数，差值显示百分点。`scripts/generate_core_tables.py`生成展示表及`tables/f1_text_values.tex`正文数值；两绘图入口分别为`plot_within_site_f1.py`、`plot_degradation_heatmap.py`，共用`scripts/f1_display.py`。`tables/table2_cross_site_f1_12paths.csv`为带单位的展示CSV，计算仍读取正式summary。探索图不自动进入论文。

## 底表与分母

`processed/sec33_crop_spatial_context/whole_cm.csv`保留192套完整矩阵。完整斑块特征、数组和计数在 `processed/sec33_reference_patch_types/`，连接键 `target,PID`，预测键 `kind,model,source,target,fold`。

两个定向漏分率之和恢复该类漏分率，不能恢复F1；FN与FP由完整矩阵闭合。五次不合并替代指标均值，NA不减少次数，负值保留。

原 `sec33_directional_confusion`保留修正输入及有效距离、组成对照。累计440份原文件已恢复，当前用途见[复用入口](../results/summary/reuse-status.md)；[第二次恢复记录](../archive/2026-10-10-mainline/restored-second-pass.csv)明确413项理由，旧轮次任务不因此重启。192份`sec33_crop_spatial_context/joint_*.npz`的分区汇总与整图计数相同，可用作整站计数核对；`patch_id`是存储图块号，不能连接完整参考斑块`PID`。

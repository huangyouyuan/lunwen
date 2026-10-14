# 成果用途与复用入口

2026-10-15用途复核：缩小仓库计划已取消，[额外副本及配套流程](../../archive/2026-10-15-cancel-remote-plan/README.md)归档。科研成果和下面的科学追溯链全部原位保留，不按大小或是否进入正文归档。下方2026-10-11的恢复核查是历史记录；基础整理、后续空间分析和1.3修订已完成，不能据其旧“下一步”重复执行。

当前阅读顺序是：1.3现行展示及基础表 → 本站模型优势主表 → 全路径跨站保持与固定D来源对照；完整章节取舍见[交接](../../HANDOVER.md)。3.1必要补充与3.3正文仍待写，不再遍历指标寻找统一主因。

更新：2026-10-11，整理前基线`a70e11b`，本版范围见[版本说明](../../plan/version-notes-2026-10-11.md)。这里区分“文件值得保留”与“方案是否用于论文”。有效结果不因来自旧轮次而失去价值；本次未生成新科研结果，也未批准等级候选。

## 当前证据与可复用探索

| 层级 | 入口 | 可直接复用什么 | 解释和执行边界 |
|---|---|---|---|
| 当前1.3展示与本站基础 | [现行表1及联合图](sec13_landscape_display/README.md)、[联合份额v3](area_shape_joint_bubbles_v3/area_shape_joint_bins.csv)、[基础表](sec13_sec31_foundations/README.md) | 四站组成、联合面积份额、NP/AI/ENN P90/ED及12个本站基准 | 1.3已完成，不再以旧表主导叙述；旧中位数、极值、PD及图表仍可复核 |
| 当前3.1/3.3优先证据 | [模型优势主表](model_advantage_spatial_conditions/main_reading_table.md)、[路径表](model_advantage_spatial_conditions/cross_path_overview.csv) | 16个本站模型比较、48条跨站对照、同支持距离权重及五次方向 | 先补本站参照，再追踪固定D换来源的优势变化；漏分优势不能替代完整F1 |
| 针对性补充与反例 | [发现提炼](spatial_findings_refinement/README.md)、[全路径空间条件](spatial_error_conditions/README.md) | C/D大豆共同来源与支持、自然计数、四站完整条件表 | 已完成统计，不重做整轮分析；三套权重不混合，形状关联不写成独立作用 |
| 当前数值基准 | [正式F1](f1_raw_scale/crop_f1_difference_36paths.csv)、[定向收尾](sec33_directional_confusion_closeout/README.md) | 原尺度F1/ΔF1、六向错分、模型分层、六向组成、互斥最近带 | 后续修正优先于旧重叠视图或缺两方向的旧组成表 |
| 基础参考 | [整图斑块字典](sec33_reference_patch_types/data_dictionary.md)、[分布](sec33_indicator_grading_preparation/README.md) | 完整参考斑块、192份预测计数、参考数组、整站背景与两种权重分布 | `target,PID`连接；完整斑块不同于存储图块和真实田块 |
| 已有距离证据 | [七带字典](sec33_round3_distance/data_dictionary.md)、[增量配对](sec33_round3_closeout/data_dictionary.md) | 七带整数矩阵、类内漏分率/净贡献、逐次两端Δe、D站五次诊断与原图 | 绝对漏分率配对和Δe配对分别保留，不相互替代；>6是开放远内部 |
| 完整斑块补充探索 | [K2报告](sec33_reference_patch_types/exploration-report.md)、[K4报告](sec33_k4_sensitivity/exploration-report.md) | 冻结配置/归属、四站两作物逐次计数、类型支持、边界/内部、整块漏识别、全部反例和探索图 | 原报告的“K2主分析”是当时安排，不是当前强制主方案；K4不是K2严格嵌套；不能把同类当成面积形状与组成均已控制 |
| 未批准的参考候选 | [五档原交付](sec33_common_five_grades/README.md)、[本次状态](sec33_common_five_grades/USE_STATUS.md) | AREA小值段、ENN集中值、共同阈值候选、支持量和逐PID候选归属 | 待审阅、未冻结；没有等级错误率结果。恢复不代表认可其面积分布合理或决定下一步沿用 |
| 整站空间交叉计数 | [联合底表说明](../processed/sec33_crop_spatial_context/README.md)、[位码×七带CM](../processed/sec33_crop_spatial_context/type_band_cm.csv) | 192份`cm[400,7,8,3,3]`、参考数组、身份索引；可直接恢复整站定向/位码/距离统计 | 400是存储分区，求和后是整站像元计数，不赋予128×128景观分析意义；图块号不能连接完整斑块PID |
| 描述性标准化与完整分量 | [距离共同权重](sec33_crop_spatial_context/distance_common_weights.csv)、[完整F1分量](sec33_crop_spatial_context/whole_f1_error_components_summary.csv) | 环境分布和条件错误的描述性对照，两个漏分与两个误分入分量 | 标准化漏分率不是F1；F1分量用自身分母，不是因果贡献 |

类型结果、候选、参考分布不是三种互相替代的证据。1.3可直接复用整站参考背景与连续分布；3.1可直接复用本站矩阵、完整指标和六向错误；3.3可按明确比较复用已有位置和类型证据，不必重新做整轮统计。

本轮暂不投入新的统计：K2/K4重新聚类、共同五档冻结与等级错误、ENN及整站指标的全面扩展。它们的原统计、候选、支持量、字典和核查均保留；ENN中位数相同不表示无信息，AI/ED/NP也不能复制为斑块级独立样本。旧表生成器、探索图和已完成任务记录仍有引用或复现用途，继续原位保存，只按历史用途阅读，不自动执行旧计划。

## 为什么仍保留一部分归档

旧DR/百分比退化、被正式F1链取代的重复输出，以及图块AREA_MN分组、图块组成匹配结果继续作为历史。它们有追溯价值，但不能混充完整参考斑块分析。定向混淆旧主图中的重叠边界不再是主要比较，旧四向组成表不代表六向覆盖；当前收尾结果优先。

本次仍保留部分按位并集的方向统计作为补充，原位码0—7底表互斥完备。按位并集可重叠，三种边界贡献不能相加。`reference_type_band_support.csv`里的`patches`是涉及存储图块数，不能与完整斑块支持量混用。

历史任务不恢复为活动待办。K2/K4与候选原报告、清单按原字节恢复，里面的当时路径、命令与结论状态不改写；若路径在原位不存在，用[有效位置清单](../../archive/2026-10-10-mainline/effective-locations.csv)定位。该清单同时列出归档和恢复项，不能只看初次迁移表。

## 可复用源码怎样查

旧生产脚本仍以`.source`保存完整原字节。保留历史状态的原因是它们包含原输出目录、阶段写入和旧依赖，不是认为所有函数都无价值。此次不恢复可执行入口、不重跑这些流程；若后续需要重汇总，先复用表，确有缺项再提取经过检查的只读函数并写入独立新目录。

| 源码入口 | 已查到的可复用内容 | 不能直接做什么 |
|---|---|---|
| [完整斑块](../../archive/2026-10-10-mainline/history/scripts/explore_sec33_reference_patch_types.py.source) | `component_mapping`、`count_patch_prediction`、`rates`、`join_baseline`、`strict_summary` | 不重启prepare/cluster/freeze/count或覆盖原统计 |
| [K4](../../archive/2026-10-10-mainline/history/scripts/explore_sec33_k4_sensitivity.py.source) | `join_assignments`、`aggregate_array`、`contrast_types` | 不把既有K4重汇总改成重新聚类，也不改冻结配置 |
| [分布准备](../../archive/2026-10-10-mainline/history/scripts/prepare_sec33_indicator_grading.py.source) | `value_frequency`、`inverse_ecdf`、`cdf_gap` | 不平均旧分位数或无故重建分布表 |
| [五档候选](../../archive/2026-10-10-mainline/history/scripts/prepare_sec33_common_five_grades.py.source) | `pixel_cuts`、`classify`、`assign`、`support_rows`；有防覆写检查 | 不把恢复等同于批准断点，不依据误差选最优切点 |
| [距离与增量配对](../../archive/2026-10-10-mainline/history/scripts/close_sec33_round3_distance.py.source) | 已有逐次配对及五次诊断的来源 | 不重写历史输出，不将绝对率配对冒充Δe |

## 本次核查到哪一步

归档哈希与恢复原字节检查覆盖所有移动文件。对192个完整预测身份，逐项比较旧存储分区联合CM和整图类型CM的全部`7×8×3×3`整数单元，完全一致。这证明两种保存方式可恢复同一整站联合计数，不证明旧图块形态分析适合作为当前单位。

恢复归属按明确`target,PID`核对参考身份及类型/等级支持；原距离生成、FRAGSTATS工程配置、预测重新推理均没有执行或重新认证。详细范围见[第二次复用核查](../../verification/second-pass-reuse-2026-10-11.md)。接下来仍是[1.3与3.1基础材料计划](../../plan/tasks/2026-10-10-sec13-sec31-foundations.md)，本次恢复本身没有执行该计划。

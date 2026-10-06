# 微观空间解释探索数据字典

所有结果均为derived / exploratory，不自动进入正文。CSV保留17位有效数字；空字段表示NA，不是0。报告显示两位小数，所有比较、排序、方向和计数使用未舍入值。小正/负数可显示为0.00。

## 身份与组织

基本运行键`kind,model,source,target,fold`：本站`kind=within,source=target,fold=0`，代表全部独立测试图块的汇总；跨站`kind=cross,source!=target,fold=1..5`。类名`corn,other,soybean`对应0、1、2。`band`为七带原码`0<d<=1`…`5<d<=6,d>6`。本站率按同条件整数CM求和后算；跨站每次分别算，再取五次算术均值和样本标准差ddof=1。没有三源合并或15次独立重复。

每个summary唯一键为`model,source,target`加以下条件字段；本站列因三个来源而重复，汇总本站统计时必须按`model,target`及条件去重。每个per_prediction唯一键为基本运行键加条件。总表目录、行数、字段见[table_catalog.csv](table_catalog.csv)。

| 文件族 | 条件字段与用途 |
|---|---|
| processed `reference_{target}.npz`、`metadata_{target}.csv` | `patch_id`对应数组第0轴；labels/pair_bits/bands形状400×128×128，support为400×7×8×3；patch_uid、fold_id保留 |
| processed `joint_*.npz`、`joint_counts_index.csv` | cm形状400×7×8×3×3，最后两轴是真实、预测类别；计数为整数。12份本站+180份跨站；本站每图块只含一次测试 |
| processed `type_band_cm.csv` | 基本运行键+band+bitmask；0—7互斥位组合，包含全零空条件，9个`cm_i_j`字段 |
| `whole_class_*`、`whole_direction_*`、`whole_cm.csv` | 全站完整CM及三类精度/六种有向错误；class条件crop，direction条件true_class,predicted_class |
| `crop_gap_*` | 每运行的玉米−大豆F1/Precision/Recall差；leakage_gap特意定义为大豆−玉米，详见下文 |
| `whole_f1_error_components_*` | crop+role+other_class；四项F1误差分量，包含进入该类的两种假阳性 |
| `distance_class_*`、`distance_direction_*` | band+crop或band+两类方向；完整三类CM，不是仅裁出真实作物像元后计算F1 |
| `exclusive_type_direction_*`、`exclusive_type_contribution_per_prediction.csv` | band+bitmask+两类方向；贡献可按互斥类型、七带相加 |
| `type_direction_*`、`type_contribution_per_prediction.csv` | boundary_type+band+两类方向；按位并集存在重叠，role说明向对侧、第三类或非该类型的参考侧 |
| `reference_type_band_support.csv`、`inclusive_type_reference_support.csv` | target+类型+band+true_class；pixels/reference_pixels、patches、class_total、pixel_share。参考标签决定，各模型/来源相同 |
| `boundary_asymmetry_*`、`boundary_absolute_asymmetry_summary.csv` | boundary_type+band+first_side+second_side；按同运行编号连接两侧，不是按边段配对 |
| `distance_common_weights.csv` | target+band；两作物真实像元数、分布、共同支持、common_weight和coverage |
| `distance_weighted_*`、`weighted_crop_gap_*` | crop或作物差；full_original、shared_original、common_weighted三种描述性漏分率/增量 |
| `area_*`、`area_high_low_*` | grouping_crop+group+方向/评价crop；grouping_crop决定冻结分组，不是被评价类别的筛选条件。保留缺类组。高低表按显式身份连接 |
| `frozen_group_features_reused.csv` | 复用第一轮组身份、阈值、像元组成、AREA_MN实测中位数/范围；group键可连接本轮AREA表 |
| `fixed_matches.csv`、`comparison_rules.csv` | contrast+pair_id及两侧patch_uid/id；仅参考特征决定的配对，不用错误结果选阈值 |
| `matched_*` | contrast+side+方向/评价crop；两侧完整CM汇总后求率，不平均图块F1或图块错误率 |
| `matched_location_*` | 再加location+band，location为all_types或原类型；同一批选中patch的联合CM。all_types七带可相加，原类型不可彼此相加 |
| `*_contrast_*` | right_minus_left_rate为右组率−左组率；其delta为跨站组间差−本站组间差；逐次按fold连接 |
| `directed_endpoints_*` | true_class+predicted_class；显式运行键连接最近和>6带，保留原率和增量。summary的delta_interior_minus_near_rate是两端额外错分的差 |
| `figure{1,2,3}_plot_data.csv` | 每个实际图中观测点的身份和值；范围来自五次逐值，不是置信区间 |
| `*_exceptions.csv`、`scientific_counts.json` | 全部玉米F1优势例外、F1与漏分排序冲突、边界第三类错误占优例外；报告计数可直接复核 |

`area_feature_distributions.csv`保留三类图块组成、AREA_MN、ED、AI的实测范围；`area_ai_rank_redundancy_reused.csv`为第一轮秩相关记录的原样副本，未新算P值。选中图块的特征残差和支持覆盖分别在`matched_feature_distributions.csv`、`matched_support_coverage.csv`，没有把图块指标当成像元距离。

## 分母、差值与有效状态

- `pixels=N`为条件内真实类别像元数；`errors=CM[c,j]`；`rate=errors/N`。同类的两个有向率之和为leakage=1−Recall。**只看真实作物子集的rate不是F1。**
- Precision=TP/(TP+FP)，Recall=TP/(TP+FN)，F1=2TP/Z，Z=2TP+FP+FN=N+预测为该类像元数。Precision和Recall各按自己的分母处理NA；真实类缺失但有假阳性时F1=0；Z=0才是F1的NA。
- 所有`delta_f1`为本站−跨站；其他普通`delta_*`均为跨站−本站。特别是`delta_f1_gap`指玉米−大豆F1差在跨站后的变化，不是某作物的ΔF1。恒等式为`cross_f1_gap=within_f1_gap+soybean_delta_f1−corn_delta_f1`。
- `fn_component=(FN/Z)`、`fp_component=(FP/Z)`。`whole_f1_error_components`中的outgoing(c→j)=CM[c,j]/Zc，incoming(j→c)=CM[j,c]/Zc；四项和=1−F1，四项跨站−本站增量和=ΔF1。跨站每次各用自己的Z，再平均。它们是误差分量，不是因果贡献，也不是按真实类分母归一的定向错误率。
- direction表中的`f1_fn_component`仅为该true_class的外出分量；不可把它当作接收类别的假阳性分量。完整接收分量请读`whole_f1_error_components`。`crop_gap`中的fn/fp_component_gap均为大豆分量−玉米分量，两项相加=玉米F1−大豆F1。
- `pixel_share=N条件/N全站同类`。`net_added_errors=平均跨站错误数−本站错误数`；`net_class_error_contribution=net_added_errors/N全站同类`，有效支持时等于pixel_share×delta_rate。空条件的错误计数和贡献为0，条件错误率仍为NA。净增数量不是逐像元“原本正确后变错”数量。
- `within_*`为同模型同目标同条件基准，`cross_*_mean/std`为完整五次结果。`n_valid_*`数有效逐次值，`*_status`同时考虑本站基准；`delta_*_direction`记录全部正、全部负、全部零、混合或不可计算。不可计算不标成相等，不以少于五次值计算均值或标准差。
- `boundary_asymmetry`为第二侧→第一侧率减第一侧→第二侧率：corn_soybean为大豆→玉米减玉米→大豆；corn_other为其他→玉米减玉米→其他；other_soybean为大豆→其他减其他→大豆。signed增量、均值绝对值变大、逐次绝对值的平均是三个不同统计；`boundary_absolute_asymmetry_summary`保存最后一种，不能互换。
- `weighted_crop_gap`统一为大豆漏分率−玉米漏分率；其delta为两作物漏分增量之差。共同支持带须两类N>0，各自归一后取两分布算术平均；零权重的NA不进入和式，正权重NA则结果NA。本次四站七带均有两作物支持，coverage均为1，full_original=shared_original。不是调整F1或组成/结构因果分解。

## 有限条件对照

两方案都仅针对D站大豆。方案A以冻结AREA_MN低、高组为候选，玉米和大豆占比各差≤0.05；30对图块。方案B取其他类占比下、上三分位（q1=0.0966796875，q2=0.22200520833333309），大豆AREA_MN比≤1.10；36对。特征距离线性指派保证最大有效配对数后最小特征差，不放回，排序固定，不按模型/来源重新选图块。两侧始终汇总完整CM；同组中的不同参考类别分别使用其真实支持量。不能称组成完全受控，不能将两个不同方案当作同一批图块的实验干预。

## 核查及运行清单

`prepare/count/analyze/diagnose/plot_checks.csv`只记录各阶段实际完成的检查；9项内存单元测试另见verification。原始距离生成、历史复合指纹、FRAGSTATS未重算，限制见[资产清单](asset-and-definition-inventory.md)。阶段manifest保存当阶段输入与当时磁盘源码的哈希，脚本之后增加诊断和绘图不代表之前阶段重新运行。最终源码、全部产物和文档以`delivery_manifest.json`记录；不将旧阶段源码哈希冒充最终源版本的完整重跑。

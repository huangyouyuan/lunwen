# 分档、分母、共同支持与文件定义

本批结果为derived / exploratory；不是分类实验的新运行，也不是因果效应估计。CSV保存17位有效数字，空值表示NA，零计数仍保存。计算使用原精度。

## 身份与空间单位

- A/B/C/D = `iw_2023/iw2_2023/ida_2023/il_2023`。`kind,model,source,target,fold`定义预测；本站`within,source=target,fold=0`是五折测试完整汇总，跨站`cross,fold=1..5`是五个源模型分别覆盖同一目标站。
- `target,PID`连接完整参考斑块与NPZ内的显式`PID`数组。本轮不按CSV行号连接。斑块是整图30 m参考标签8邻域同类组件，不是农业田块，不是128×128图块。
- 全部187,372个三类斑块参与整站闭合；其中149,234个作物斑块参与形态分组。单像元和外框斑块全部保留。
- AREA单位ha，1像元=0.09 ha；SHAPE无量纲；ENN单位m。本轮三项均无缺失，`feature_status=valid`。脚本遇到缺失、不合法值或未覆盖值会停止，不默默删行。未来出现缺失时需另行定义NA组，不能直接套本次对照。
- ENN为窗口内最近另一个同类斑块的边界像元中心距离。七带是像元到参考类别交界的距离，二者不同；最近带也不等于直接四邻域异类接触。

## 统一探索分档

| 变量 | 区间 |
|---|---|
| AREA / ha | `<10`, `10-<50`, `50-<100`, `100-<200`, `200-<500`, `>=500` |
| SHAPE | `1-<1.5`, `1.5-<2`, `2-<3`, `>=3` |
| ENN / m | `60-<90`, `90-<120`, `120-<180`, `>=180` |
| 七距离带 / 像元 | `0<d<=1`, `1<d<=2`, …, `5<d<=6`, `d>6` |
| 对照用三段距离 | `0<d<=1`, `1<d<=6`, `d>6` |

AREA和SHAPE沿用现有气泡图；ENN按30 m网格的直观距离阈值选探索区间，未用误差优化切点，也不称为形态类别。指标值恰等于切点时进入右档。所有站和作物用同一组阈值。

`scheme`包括`all,area,shape,enn,area_shape,area_shape_enn,distance,area_shape_distance`；`group`以`|`依次连接标签。每种scheme内部互斥完备；不同scheme之间重叠，贡献不能相加。斑块可跨多个距离带，距离分组的`patch_count`是向该组贡献至少一个像元的斑块数，**跨距离组不能加斑块数**。其参考像元和错误计数则严格闭合。

## 参考支持与作物组内指标

`reference_group_support.csv`每目标×作物×scheme×group一行：

- `patch_count`、`reference_pixels`、`area_ha`；`area_share=该组参考像元/该站该作物全部参考像元`，值域0—1，各scheme内合计1。
- `singleton_patch_count`保留单像元支持，`outer_edge_patch_count/outer_edge_pixels`保留外框支持；未排除这些斑块。
- 距离组的面积是该组内像元面积，不是所有相交斑块的完整面积。

`group_metrics_per_prediction.csv`在此支持上连接预测与同模型目标本站基准：

- `to_corn/to_other/to_soybean`是三类预测计数，包含正确预测那一列；不能把三列都叫错误。`fn`是两条错误方向的和，`to_other_crop`是另一种作物的错误计数。
- `omission_rate=fn/reference_pixels`；`to_other_rate`与`to_other_crop_rate`相加等于漏分率。`within_*`来自独立本站汇总；`delta_*_rate=跨站率−本站率`。这些率可乘100显示为百分比，增量可显示为百分点。
- `omission_contribution=组FN/整站该作物参考像元`；`net_omission_contribution=(组跨站FN−组本站FN)/整站该作物参考像元`。同scheme内分别相加恢复全作物漏分率及其增量，可显示百分点。
- `error_share=组FN/全作物FN`；`net_error_share=组FN净变化/全作物FN净变化`。后者是带符号净贡献比例，可负或大于1；分母为0记NA，不是“新增错误像元占比”。
- 不计算分组F1，因为真作物分组没有完整FP。无参考支持时错误率和增量NA，但计数、相对全作物的贡献为0。

`within_group_metrics.csv`仅本站；`cross_group_metrics.csv`按模型、来源、目标、作物、scheme、group保存五次统计。`*_mean/std/min/max/n_valid/positive/negative/zero/direction`中，std使用ddof=1；必须五次全有效才给均值/标准差，不能少一次算四次。正负次数针对该列自身；判断退化符号看`delta_*`。本站复制为每条路径的比较基准，不增加独立基准数。

## 完整F1和六方向

`whole_crop_per_prediction.csv`及两张whole summary保留三类的TP、FN、FP、精确率、召回率和F1。`delta_f1=本站F1−跨站F1`；`delta_recall/delta_precision=跨站−本站`。F1只从完整三类矩阵计算。

`fn_loss=FN/(2TP+FN+FP)`、`fp_loss=FP/(2TP+FN+FP)`，二者和为`1−F1`；跨站减本站后的`delta_fn_loss+delta_fp_loss=delta_f1`。这是F1损失的代数分解，分母也会变化，不是仅改变FN或FP的反事实影响。

`six_directions*`保留玉米→其它地类、玉米→大豆、其它地类→玉米、其它地类→大豆、大豆→玉米、大豆→其它地类。定向率分母为真实来源类别像元；跨方向比较“净增最多”使用`delta_errors`整数/均值，不能直接比较不同分母的率。`delta_count_rank`在同一次预测或同模型路径五次均值内排序。

`direction_location*`把已有七带统计合并为三个互斥段，保留其它地类真值：`rate`分母是相应真实类别在该距离段的像元，`net_direction_contribution`分母是该真实类别全站像元。这样可以定位作物FP从哪个真实类别、哪个距离段进入，而不把它放进被预测作物的斑块形态组。

## 条件对照：两组用相同权重

| `contrast_name` | high−low的定义 | 共同分层 |
|---|---|---|
| `area_control_shape` | AREA≥50 ha − AREA<50 ha | 四档SHAPE |
| `area_control_shape_distance` | 同上 | 四档SHAPE×三段距离 |
| `shape_control_area` | SHAPE≥2 − SHAPE<2 | 六档AREA |
| `shape_control_area_distance` | 同上 | 六档AREA×三段距离 |
| `enn_control_area_shape` | ENN≥90 m − ENN<90 m | 六档AREA×四档SHAPE |
| `enn_control_area_shape_distance` | 同上 | 六档AREA×四档SHAPE×三段距离 |

仅为明确问题所作的可读对照，不宣称存在50 ha、SHAPE=2或90 m的自然阈值。主规则`primary`要求每个参与层、每组至少10个贡献斑块和1000参考像元（90 ha）；`all_supported`仅要求每组至少1斑块、1像元，检验支持门槛敏感性。两种规则均与错误结果无关。门槛不意味着样本独立或统计显著。

每个站×作物固定参考集合：令两组在层k的全组面积份额为q低,k与q高,k，共同权重为`min(q低,k,q高,k)`在合格层重新归一化。两组错误率用同一权重加权。`contrast=high_standard_rate−low_standard_rate`；`delta_contrast=跨站contrast−本站contrast`。后者比较哪组额外漏分更多，不等同哪组绝对错误率高。

`low/high_coverage`分别为低/高组保留像元占各自全组的比例；`overlap_mass`为归一化前重叠份额之和。两个coverage不能互相替代。`conditional_support_weights.csv`逐层保存支持、排除标记和权重；`stratum`从0开始，按控制变量的上述顺序编码，距离为最内层：shape或area档号；area×shape为`a*4+s`；若有距离，则再乘3加d。原始分档的全部支持仍在`reference_group_support.csv`。

这些比较只让粗分档和距离段的面积权重一致，没有让档内连续值、局部邻接、影像和时序特征完全相同。加入距离后对照减弱不能直接转成“边界中介效应占比”；保留集合与权重也可能改变。

## 四站相同权重与差距分解

每作物分别对`AREA×SHAPE`、再加三段距离、或再加四档ENN做四站共同支持：每个层在四站均达到相同primary或all_supported门槛才保留。每站先按其保留像元归一化；四站组成份额的算术均值作为共同权重，每站等权，不让大作物面积站支配权重。

`raw_rate`使用全站该作物；`retained_native_rate`只使用共同支持、保留原站组成；`standardized_rate`在共同支持上换成统一组成；`coverage`为该站全作物保留比例。本站/跨站模型均用同一参考权重。跨站来源固定后可比较其余目标；三来源平均的目标比较不是严格相同源集合。

`within_site_gap_decomposition.csv`按站2减站1，在保留范围内精确分解：

`差距 = Σ[(w2−w1)(r1+r2)/2] + Σ[(r2−r1)(w1+w2)/2]`。

第一项`composition_component`表示条件占比差别，第二项`condition_rate_component`表示同分档错误率差别；二者是对称的算术分解，不是因果解释份额。`standardized_gap`另用上述四站共同权重，因此不要求等于第二项。不得拿保留范围的分解直接除全站F1差距。

## 精简阅读表

`reading_*spatial_subsets`组合原始分档便于阅读。子集`area_lt10`包含于`area_lt50`，`far_gt6`包含于`interior_gt1`，不同子集不能全部相加。跨站的`ratio_of_mean_net_counts`是**五次组计数净变化均值/五次全作物计数净变化均值**，不同于`cross_group_metrics.csv`中逐次净比例的平均。报告的总体贡献比较使用前者，并明确限定全作物平均净变化为正的68组；其余4组原值保留。

`reading_target_cross_means`按目标站对三来源路径等权，先各路径五次统计，再三路径平均；只描述既有实验。`reading_condition_consistency`数的是12个本站模型—目标组合或36个跨站模型—路径组合，不把两作物、站点或五次重复当作独立地理样本。

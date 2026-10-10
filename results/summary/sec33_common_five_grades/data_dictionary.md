# 共同五档数据字典与下一轮接口

## 对象与来源

全部结果为derived / exploratory，阈值状态为`pending_author_review_not_frozen`。来源是完整参考标签上8邻域同类连通斑块的既有`reference_patch_features.csv`；唯一键`target,PID`，辅助身份`patch_uid`。A/B/C/D依次为`iw_2023/iw2_2023/ida_2023/il_2023`。作物编码`corn=玉米,soybean=大豆`；`other=其他类`在原特征和三类总量表保留，不进入主体作物等级。

AREA单位ha，SHAPE无量纲，ENN单位m；1像元=0.09 ha。各站整幅参考图为6553600像元。总体作物149234斑块、19426296像元；其他类38138斑块。标签版本、原软件指标和距离的来源限制沿用历史记录，本轮没有重生成或把历史状态升级。

## 配置、定义及归属

`candidate_config.json`记录唯一推荐及唯一备选。`recommended`的AREA名义上界为1/10/50/150 ha，按十进制`floor(阈值/0.09)`实现为11/111/555/1666像元；`area_ecdf_alternative`使用总体面积ECDF的20/40/60/80%观测分位点。两个方案的SHAPE定义相同且单独应用，不是综合分型。

`grade_definitions.csv`唯一键`scheme,metric,grade_number`，20行。`grade_number=1..5`，`grade=Ⅰ..Ⅴ`；AREA原值增大、SHAPE原值减小。`raw_lower,raw_upper`及`lower_inclusive,upper_inclusive,upper_unbounded`定义名义原值区间；开放上界空白配合`upper_unbounded=true`，不是缺失指标。SHAPE首个升序区间含物理最小值1，其余左开右闭，再逆向编号。AREA按`pixel_min_inclusive,pixel_max_inclusive`整数闭区间归属；开放上界空白。`attainable_upper_ha`是栅格可达到的上端，区别名义切点。`spatial_meaning,value_direction,cut_basis,scheme_status`明确空间方向、依据和待审阅状态。

`processed/patch_grade_assignments.csv`149234行，键`target,PID`；保存原`AREA,SHAPE,ENN`及`reference_pixels,boundary_pixels,interior_pixels,far_interior_pixels`、`singleton,no_interior,touches_outer_edge`。列`AREA_recommended_number/grade/status`等分别表示指标与方案的编号、显示标签、`valid`或`missing_or_invalid_metric`状态。SHAPE两方案列有意相同，不代表第二次独立分级。缺失、不合理值（包括SHAPE<1）或AREA—像元不一致时编号和标签为空，不填零；内部函数的0仅是无效哨兵，不写成等级。

`processed/invalid_metric_records.csv`记录`scheme,metric,target,crop,PID,value,reference_pixels,missing_reason`，当前0行但保留列头。`excluded_reference_support.csv`36行（2方案×2指标×9域），保留排除数量与像元量，当前全部为0。

## 支持量与覆盖

`grade_support.csv`180行，键`scheme,metric,domain,target,crop,grade_number`。`domain=all`为四站两作物去重合计；`site_crop`为八个单站单作物域。同一方案和指标下八层可合成总体，但不能再把总体行加入，也不能混加两指标或两方案。

| 字段 | 定义与分母 |
|---|---|
| `n_patches,pixels,area_ha` | 等级斑块数、参考像元整数和、像元数×0.09 ha |
| `domain_n_patches,domain_pixels` | 对应总体或站点作物域的全部数量/像元，包含潜在无效记录 |
| `valid_n_patches,valid_pixels` | 当前指标有效归档记录的数量/像元；不替换域总分母 |
| `patch_share,area_share` | 等级数量/域总数量、等级像元/域总像元；当前无排除，五档各自加和为1 |
| `singleton_count` | 参考像元数等于1的斑块数；单像元像元数与该数量相同 |
| `no_interior_patches,with_interior_patches` | `d>1`像元为0、>0的完整斑块数；互补恢复本档斑块数 |
| `edge_patches,edge_pixels` | 触研究区外框的完整斑块数，以及这些斑块全部像元和，后者不是“外框像元数” |
| `boundary_pixels,interior_pixels,far_interior_pixels` | 原七带第一带`0<d≤1`、后六带`d>1`、第七带`d>6`的支持整数；前两项互斥完整，远内部包含在内部 |
| `boundary_share` | 本档边界像元/本档全部像元，零支持时NA，不是边界错误率 |
| `support_status` | `has_reference_support`或`zero_reference_support`；零计数/面积占比表示实际零参考支持，不能作零误差 |

单像元、无内部、触外框标记可能重叠，不能加总为独立分组。`all_class_reference_inventory.csv`12行，键`target,crop`，保留三类对应上述整数支持及是否进入作物候选分级；各站三类恢复6553600像元。

`five_grade_coverage_comparison.csv`20行，键`scheme,metric,grade_number`，列`A_corn_n_patches/pixels/patch_share/area_share`等覆盖八层。`coverage_diagnostics.csv`20行给出八层数量最小/最大及所在层、层内面积占比范围、空层数；`largest_stratum_share_of_grade_pixels`的分母是该档全域像元，`largest_site_share_of_grade_pixels`先合并该站两作物再除以该档全域像元。它们与某层内部的`area_share`不是同一分母。未设置充分性或稳健性人为阈值。

## 分布依据

旧`value_frequency_cumulative.csv`按完整实际取值聚合，读取采用`round_trip`；未按显示小数舍入。`area_small_value_frequency.csv`只是摘录其中`metric=AREA,domain=all/site_crop,value≤13.77`行，加`source,current_action`说明，原计数/CDF及分母不变，绝不能因摘录而重归一化。未复制`crop`域，以免混加包含关系。

`area_small_interval_support.csv`72行（9域×8诊断段），以像元上端1/4/11/33/55/111/153及开放尾段分开小值；按实际参考支持汇总，`purpose`明确不是主体等级。`patch_share,area_share`仍除以全部对应域，不除以≤13.77子域。包括尾段时闭合全域。

`cutpoint_reference_quantiles.csv`216行（9域×3指标×2权重×4概率），键`domain,target,crop,metric,weighting,probability`。两种权重均用精确频数的ECDF左逆：最小实际值，使累计整数权重首次达到q。`patch_count_ecdf`用同值斑块数，`reference_pixel_area`用同值参考像元数。前者是本轮用于候选诊断的离散分位点，与上轮`indicator_distribution_reading.csv`的斑块等权**线性插值**分位数算法不同；没有修改旧表，也没有把两者当作同算法冲突。后者与旧面积加权定义一致。同值跨过多个分位数时允许切点相同，不分拆相同值。

`enn_concentration_diagnostic.csv`9行，按总体/八层记录实际不同值数、范围、60 m数量/面积份额、>60 m尾部支持及面积ECDF四个切点。`pixel_q20_q40_q60_q80`按分号列出实际分位点。不给ENN等级；其描述性值不等于整体聚集度。

## 下一轮最小计数接口

选定方案后，从本轮归属按`target,PID`连接原`prediction_count_index.csv`和`counts_*.npz`。NPZ的`patch_band_prediction_counts[PID,band,predicted_class]`以显式PID索引；不得按特征CSV行序索引。站点内PID可以重复，跨站连接必须带target。真实类别由`crop`连接，预测类轴和七带顺序沿用既有字典。

先按指标等级、真实作物和位置求**整数像元总和**，用该集合的真实支持作分母，不能平均斑块错误率。本站为已有完整独立测试汇总计数；跨站180份按模型、源、目标、预测编号分别计算率，再对同组合完整五次求算术均值、样本标准差`ddof=1`及方向。缺失一次或不可算不能以较少有效次数替代五次均值。不同模型和来源同目标等级必须使用相同PID/像元支持。

无需新增数据即可计算：该等级面积支持、召回率、漏分率、两种错分去向及其跨站减本站增量、七带和`边界/内部/远内部`对照、净错误计数变化。边界率以`boundary_pixels`、内部率以`interior_pixels`作分母；远内部另以第七带支持作分母。没有相应像元时NA。本站与跨站错误数之差只称净变化，不能称逐像元实际新增/纠正错误。

现有图斑计数缺少PID×直接接触位掩膜联合轴；`type_band_bit_cm`按K2汇总，不能改标签当作新等级结果。只有确需该交叉时，读取原`reference_full_{target}.npz`的`label,ids,bands,bits`和索引指向的既有预测，累计PID×band×bitmask×预测类；保留纯另一作物、纯其他类、混合、最近带非直接接触四个互斥组，不重算距离或最近边界、不向内部外推接触类型。

真实作物斑块内部计数没有完整假阳性形态归属，不能命名为该等级F1或ΔF1。整站F1/ΔF1继续使用现行汇总；F1=2TP/(2TP+FP+FN)，分母为0才NA。错误率增量为跨站−本站，ΔF1为本站−跨站，两者不能混用。本轮接口尚未执行等级误差计算。

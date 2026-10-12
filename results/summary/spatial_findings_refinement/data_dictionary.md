# 提炼表的统计口径

数据性质：derived / exploratory。所有数值来自已保存的参考特征和预测计数，没有placeholder或mock。各站完整AREA×SHAPE分布沿用[气泡图原表及说明](../area_shape_joint_bubbles_v3/README.md)；本文件只定义本轮条件对照。

## 身份、单位与分组

- A/B/C/D对应`iw_2023/iw2_2023/ida_2023/il_2023`；模型`convgru/unet3d/utae`对应ConvGRU/3D U-Net/U-TAE。本轮新分层仅含C、D大豆；`whole_F1_context`另保留两站两作物完整F1背景。
- `kind,model,source,target,fold`唯一确定一次预测；本站`fold=0`是保存的五折测试汇总身份，不是额外训练的一折。跨站为1～5，每次覆盖完整目标站；没有跨站集成。
- `arm=0`或`low`为SHAPE<2，`arm=1`或`high`为SHAPE≥2。SHAPE无量纲；不是冻结形态类型。完整参考斑块为30 m标签8邻域连通对象，不等同于农业田块。
- AREA为ha，`area_ha=reference_pixels×0.09`；ENN为m。`pixels`为同组参考像元数。率、率差、面积份额、贡献份额均存0—1尺度，除原气泡表的`area_share_pct`为0—100。报告中的百分点为率差乘100。
- 原七带依次为`0<d≤1`、`1<d≤2`、`2<d≤3`、`3<d≤4`、`4<d≤5`、`5<d≤6`、`d>6`，d单位为像元。它不是ENN，也不等于直接异类接触分组。
- `a6d3`采用六档AREA（0、10、50、100、200、500、∞）与三段距离（首带、其后五带、远内部）。`a6d7`用相同AREA和原七带。`a12d7`的AREA边界为0、1、10、25、50、75、100、150、200、350、500、1000、∞，使用七带。均左闭右开；实际AREA均大于0。
- `area_bin/distance_bin`从0计；`stratum=area_bin×该方案距离带数+distance_bin`。分档支持保存全部格；零支持的错误率为NA，不替换为0。没有按单像元或外缘斑块筛除。
- `reference_cells`及`cell_counts_per_prediction`的`patch_count`是向该距离层贡献至少1像元的斑块数。同一斑块可出现于多个距离层，不能跨带相加当作独立斑块数。完整自然组中的`patch_count`每斑块计一次。

## 共同支持与权重

`scope=within_target`在每个目标的高/低两组间建权重；`scope=joint_CD`在C低/C高/D低/D高四组间使用完全相同的权重。后者用于本轮跨目标比较。

对每个组，将各层参考像元数除以该组完整像元数；每层取参与组中最小份额。`rule=primary`要求该层每组至少10个贡献斑块、1000像元；`all_supported`只要求各组非零支持。排除不满足门槛的层，将其余最小份额归一化为权重。权重只依赖参考，不根据任何预测错误选取。

`coverage=retained_pixels/total_pixels`，分母为该目标该形状组的完整面积；`excluded_pixels`明确保留被排除部分。覆盖率不等于权重质量或因果识别程度。`overlap_mass`是归一化前最小份额之和；不得当作覆盖率。`common_strata/total_strata`是纳入层数/候选层数。

`matched_geometric_area_ha`为各层按像元加权log(AREA)，再按共同层权重合成后取指数；`matched_mean_enn_m`为同样权重下的像元加权ENN算术均值。二者用于检查残余不平衡，不替代表1中位数。共同分档权重并不保证连续AREA、ENN、邻接或影像条件相同。

## 错误率与增量

`to_corn/to_other/to_soybean`为真实大豆像元分别判为三类的整数计数。`fn=to_corn+to_other`。对纳入层先算“定向计数÷该层该组参考像元”，再按共同权重求和，得到`low/high_corn`和`low/high_other`；二者之和为`low/high_omission`。

- `gap_指标=high_指标−low_指标`，是高低组绝对错误率差。
- `within_字段`为同模型、同目标、同方案权重下的本站汇总基准。
- `delta_字段=跨站字段−within_字段`。核心`delta_gap_omission`等于“高组额外漏分−低组额外漏分”，也等于“跨站高低差−本站高低差”。
- `delta_gap_corn+delta_gap_other=delta_gap_omission`。正、负都保留；差值为负不代表任一组错误率实际下降。
- 所有分组错误率的分母是真实大豆像元。它们没有完整FP，因此不能称为分组F1。

五次分别计算后汇总。`_mean/_std/_min/_max`分别为五次均值、样本标准差（ddof=1）、极小和极大；`_positive/_negative/_zero`为五次符号次数，`_n_valid`为有效值数，`_direction`记录方向一致性。不得把一次NA悄悄删掉后计算四次均值。候选一致性表的`delta_gap_min/max`是各模型—来源**均值**的最小/最大，不是所有单次极值，也不是置信区间。

## 自然计数贡献与标准化差的分解

`natural_shape_counts`保留高低组的完整像元和计数，不按共同支持筛选，也不使用共同权重。

- `area_share=该组完整参考像元/本站全部大豆参考像元`。
- `delta_fn`等计数增量为跨站减同模型本站，不是逐像元配对的“新增错误数”。
- `net_fn_contribution=该组delta_fn/全大豆参考像元`，表示该组对全作物漏分率净变化的贡献；乘100可写为百分点。`net_to_corn/other_contribution`同理。
- `ratio_of_mean_fn_net=该组delta_fn_mean/两组delta_fn_mean之和`，即对整站平均FN净变化的份额；零分母为NA，负值或超过1不截断。精简表的`complex_share_of_fn_net`即高组的此字段，`complex_fn_net_mean`为高组平均净计数，`complex_area_share`为高组自然面积份额。
- `stratum_gap_contributions`则是“共同权重×该层高低组错误率增量之差”，各层相加恢复标准化`delta_gap`。排除层的分解项为0，仅表示它未进入该对照，不表示该层没有错误。这种分解不能作为自然全站净错误贡献。

`paired_C_D`按`model,source,fold,scheme,rule`连接相同源模型的两目标预测，`C_minus_D`为两站同指标之差。五次共享目标参考，四站也不是大量独立地理重复，不作显著性检验。

`whole_F1_context`复用上一轮完整三类混淆矩阵结果：`delta_f1_mean=同模型目标本站F1−跨站平均F1`，与错误率增量符号定义不同。`delta_fn_loss_mean/delta_fp_loss_mean`沿用完整F1恒等分解，定义见[上一轮字典](../spatial_error_conditions/data_dictionary.md)，不解释为独立效应。

`core_common_source_comparisons`重复附列同一自然贡献以便跨方案阅读；`all_paths_candidate_context`保留旧六档×三段、逐站共同权重口径；两者不能跨行、跨方案相加。不同指标分组也不可相加为总贡献。

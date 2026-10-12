# 统计定义与表字段

结果为derived / exploratory，保存17位有效数字。A/B/C/D对应`iw_2023/iw2_2023/ida_2023/il_2023`。模型代码`utae/unet3d/convgru`对应U-TAE/3D U-Net/ConvGRU。玉米/其它地类/大豆混淆矩阵顺序为0/1/2。本轮不重排原矩阵。

## 身份、分组与支持

`kind,model,source,target,fold`标识单模型预测；模型对照以`comparison_model`替换`model`。本站fold=0是五折独立测试的完整计数汇总，跨站1～5是源站各折模型覆盖完整目标站的预测。实际运行记录表证明三模型同编号有相同源站训练/验证/测试折和测试图块集合；配对只对齐训练划分及目标参考，不代表权重、初始化或训练过程一致。

原距离代码在2倍网格标记完整参考标签有效类别四邻域共享边线段，作欧氏距离变换后在像元中心采样、除以2；相邻中心到直边距离为0.5像元。外框、图块框、NoData边不参与。七带为`0<d≤1`至`5<d≤6`和`d>6`，三段阅读为首带、其后五带、远内部。这里的距离不是ENN，也不等于直接异类接触组。

`scheme=all,distance,distance_three,area_shape`分别为全作物、七带、三段、原24格联合分档。AREA为ha，档界0、10、50、100、200、500、∞；SHAPE档界1、1.5、2、3、∞，左闭右开。参考对象为完整8邻域同类斑块，保留单像元及外缘斑块，不等同实测田块。不同scheme相互重叠，贡献不能相加。

`reference_pixels`为组内参考像元；`area_ha=reference_pixels×0.09`；`area_share=reference_pixels/whole_crop_pixels`，分母是该站该作物。`patch_count`跨距离不可相加，同一斑块可能贡献多带；合并三段未重算去重斑块数，记NA，而非把七带斑块数直接累加。

## 单模型错误、模型优势和贡献

`model_group_rates_per_prediction`保留三模型各组FN和绝对漏分率，便于直接查看三模型。`group_advantage_per_prediction`保留两个模型的对应字段，后缀`_convgru/_other_model`分别为ConvGRU和`comparison_model`指定模型。

- `omission_rate=fn/reference_pixels`。无参考像元时率为NA；计数及对全作物贡献为0。
- `advantage=omission_rate_convgru−omission_rate_other_model`。正值为另一模型漏分更少，负值为其漏分更多。
- `net_fewer_pixels=fn_convgru−fn_other_model`，是带符号净计数差，不是逐像元确认的纠正数。
- `net_to_other/net_to_other_crop`为两条错分去向各自的净计数差，二者相加恢复`net_fewer_pixels`。
- `within_*`为同目标同作物、同模型对照和同分组的本站汇总基准。
- `advantage_change=advantage−within_advantage`，正值表示相对优势扩大。
- `error_increment_模型=该模型跨站绝对漏分率−该模型本站绝对漏分率`。因此`advantage_change=error_increment_convgru−error_increment_other_model`，不能据优势扩大声称另一模型自身错误减少。
- `whole_rate_contribution=net_fewer_pixels/whole_crop_pixels`。各组相加恢复全作物优势；乘100为百分点。
- `net_reduction_share=net_fewer_pixels/whole_net_fewer_pixels`。是对全作物带符号净差的份额，允许负值和超过1；全作物总差为负时，这个比例描述净劣势的分配，不应称为正向改进贡献。

预先固定`abs(whole_net_fewer_pixels/whole_crop_pixels)<0.001`（0.1个百分点）时，`net_reduction_share=NA`并标记`near_zero_total_do_not_rank`。这是避免净分母接近零时比例失真的阅读规则，不是显著性阈值，也不删除其计数、率差或路径。完整值与空组NA均保留。

跨站每条路径先分别计算五次，再汇总均值、样本标准差（ddof=1）、极值和方向。`_positive/_negative/_zero`为五次正负零次数；`_n_valid`为有效次数，五次不能全部有效则均值及标准差为NA，不缩成四次统计。`net_reduction_share_mean`是逐次净比例均值；另给`ratio_of_mean_net_reduction=组平均净差/全作物平均净差`，报告贡献份额使用后者。它按平均总差执行同一近零门槛，`mean_contribution_status`说明状态。

## 固定同一支持的条件对照

只保留两项：`area_control_shape_distance`将AREA<50/≥50 ha记arm=0/1，外层控制四档SHAPE；`shape_control_area_distance`将SHAPE<2/≥2记arm=0/1，外层控制六档AREA。`stratum=control_bin×3+distance_bin`，距离编号依次0/1/2；控制档号从0开始，按上述AREA或SHAPE顺序。

两项均复用旧`conditional_support_weights.csv`对应对照的参考支持、纳入层和共同权重。`primary`每层每组至少10个贡献斑块/1000像元；`all_supported`为两组非零。`eligible`与预测错误无关。权重均由两组各层占完整组面积的份额取较小值，再在合格层归一化。

- `distance_equal`：直接使用原共同面积/形状×距离层权重。
- `distance_native`：纳入层完全相同，先将上述共同权重按外层档求和，固定为共同外层权重；在每一组、每一外层档内，再按该组纳入像元的原距离比例分配。它不是未筛选全作物率。
- 两种模式的每组覆盖、每层纳入标记、每个外层权重均相同，只有外层档内的距离权重不同；`same_support_weights`同时保存两套权重，排除层为0。
- `conditional_model_rates_per_prediction`保存共同权重后的单模型组率；`conditional_advantage_per_prediction`逐次算ConvGRU减另一模型，保留模型绝对率、自身增量和本站优势。`conditional_contrast`另算高组减低组的优势差及该差的跨站变化。
- `conditional_coverage`的分母为该目标该作物该arm完整参考像元；`retained/excluded_pixels`为保留/排除像元。不能把保留层中斑块数跨距离相加当作独立支持量。

两组各用同一参考支持，所有模型和来源也用同一权重。距离控制前后差的缩小不是因果中介比例；三段内连续距离、连续AREA、邻接、ENN和影像时序仍可能不同。

## 复用桥接和完整F1

`refined_CD_bridge`直接读取上一轮`a12d7, joint_CD, primary`的C/D大豆标准化逐次率，再计算模型优势和高低组优势差。这里两站共用权重，和本轮四站各自权重不同，不能混用数值或覆盖；`change_high_minus_low_advantage`精确等于ConvGRU的旧`delta_gap_omission`减相应模型同项。完整逐次表保留本站行和基准。

完整三类混淆矩阵仍按保存整数计算、核对全部576行类别指标和正式F1。`complete_class_context_per_prediction`保留TP、FN、FP及其它地类；`complete_F1_comparisons`保存两模型完整F1和正式`ΔF1=同模型目标本站F1−跨站F1`。`f1_advantage`反向定义为另一模型F1减ConvGRU F1，正值表示完整F1较高，不能与漏分优势当作同一指标。

主表16行及其三来源范围是阅读摘要，不增加独立地理样本。`within_top_joint_cells`按净计数前三名保留并列；主表CSV的`top3_joint_groups`另摘录排序前三格便于阅读，完整并列和全部24格始终保留。C/D及共享目标上的五次预测不作显著性推断。

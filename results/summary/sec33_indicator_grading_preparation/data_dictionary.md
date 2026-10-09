# 指标分级准备数据字典

## 对象、来源与分母

主输入为`results/processed/sec33_reference_patch_types/reference_patch_features.csv`，唯一键`target,PID`，辅助身份`patch_uid`。四站A/B/C/D=`iw_2023/iw2_2023/ida_2023/il_2023`。完整2560×2560标签30 m、8邻域连通定义沿用历史；1像元=0.09 ha。当前187372个三类参考斑块中149234个作物斑块，作物支持19426296像元。其他类38138个斑块保留在原底表和`all_class_reference_support.csv`，不混入两作物分布。

`domain=all`为四站两作物唯一斑块合计；`crop`为同作物跨四站合计；`site_crop`为单站单作物。每个视图内部身份不重复，但三种视图互相包含，禁止合计。合并分布从实际单斑块值计算，不平均旧表分位数。所有分析为derived / exploratory，未生成新等级。

AREA为ha、SHAPE无量纲、ENN为m，使用原FRAGSTATS输出；有限且大于0的三项主指标为有效值。当前全部作物记录有效，缺失/无效数量和像元数均为0。一般缺失不填0：数量频率分母`n_valid`，面积频率分母`pixels_valid`，另保留`n_total,pixels_total`及排除覆盖。CONTIG的0是合法值，其旧分布直接复用，不适用主指标的正值筛选。

## 分布与算法

`indicator_distribution_reading.csv`唯一键`domain,target,crop,metric,weighting`，66行。`weighting=patch_equal`为斑块等权，分位数沿用pandas线性顺序统计量算法：排序后位置`(n−1)q`在相邻值间线性插值。插值分位数不一定是观测值。已有总体和八层的`minimum,q25,median,q75,q95,maximum`直接引用旧表，`reused_source,reused_fields`明确来源；缺失的`q05,q10,q90,q99`新增。`crop`域此前无分布，直接从原斑块值补充所有分位数。

`weighting=reference_pixel_area`为像元面积权重：按指标值排序，每斑块权重为其`reference_pixels`。分位数为累计有效像元权重首次达到q的最小实际观测值，即加权ECDF左逆；不做线性插值。同值集中时多个分位数可以重合，不把同值拆开。它表示“随机取该参考域作物像元时，其所属完整斑块指标的分布”，不表示对大斑块重新切片。总体权重由四站实际作物像元量决定，不是八层等权的聚类权重。

`q05,q10,q25,median,q75,q90,q95,q99`为5/10/25/50/75/90/95/99百分位；`n_unique`为未舍入有效实际取值数；`minimum,maximum`为实际范围。`patch_area_cdf_gap`为同一域数量ECDF与面积ECDF的最大绝对差，描述权重差异，无检验或P值。`current_status`仅覆盖本轮分布派生核验，不代表原软件全部参数或距离生成已重新验证。

`processed/value_frequency_cumulative.csv`45910行，唯一键`domain,target,crop,metric,value`。读取保存CSV采用round_trip，按实际数值精度groupby，不按显示小数位合并。`n_patches,pixels`是同值数量和参考像元整数和；`patch_share,area_share`分别除以同域同指标有效数量/像元。`cumulative_n_patches,cumulative_pixels`按实际值升序累计，`patch_cdf,area_cdf`为对应累计比例。`patch_rank,area_rank`按数量/面积降序，同分时实际值升序，仅用于选择阅读样例。

`concentrated_values.csv`保留每域每指标数量或面积排名前5的并集，不是全部频率，也不是待删除值清单。`singleton_count/pixels`对应完整斑块仅1像元；`no_interior_count/pixels`对应完整斑块无`d>1`像元；`edge_count/pixels`对应斑块触及外框。它们为可交叉重叠的属性，不能互相相加。边界/内部像元字段为原七带支持，不是预测错误。

`diagnostic_value_intervals.csv`165行，唯一键`domain,target,crop,metric,interval_id`。仅按**合并面积ECDF**5/25/50/75/95分位及最大值的不同实际值切段，首段含最小值，后段左开右闭；重复分位点去重，所有同值保持在一段。ENN首段可退化为单一取值60 m。每项指标区间定义四站两作物共用，目的是检查参考支持，`purpose=pooled_area_ecdf_diagnostic_not_frozen_grades`。这些区间不是正式/冻结断点，也不预设后续采用相同区间数。各域段内数量/面积之和恢复有效总体；零支持保留计数0，支持占比0是实际覆盖而非零误差。

`stratum_distribution_overlap.csv`84行，键`metric,target_a,crop_a,target_b,crop_b`。包含八层所有28对。`range_overlap_*`为两层完整数值范围交集，`range_patch/area_coverage_a/b`分别为两层落入交集的有效数量/面积比例。`max_patch/area_cdf_gap`在两层观测值并集计算ECDF最大差，分母各层独立。`area_weighted_q05_q95_overlap_low/high`为两层面积加权中间90%区间交集；low>high表示无交集。范围重叠不能等同于形态、组成或邻域条件已控制。

## 复用表和支持量

`reference_support_reading.csv`11行，键`domain,target,crop`。原K4四类互斥，`n_patches,pixels,singleton_count,boundary_pixels,interior_pixels,far_interior_pixels,no_interior_patches,edge_patches,edge_pixels`从已有对应域四类整数计数求和，并与现有特征逐行支持核对。比例由这些整数重新除以总体分母，不平均类型比例。`area_ha=pixels×0.09`。新增`no_interior_pixels`来自已有特征字段，`no_interior_area_share`以同域作物总像元为分母。数量比例分母为全部该域作物斑块，面积比例分母为全部该域作物像元。

`reused_indicator_distributions.csv`45行、`reused_indicator_correlations.csv`90行，原字段数值不修改，仅加来源/权重说明；GYRATE/CONTIG可由此直接查旧分布，不新算指标或重新筛选。相关性沿用历史，没有当作本轮新结果。`reused_type_reference_support.csv`60行，原K2 16行加K4 44行，用`scheme`和明确的`K2-T1/T2,K4-C1..C4`区别，保持原domain；两方案及不同domain不能重复合计。原类型中位数只描述该类型，不用于反算总体中位数。

`all_class_reference_support.csv`12行，键`target,crop`；原三类像元、斑块及位置支持的直接汇总，恢复每站6553600像元。`count_reuse_schema.csv`4行记录本轮重开的四站ConvGRU本站样本，包括原NPZ实际键与形状。192份索引身份和文件存在性已核查，其余188份数组未重新打开，不借此宣称全预测数据再次完成逐像元核验。

## 下一轮计数衔接

`patch_band_prediction_counts[PID,band,predicted_class]`可由新等级归属按`target,PID`选择明确PID，再对计数求和；真实类别由特征表连接。它支持真实作物召回率、漏分率、错向另一作物/其他类、边界`0<d≤1`、内部`d>1`及远内部`d>6`，并保留七带。每个跨站预测分别算率，再取五次均值和样本标准差；不能按K2/K4汇总比例拆分，也不平均斑块错误率替代像元汇总率。

现有图斑级数组没有直接接触`bits`维度，`type_band_bit_cm`已经按K2压缩。新等级×直接接触需读取原`reference_full_{target}.npz`中的`label,ids,bands,bits`和计数索引指向的已有整幅预测，新增可复用的`PID×band×bitmask×predicted_class`整数联合计数；不重新生成距离、类型或预测。最近带内仅另一作物/仅其他类/混合/无四邻域直接接触四组沿用现行规则，不能向内部外推类型，无边段身份。

完整类别F1还包含真实其他类及另一作物进入该类的FP，不能在真实作物斑块内计算完整F1，也不能把“同AREA等级的真实来源类集合”未经定义当成预测目标作物的形态组。现有整站F1/ΔF1及六向定向错分继续复用收尾目录。未来错误增量是跨站减本站，ΔF1是本站减跨站，且计数差只称净变化。等级错误重算本轮尚未开展。

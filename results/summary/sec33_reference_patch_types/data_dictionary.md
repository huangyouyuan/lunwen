# 整图参考作物斑块探索：字段、分母与尺度

原FRAGSTATS `.patch`和`.adj`已另存为可跟踪CSV，见[原始结果表格及来源说明](../../raw/sec33_reference_patch_types/README.md)。此处分析字段与原表字段分开；原表保留重复记录、原序和原精度。

结果性质为derived / exploratory。CSV以17位有效数字保存，空值为NA。计数为整数；报告只在显示时舍入两位小数。本站与跨站逐次统计均以同一目标参考标签、相同完整斑块和像元为依据。不计算真实作物斑块内部的类别F1。

## 图斑与分型

- `target`与`site`：A=iw_2023、B=iw2_2023、C=ida_2023、D=il_2023。
- `PID`为既有FRAGSTATS ID图的整数；`patch_uid={target}__ref{PID}`是本站内唯一完整参考斑块身份。它不是历史128×128图块的patch_id。`id_component_correspondence.csv`保留与独立恢复8邻域组件的双射，两个程序的整数编号无需相等。
- `reference_patch_features.csv`保留四站全部三类斑块；`crop`为corn/other/soybean，参考标签原码1/2/3，内部预测码0/1/2。其他类不参与聚类，但保留在全站矩阵闭合和错分去向中。
- `reference_pixels`是整图中该ID的像元数，AREA为ha，1像元=0.09 ha；GYRATE、ENN单位m，SHAPE、CONTIG无量纲。SHAPE表示栅格边长相对同面积最紧凑形状的周长复杂程度，不是长宽比。GYRATE描述围绕质心的空间延展，不能等同于纯狭长度；该批单像元GYRATE为15 m，沿用原输出，不自行改0。CONTIG是局部邻接连续性，不等同于图斑数。ENN是研究区内最近同类斑块的欧氏距离，不能说明研究区外邻近关系。当前文件没有FRAC、PROX，因此不推定PROX半径。
- `touches_outer_edge`标记任意像元触及2560×2560外框的斑块；外框截断使面积、形状及邻近条件受范围影响，保留这些斑块并单列覆盖。它不把外框设为真实类别边界。
- `row_min/max,col_min/max`是整图内包围范围，仅供定位和展示；`oof_fold_count`说明同一完整斑块可跨越不同独立测试折，不能把斑块称为由一个模型统一预测的本站样本。
- `feature_status,missing_reason`保留可用状态。所有小斑块均保留；未以错误筛选特征。
- `cluster_candidates.csv`保存K=2/3/4的所有候选归属；`cluster_parameters.json`保存变换、共同标准化、样本权重、中心与种子；`frozen_configuration.json`记录预测读取前的冻结文件哈希。`frozen_patch_assignments.csv`的`spatial_type=1/2`为冻结类型，0只用于未聚类的其他类。
- T1/T2按簇中心面积排序，不是精度排序。主变换为log(AREA)、log(SHAPE)、log(ENN)。八个站点×作物层等权用于共同均值、标准差及K-Means，普通斑块等权作为稳定性对照。类型同时包含形态与邻近条件，不能声称同簇内组成或其他形态已受控。

## 参考空间与计数底表

- `reference_full_{target}.npz`保存整图`label,ids,bands,bits,oof_fold`。`bands=0..6`对应原七带 `(0,1]`、`(1,2]`、`(2,3]`、`(3,4]`、`(4,5]`、`(5,6]`、`>6`像元。
- 分带来自已有完整参考标签共享边距离。直线相邻像元中心距共享边0.5像元；研究区外框与NoData边不自动参与。没有重新执行EDT。旧分带由已保存参考数组复原整幅，不用图块裁剪框产生距离。
- `bits=0..7`是互斥完备原边界位组合。位1=玉米—其他，位2=玉米—大豆，位4=其他—大豆。3/5/6/7为多类型交汇，单列；0为无直接类型标记，最近带中也可能存在。类型只描述直接交界的两侧邻域，不能外推到内部，也没有边段ID。
- `prediction_count_index.csv`连接`kind,model,source,target,fold`、原整幅预测路径、计数文件与SHA-256。本站kind=within、source=target、fold=0表示完整OOF；跨站kind=cross、fold=1..5表示五个源模型各自预测完整目标站。
- 每份`counts_*.npz`中的`patch_band_prediction_counts[PID,band,predicted_class]`保存每个完整参考斑块的七带三向整数计数，参考真值类别由斑块特征表连接。PID=0行空白；其余行包含所有参考类，包括other。`type_band_bit_cm[type,true_class,band,bitmask,predicted_class]`保留类型、七带及互斥边界类型的完整整数计数。前者是图斑级底表，不能以行位置替代PID身份。
- 完整整幅GeoTIFF用于景观关联。旧图块预测和测试折只用于逐像元核验该GeoTIFF的覆盖与OOF来源，不作为本轮景观分析单位。

## 类型结果与率

`type_error_counts.csv`、`boundary_type_error_counts.csv`含本站和全部跨站逐次整数计数。`region=all,boundary,interior,far_interior`分别是完整斑块、0<d≤1、d>1、d>6；另保留七带原字段，以及all_edge/all_nonedge的截断/非截断斑块完整区域。它们是不同视图，不能把所有region相加。

- `pixels=N`为指定真实作物、类型、位置的参考支持量。`correct`是预测正确像元，`errors=N-correct`。
- `other_crop_errors`表示错成另一种作物，`other_errors`表示错成其他类；二者相加恢复errors。
- `recall=correct/N`、`leakage=errors/N`、`other_crop_rate=other_crop_errors/N`、`other_rate=other_errors/N`。零支持量率为NA，计数为0；没有内部像元的图斑不会伪造内部错误率。
- `n_patches_with_support`是该位置有参考像元的斑块数，`type_pixels,class_pixels`分别是该站该作物同类型/全类型的总像元数。
- `_per_prediction.csv`保留同键本站率和跨站逐次率；`delta_*`一律是跨站减本站，是错误或率的增量，不是ΔF1。正确率/Recall的增量符号与漏分相反。
- `net_added_errors`是两种结果错误数量之差，不是逐像元原本正确后来变错的数量。`net_contribution_to_class_leakage=net_added_errors/class_pixels`，`net_contribution_to_type_leakage=net_added_errors/type_pixels`。边界与内部贡献之和恢复对应整体漏分率增量；不能用其解释完整F1变化。
- `pixel_share_of_type/class`与贡献的分母对应。带内错误率增量高不等于该带净增数量最大。所有负值保留，不强行解释可能有抵消的净增百分比份额。
- `_summary.csv`的mean/std/min/max来自五次独立计算值；std为样本标准差ddof=1，不是置信区间。任一逐次值NA则均值及标准差NA，不减少五次分母。`*_direction`为all_positive/all_negative/all_zero/mixed/not_calculable；判定用未舍入值，NA不叫相等。
- `location_contrasts_*`是同一预测编号的“内部增量−边界增量”，不是跨站绝对错误率差；`type_contrasts_*`为T2−T1漏分率增量。模型/来源对照固定目标、作物、类型和位置。

## 图斑数量和整块漏识别

`type_reference_support.csv`分别报告数量占比和像元面积占比，不将大量单像元斑块的数量优势当作面积优势。`boundary_share`为边界像元占该类型作物像元的比例；`no_interior_fraction`为没有d>1像元的图斑比例。

`whole_patch_miss_*`中`no_correct_patches`指整个参考斑块的正确识别像元数严格为0，`no_correct_patch_fraction`以该类型斑块数为分母；`no_correct_pixels/no_correct_area_fraction`另按这些斑块包含的参考像元数统计。它不同于“斑块中至少有一个错误”，也不能以图斑个数权重替代主像元汇总率。比例逐次计算后五次汇总。

全站`whole_crop_f1.csv`使用完整三类CM计算作物F1，仅用于与当前正式汇总闭合，不是类型内指标。背景class/landscape/adjacency表只描述各整幅站点，没有复制为每个斑块属性。

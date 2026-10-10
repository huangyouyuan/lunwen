# 完整参考斑块与预测计数：活动数据字典

原FRAGSTATS `.patch`和`.adj`已另存为可跟踪CSV，见[原始结果表格及来源说明](../../raw/sec33_reference_patch_types/README.md)。此处分析字段与原表字段分开；原表保留重复记录、原序和原精度。

结果性质为derived / exploratory。CSV以17位有效数字保存，空值为NA。计数为整数；报告只在显示时舍入两位小数。本站与跨站逐次统计均以同一目标参考标签、相同完整斑块和像元为依据。不计算真实作物斑块内部的类别F1。

## 参考斑块身份与指标

- `target`与`site`：A=iw_2023、B=iw2_2023、C=ida_2023、D=il_2023。
- `PID`为既有FRAGSTATS ID图的整数；`patch_uid={target}__ref{PID}`是本站内唯一完整参考斑块身份。它不是历史128×128图块的patch_id。`id_component_correspondence.csv`保留与独立恢复8邻域组件的双射，两个程序的整数编号无需相等。
- `reference_patch_features.csv`保留四站全部三类斑块；`crop`为corn/other/soybean，参考标签原码1/2/3，内部预测码0/1/2。其他类保留在全站矩阵闭合和错分去向中。
- `reference_pixels`是整图中该ID的像元数，AREA为ha，1像元=0.09 ha；GYRATE、ENN单位m，SHAPE、CONTIG无量纲。SHAPE表示栅格边长相对同面积最紧凑形状的周长复杂程度，不是长宽比。GYRATE描述围绕质心的空间延展，不能等同于纯狭长度；该批单像元GYRATE为15 m，沿用原输出，不自行改0。CONTIG是局部邻接连续性，不等同于图斑数。ENN是研究区内最近同类斑块的欧氏距离，不能说明研究区外邻近关系。当前文件没有FRAC、PROX，因此不推定PROX半径。
- `touches_outer_edge`标记任意像元触及2560×2560外框的斑块；外框截断使面积、形状及邻近条件受范围影响，保留这些斑块并单列覆盖。它不把外框设为真实类别边界。
- `row_min/max,col_min/max`是整图内包围范围，仅供定位和展示；`oof_fold_count`说明同一完整斑块可跨越不同独立测试折，不能把斑块称为由一个模型统一预测的本站样本。
- `feature_status,missing_reason`保留可用状态。所有小斑块均保留；未以错误筛选特征。

## 参考空间与计数底表

- `reference_full_{target}.npz`保存整图`label,ids,bands,bits,oof_fold`。`bands=0..6`对应原七带 `(0,1]`、`(1,2]`、`(2,3]`、`(3,4]`、`(4,5]`、`(5,6]`、`>6`像元。
- 分带来自已有完整参考标签共享边距离。直线相邻像元中心距共享边0.5像元；研究区外框与NoData边不自动参与。没有重新执行EDT。旧分带由已保存参考数组复原整幅，不用图块裁剪框产生距离。
- `bits=0..7`是互斥完备原边界位组合。位1=玉米—其他，位2=玉米—大豆，位4=其他—大豆。3/5/6/7为多类型交汇，单列；0为无直接类型标记，最近带中也可能存在。类型只描述直接交界的两侧邻域，不能外推到内部，也没有边段ID。
- `prediction_count_index.csv`连接`kind,model,source,target,fold`、原整幅预测路径、计数文件与SHA-256。本站kind=within、source=target、fold=0表示完整OOF；跨站kind=cross、fold=1..5表示五个源模型各自预测完整目标站。
- 每份`counts_*.npz`中的`patch_band_prediction_counts[PID,band,predicted_class]`保存每个完整参考斑块的七带三向整数计数，参考真值类别由斑块特征表连接。PID=0行空白；其余行包含所有参考类，包括other。`type_band_bit_cm[type,true_class,band,bitmask,predicted_class]`保留类型、七带及互斥边界类型的完整整数计数。前者是图斑级底表，不能以行位置替代PID身份。
- 完整整幅GeoTIFF用于景观关联。旧图块预测和测试折只用于逐像元核验该GeoTIFF的覆盖与OOF来源，不作为本轮景观分析单位。

## 当前可复用方式

`patch_band_prediction_counts`以明确的`target,PID`连接参考特征，可按未来参考条件重新汇总作物召回率、漏分率和两个定向率。零支持率记NA，完整七带整数加和可核对全站三类矩阵。各模型和来源须使用同目标相同斑块集合。本站完整OOF是12个独立组合，跨站180份，合计192份计数；五次指标各自计算，不合并矩阵替代指标均值。

`type_band_bit_cm`是历史K2类型的已汇总张量，保留在现有文件中追溯，不能换标签充当新等级或其他分组结果。按任意新斑块条件交叉直接接触类型，需要参考`ids,bits,bands,label`与已保存整幅预测补计数；仅凭斑块—距离—预测张量不能恢复丢失的边界位关联。本次不执行补统计。

误分入的真值像元属于另一参考类别，不能硬塞入被预测作物的形态组。完整类别F1需完整三类CM；作物斑块内指标不能命名为等级F1。净计数差不等于逐像元实际新增错误。

背景`background_class.csv,background_landscape.csv,background_adjacency.csv`读取`scope=full`描述站点，不能复制为各斑块属性。数量权重与参考像元面积权重分开，见 [参考分布入口](../sec33_indicator_grading_preparation/README.md)。

## 来源与验证状态

本次只整理字典及文件入口，未重算标签、距离、指标或预测。身份、计数和公式的原核查分别见本目录的`prepare_checks.csv,count_checks.csv,feature_audit_checks.csv,metric_formula_checks.csv`及原清单。历史验证范围不因文件移动升级。

2026-10-11复查后，K2/K3/K4候选、K2冻结配置、类型结果和原报告已恢复本目录及对应processed原路径；K4敏感性完整结果也已恢复。它们有复用价值，未被判定无效；历史报告的“K2主分析”建议不等于当前论文决策。共同五档仍是未批准候选，详见[用途索引](../reuse-status.md)。原字典快照及各阶段哈希保持，不自动执行历史生产源码。

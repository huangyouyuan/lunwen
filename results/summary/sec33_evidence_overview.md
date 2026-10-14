# 3.3 证据总览

更新：2026-10-11；2026-10-14补入新增证据入口。供选择证据，不是正文。本次整理只引用已保存结果，没有重算预测误差；原轮次总览与历史判断保存在 [快照](../../archive/2026-10-10-mainline/snapshots/results/summary/sec33_evidence_overview.md)。当前优先完成1.3四站参考背景与3.1本站错分基准，再围绕3.2组织3.3。完整K2/K4探索、参考等级候选和空间底表已恢复原位，见[复用入口](reuse-status.md)，不以是否成为主方案判断是否保留。

## 围绕3.2已能说明什么

| 3.2现象 | 已有对应证据 | 解释边界 |
|---|---|---|
| 两作物全部跨站均值低于本站F1基准 | 全域六向错分及TP、FN、FP可分别核对召回率和精确率变化 | 空间漏分统计不能解释全部F1变化 |
| 玉米通常绝对F1更高 | 本站12/12独立组合、跨站28/36均值玉米较高，跨站有8个例外 | 与“玉米跨站退化更小”不是同一判断 |
| ConvGRU平均ΔF1较小、绝对F1较低 | 绝对值与目标本站基准是不同比较；模型分层揭示不同错误构成 | 不称ConvGRU普遍泛化更强，不从基准反推机制 |
| 固定D目标站，B源ConvGRU大豆差距突出 | 大豆→玉米增加，同时进入大豆FN和玉米FP；延续到远内部，模型和来源改变幅度 | 定位去向、位置及条件，尚未说明B源为何如此 |
| B↔D较大F1差距的方向随模型改变 | ConvGRU大豆B→D伴随召回率较大下降，3D U-Net大豆D→B伴随精确率较大下降 | 必须保留误分入；两目标参考集合不同 |
| A目标跨站F1高、C玉米F1低 | 四站参考组成和完整斑块分布可作背景 | 尚未分离环境分布与条件错误，不写成景观成因 |

正式现象来源：[F1及ΔF1](f1_raw_scale/crop_f1_difference_36paths.csv)。其余来源：[收尾报告](sec33_directional_confusion_closeout/exploration-report.md)、[模型—作物汇总](sec33_directional_confusion_closeout/model_crop_metrics_summary.csv)、[路径级指标](sec33_directional_confusion_closeout/model_crop_path_diagnostics.csv)、[六向混淆](sec33_directional_confusion_closeout/directional_summary.csv)。

## 最完整的条件证据

B→D ConvGRU中，大豆→玉米从本站122,096像元至跨站五次均值402,652.2像元，净变化+280,556.2，五次均正。同一混淆单元同时进入大豆FN和玉米FP，对应大豆Recall −13.84、Precision +0.30，以及玉米Precision −8.33、Recall −1.77个百分点。大豆Precision为4正1负，不能写成五次均提高；净计数变化也不是逐像元新增错误。

B→D大豆→玉米的远内部d>6增量为ConvGRU +12.77、3D U-Net +1.43、U-TAE +5.15个百分点，三模型五次均正。固定D与ConvGRU，A/B/C源分别为+2.04/+12.77/+0.32个百分点；A逐次方向混合，B/C均正。因此可以支持“这一错误延续到内部且随模型、来源改变”，不能推广为某模型的一般机制。

最近带中同时接触玉米和其他类的30,405个大豆像元，B→D三模型的大豆→玉米增量五次均负，但大豆→其他增量为正，总漏分仍增加。这是去向改变，不是该边界组整体改善，也不是逐像元纠错。

来源：[两作物案例](sec33_directional_confusion_closeout/case_B_D_ConvGRU_crop_metrics.csv)、[距离对照](sec33_directional_confusion_closeout/case_D_distance_all_sources.csv)、[互斥边界](sec33_directional_confusion_closeout/exclusive_boundary_summary.csv)。最近带与直接接触不同，非直接接触最近带单列；没有边段身份，不称同一段边界两侧配对。

## 模型、形态与组成的限制

按12条路径等权，ConvGRU大豆Recall平均变化−5.04个百分点、Precision −0.59；3D U-Net和U-TAE两作物平均Precision下降更多。这个模型分层判断不能套到每条路径，也不能转换为未经定义的F1贡献比例。

既有C3/C4对照支持B→D内部错分在两类中都存在，不支持跨站增量的统一类型排序。两类面积、形状和邻近条件共同变化，同簇也不等于组成受控。[完整结果](sec33_k4_sensitivity/type_error_summary.csv)和[逐次对照](../../results/processed/sec33_k4_sensitivity/C4_minus_C3_per_prediction.csv)已恢复，作为可复用敏感性探索，不能替代新的单指标等级计数。

源站整站组成对照已覆盖六个方向，存在反向和无明确对应的情况。仅三个来源的排序不能证明组成决定误差，也不能据反例排除其作用；固定目标格局本身也不能独自解释来源变化。背景数值与局部邻接不是同一尺度。

来源：[六向组成对照](sec33_directional_confusion_closeout/source_composition_direction_contrast.csv)、[来源排序诊断](sec33_directional_confusion_closeout/composition_source_order_diagnostic.csv)、[保留的C3/C4案例](sec33_directional_confusion_closeout/case_D_C3_C4_interior_all_sources.csv)。参考特征见 [分布入口](sec33_indicator_grading_preparation/README.md)。

## 新增证据入口（2026-10-12/13）

- [四站空间条件与分类错误](spatial_error_conditions/README.md)：全路径分档、共同权重与空间子集实际贡献；为3.1/3.3提供条件基准与反例，不识别独立作用。
- [空间条件发现提炼](spatial_findings_refinement/README.md)：共同A/B来源下，C大豆高SHAPE组跨站额外漏分对照为正、D为负，六个模型—来源组合均五次同向；不称独立形状效应。
- [模型优势在空间条件中的分布](model_advantage_spatial_conditions/README.md)：以ConvGRU为参照的模型漏分优势分解；固定D换来源时优势幅度与最近带以外份额改变，C玉米本站优势跨站均值为负；完整F1单列。

## 当前收敛建议

优先保留两至三个判断：按模型区分漏分与误分入；以B→D连接具体方向、两作物指标和内部位置；用同目标换来源及B↔D反例限定解释。1.3先给出参考空间背景，3.1先给出本站错误参照，3.3不重复这两节，也不强求统一景观因果规律。

尚缺的是基础材料的精简阅读表及章节证据组织，见 [基础计划](../../plan/tasks/2026-10-10-sec13-sec31-foundations.md)。共同指标等级、联合条件对照和回归均不是自动下一步；若确需补充，须指出哪项3.2差异仍无法由已有表回答。

本次文档整理不升级科学生成验证。整数计数和统计沿原 [核查记录](sec33_directional_confusion_closeout/verification.md)；距离数组生成、FRAGSTATS原工程参数、B站元数据限制保持历史状态。未落盘预检不作为证据，历史轮次与旧口径见 [归档](../../archive/2026-10-10-mainline/README.md)。

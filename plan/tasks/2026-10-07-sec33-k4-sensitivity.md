# 3.3 既有K=4空间类型补充敏感性分析

开始日期：2026-10-07（Asia/Shanghai）；起始HEAD：`d29a228`。已有文献库修改和`2026-10-06-sec33-boundary-share-standardization.md`保持原样，不执行该计划。

## 动机与范围

这是K=2主分析完成后的补充敏感性分析。K2-T2承载绝大多数作物面积，作者指定检查已经保存的K=4候选中C3/C4能否补充主要作物面积内部的空间差异。不倒写为原先预设，不重选K、不调整特征、权重、变换或归属，不预设K=4更优。

新产物位于`results/processed/sec33_k4_sensitivity/`、`results/summary/sec33_k4_sensitivity/`和`figures/exploratory/sec33_k4_sensitivity/`。生产及绘图脚本位于`scripts/`，必要测试位于`scripts/test/`。不改正文、K=2文件或现有冻结配置；不训练、推理、重算距离/FRAGSTATS/K-Means，不编译、提交或推送，不开子代理。

## 执行顺序

1. 核对上轮交付哈希、K=4候选与参数、特征表、K=2冻结归属及192次身份清单。按目标站/PID连接，核对唯一性、作物和UID。保存选定归属、原参数及本轮设置，统一命名K2-T1/T2与K4-C1/C2/C3/C4。
2. **先完成参考诊断和图1，再读取预测计数。** 输出32个站点×作物×K4类型的数量/面积支持及占比、五项指标分位数/范围、单像元比例、边界占比、无内部比例和截断覆盖，另给全体汇总。K2×K4交叉表同时保留数量和像元。代表斑块只按既有标准化参考特征距对应K4中心最近选择（非截断），保留逐站候选，实际查看完整形态及周围标签。
3. 读取192份既有`patch_band_prediction_counts`，按明确PID重汇总全部四类和原七带，另保留其他类用于全站闭合。不用K2的`type_band_bit_cm`冒充K4计数；它只用于恢复原总体作闭合对照，不新增边界类型分析。
4. 按原口径生成本站、跨站逐次及五次均值/样本标准差，包含支持量、两种定向错误、漏分、带符号净增数及对全站作物漏分差的贡献。主位置为边界(0,1]、内部>1、远内部>6，七带单独保留。缺支持记NA，五次不完整不缩减分母，不计算类型内F1。
5. 在同模型/源/目标/作物/位置/预测编号下连接C3/C4，报告C4−C3的本站率、跨站率和增量差、去向差及逐次方向。它是不同图斑集合的条件对照，不是图斑一一配对。另汇总作物差、模型/源站差的适用范围，最后检查D站大豆及B→D。完整分源保留，不作显著性推断。
6. 图2聚焦C3/C4，覆盖全部72个模型×路径×作物条件，区分绝对漏分差与增量差、边界与内部、两种去向。以固定行列键导出绘图底表并核验，实际查看图件。
7. 保存报告、字典、例外、核查记录及输入/脚本/产物哈希。仅增加归属连接和重汇总风险测试，复用已有NA及五次统计函数。报告以新增科学信息为主，区分局部关系与普遍关系、历史验证与本次验证。

## 必须闭合

- K4归属唯一、无缺失；所有作物斑块恰属一类。不得假设与K2严格嵌套。
- 12个本站OOF及180次跨站身份完整，源目标不同且每路径预测编号1—5完整；支持量在所有模型/来源/预测间一致。
- 每次四类（含其他类单独记录）逐元素恢复原作物/全站及七带计数；与从K2恢复的总体相等；不平均类型率验证闭合。
- 两个定向错误相加恢复漏分；边界+内部净增计数与贡献恢复总体；C4−C3均值等于对应五次差的均值。
- 原K2冻结及交付文件最终哈希不变。本轮不重验历史距离生成或缺失软件工程配置。

## 执行结果

本轮已执行完毕，新增结果性质为derived / exploratory。没有重新拟合、改变类型归属或替换K2主方案。

1. 按`target,PID`连接149234个作物参考斑块，核对候选K2与冻结K2、UID及作物身份。保存既有K4配置副本与选定归属；K2×K4交叉表证实非严格嵌套。
2. 先完成四类完整特征支持与分位数诊断，保存参考代表斑块选择，并实际查看图1，再读取预测计数。C3/C4合计承载98.39%的作物面积，八个站点作物域中C4的AREA、SHAPE中位数均更高，但指标范围有重叠，ENN等条件未控制。
3. 完整复用192份计数，按PID重新汇总四类及单列其他类、原七带和三个合并位置。K4总计数逐元素恢复K2七带计数及192份全站矩阵；同目标所有模型、来源、五次预测支持量一致。
4. 输出四类逐次/汇总率、带符号净增计数及贡献，完整C4−C3对照、作物差、模型来源对照、NA/负值/混合方向清单。全斑块72组合中C4/C3平均漏分增量各有36组更高，五次方向混合22组；没有统一类型排序。先完成全范围统计，再核对D站大豆。
5. D站B源ConvGRU的内部大豆→玉米增量在C3/C4五次均正，C3率更高，但C4净增数量更高；3D U-Net、U-TAE及A/C来源保留全部对照和例外。具体科学判断见报告，不按该实例调整类型。
6. 图2保留全部72组合，区分绝对漏分、增量、边界/内部和两种去向；432格逐项与底表核对。两张PNG均已实际查看，SVG同步保存。
7. 新增audit阶段独立核对192份身份、全站矩阵、逐次分母、C3/C4显式编号对照、五次均值/样本标准差/范围及图表底表。新增4项K4内存测试、复用8项K2测试均通过；脚本语法用内存编译检查，不生成或删除测试文件。
8. 完成数据字典、科学报告和核查记录。最终核对上一轮293个交付文件哈希不变；本轮哈希记录通过delivery_manifest逐项复核。为避免Windows Git换行改变记录字节，新增局部`.gitattributes`，仅匹配K4文件，原根目录属性及上轮交付均保持不变。

实际执行入口：

```powershell
python -B scripts/explore_sec33_k4_sensitivity.py reference
python -B scripts/plot_sec33_k4_sensitivity.py features
# 实际查看并记录参考图；此后才读取预测计数
python -B scripts/explore_sec33_k4_sensitivity.py aggregate
python -B scripts/explore_sec33_k4_sensitivity.py analyze
python -B scripts/plot_sec33_k4_sensitivity.py errors
python -B scripts/explore_sec33_k4_sensitivity.py audit
python -B scripts/test/test_sec33_k4_sensitivity.py -v
python -B scripts/test/test_sec33_reference_patch_types.py -v
python -B scripts/explore_sec33_k4_sensitivity.py seal
```

`reference/aggregate`仅供首次执行，已存在归属或计数时主动拒绝，防止覆盖。当前可重复运行`audit`核查及`seal`更新交付清单；本轮生产步骤没有调用旧目录写回流程。阶段manifest记录当时脚本版本，最终脚本以delivery_manifest为准。

交付入口：[探索报告](../../results/summary/sec33_k4_sensitivity/exploration-report.md)、[数据字典](../../results/summary/sec33_k4_sensitivity/data_dictionary.md)、[核查记录](../../verification/sec33-k4-sensitivity-2026-10-07.md)。本次统计与身份闭合为Verified；历史距离生成、原FRAGSTATS工程配置追溯仍为Partially verified。未修改正文、未编译、未提交或推送，已有文献库修改与另一任务记录保留。

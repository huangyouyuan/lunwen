# 本轮实际核查范围

本轮起点HEAD为`8750231`，已有`bibliography/references.bib`修改保留。结果性质derived / exploratory；不写正文、不绘图、不确定正式断点，历史目录未重建或覆盖。

| 内容 | 状态 | 本次实际范围与限制 |
|---|---|---|
| 参考表身份和支持 | Verified | 检查`target,PID`及patch_uid唯一，四站三类187372斑块，149234作物斑块；每站像元和恢复6553600，AREA=像元数×0.09 |
| 保存的近/内部支持 | Verified | 特征字段近+内部恢复逐斑块总像元，无内部标记与内部0一致；不重算距离 |
| 旧主指标分位数 | Verified | 27条总体/八层×三指标与实际斑块值重算对照，绝对容差1e-12；阅读表对应旧字段直接引用 |
| 复用K4参考支持 | Verified | 11个参考域四类整数支持求和，与底表数量面积、单像元、无内部、外框及位置支持一致；不平均比例 |
| 取值频率及双累计分布 | Verified | 按原精度未舍入取值聚合，33个域×指标计数与有效分母闭合，累计数量/面积末值均为1 |
| 面积加权和扩展分位数 | Verified | 权重为参考像元数；加权ECDF左逆，等权为既有线性顺序统计；缺失分母及同值处理有专项测试 |
| 共同区间参考诊断 | Verified | 33个域×指标区间计数恢复有效总量，同值不拆分；仅覆盖诊断，未冻结等级 |
| 序列化交付表复核 | Verified | 552条检查通过；加权分位数满足累计权重左逆不等式，区间逐值互斥且完整，旧分布及相关字段不变，K2/K4整数支持恢复共同参考域 |
| 192份计数索引 | Verified | 12本站+180跨站身份唯一、预期组合完整、索引计数文件全部存在；此状态仅指索引和存在性 |
| 四份计数样本 | Verified | 四站ConvGRU本站NPZ哈希与索引一致；PID轴、非负整数、7×3形状及逐斑块近/内部/远内部支持吻合 |
| 其余188份计数数组 | Partially verified | 本轮未重开，沿用此前完整计数核查；未把历史Verified当成本次全量复验 |
| 原标签—ID空间双射及软件指标来源 | Partially verified | 沿用历史验证及来源清单，本轮未重新逐像元恢复连通分区或逐字段审计.patch |
| 原始距离生成 | Partially verified | 历史数组沿用，未重算共享边距离或EDT；本轮支持闭合不升级生成状态 |
| FRAGSTATS完整工程设置 | Partially verified | 仍缺原工程配置；分辨率、连通及已核查公式沿历史，本轮不运行软件 |
| 新等级错误及等级×直接接触类型 | Not verified | 尚未确定等级或开展统计，交付只说明可复用计数及缺少的PID联合维度 |

执行命令：`python -B -m unittest discover -s scripts/test -p test_sec33_indicator_grading.py -v`，6项专项测试通过，测试夹具仅在内存。覆盖原精度同值/相邻值、缺失有效分母、面积权重与数量权重区别、累计量边界和排序、无效权重及ECDF并集。生产命令`python -B scripts/prepare_sec33_indicator_grading.py`完成191条检查，详见[verification_checks.csv](verification_checks.csv)。随后执行`python -B scripts/prepare_sec33_indicator_grading.py --audit`，从保存的CSV独立复核552条检查，详见[delivery_checks.csv](delivery_checks.csv)；新增核查阶段后6项测试再次通过。没有重复运行历史预测误差、全项目测试或任何删除型清理流程。

运行输入及当时脚本哈希见[run_manifest.json](run_manifest.json)；生产后仅增加了交付表复核阶段，原运行哈希不改写。`python -B scripts/prepare_sec33_indicator_grading.py --finalize`重检11项实际输入并封存最终脚本、测试、任务记录和结果文件哈希，见[delivery_manifest.json](delivery_manifest.json)。两个清单中的脚本哈希分别对应生产时版本与最终交付版本，不应混同。交付清单不对自身计算哈希；本轮没有提交或推送。

# 论文交接

更新：2026-10-11。本版以`a70e11b`为整理前基线，保存主线整理与两次成果恢复；详细改动和新起点见[版本说明](plan/version-notes-2026-10-11.md)。接手先检查`git status --short`和`git log -3 --oneline`，以实际状态为准。规则见[AGENTS.md](AGENTS.md)，总体计划见[plan/outline.md](plan/outline.md)。

## 当前主线与优先级

四站空间背景 → 本站错误基准 → 跨站F1差距 → 错分变化与空间条件的对应关系。3.3解释3.2的具体模型、来源和方向差异；现有数据支持描述性对应，尚未证明因果机制。

| 章节 | 职责 | 当前状态 |
|---|---|---|
| 1.3研究区空间特征 | 四站参考组成、完整参考斑块及整站景观背景 | 已写入两小节、组成图和 AREA、SHAPE 双权重分布表；2026-10-11 授权编译为 7 页，1.3 图表排版已核查 |
| 3.1本站分类性能 | F1及必要的精确率、召回率和六向错分基准 | 主体和正式图已有，补充底表已核验，正文待最小补充 |
| 3.2跨站分类性能与差距 | 绝对F1、原尺度ΔF1、模型与来源差异 | 已有正文和表图，本次不变 |
| 3.3空间解释 | 差距对应什么错误、发生在哪里、怎样随模型来源变化 | 已有探索和最小衔接表，正文未写；先围绕3.2选择具体差异 |

基础材料的只读整理与核查见[1.3与3.1基础证据](results/summary/sec13_sec31_foundations/README.md)及其[段落—证据提纲](results/summary/sec13_sec31_foundations/paragraph_evidence_outline.md)。2026-10-11 后续按作者最新要求完成 1.3 正文、组成图及 AREA、SHAPE 双权重分布表，采用 2023 年完整参考斑块数据，见[本轮核查 JSON](verification/sec13-figure-table-v2-2026-10-11.json)。3.1 保持现有主体，3.3 正文仍为空。

## 活动证据入口

| 用途 | 入口 |
|---|---|
| 正式F1与ΔF1 | `results/summary/f1_raw_scale/`；原矩阵在 `results/raw/` |
| 1.3与3.1基础阅读表及本次核查 | [基础证据目录](results/summary/sec13_sec31_foundations/README.md)；输入、脚本与输出哈希见其中`manifest.json` |
| 完整参考斑块与192份计数 | `results/processed/sec33_reference_patch_types/`；字典在对应summary目录 |
| 四站景观背景 | `results/summary/sec33_reference_patch_types/background_{class,landscape,adjacency}.csv`，读取 `scope=full` |
| 组成、分布与支持 | [参考分布入口](results/summary/sec33_indicator_grading_preparation/README.md) |
| 六向错分、模型分层与空间定位 | [定向混淆入口](results/summary/sec33_directional_confusion_closeout/README.md) |
| 全路径七带漏分与净贡献、逐次Δe配对 | [可复用结果索引](results/summary/README.md)中的距离表；已恢复原数值与清单，未重算 |
| 完整F1错分分量与距离共同权重 | [可复用结果索引](results/summary/README.md)中的整站表；不把分量称为因果贡献 |
| 完整斑块类型、候选及其图件 | [分层复用入口](results/summary/reuse-status.md)；K2/K4完整恢复为补充探索，五档仍待审阅，不自动成为主方案 |
| 3.3判断与缺项 | [3.3证据总览](results/summary/sec33_evidence_overview.md) |

原 `sec33_directional_confusion` 保留修正脚本输入及有效的距离/组成结果。`sec33_crop_spatial_context`恢复了192份联合整数计数、参考数组和整站类型×距离统计；其中400个128×128是存储分区，不能拿来重新作为景观单元。其逐分区和已与192份整图类型张量逐元素一致，详见[二次核查](verification/second-pass-reuse-2026-10-11.md)。旧图块AREA_MN和匹配结果继续归档，旧生产流程不自动运行。

## 计算与解释边界

- A/B/C/D依次为iw_2023、iw2_2023、ida_2023、il_2023；12个独立本站模型—目标组合，12条迁移路径、36个模型—路径组合、180次跨站预测。
- 本站先加总测试折矩阵再算指标；跨站五次各自计算后取均值和样本标准差。来源重复关联的本站行不是独立实验。
- ΔF1=目标站本站F1−跨站五次均值，原0—1尺度；错误率增量=跨站−本站，可用百分点显示，符号与含义不同。
- 空间对象是整图同类参考连通斑块，键为 `target,PID`；不是128×128景观图块，也不等同于真实农业田块。
- 作物斑块筛选支持召回率、漏分率和定向率；完整F1必须含完整FP。净计数差不等于逐像元新增错误。
- 边界和距离作必要定位。历史距离数组、FRAGSTATS工程参数的验证范围不因计数闭合升级。

## 归档与验证

[初次归档](archive/2026-10-10-mainline/README.md)范围过宽。632份移入文件先恢复27份，2026-10-11逐项复查其余605份后再恢复413份；累计440份已回原路径，192份仍在归档。完整K2/K4结果、配置、支持、报告和探索图，以及五档候选都已恢复。恢复不批准候选，也不要求沿用旧主方案。路径见[首次恢复](archive/2026-10-10-mainline/restored-reusable.csv)、[第二次恢复](archive/2026-10-10-mainline/restored-second-pass.csv)及[全量复查](archive/2026-10-10-mainline/second-pass-review.csv)。

当前仍归档旧DR、重复F1、被后续互斥分组替代的主视图、图块景观/匹配结果和旧任务。原生产源码与测试保持`.source`历史状态，可按[源码索引](results/summary/reuse-status.md)查阅，恢复计算需先检查写入目标与依赖，不把历史脚本重新列为默认运行入口。

本次只恢复与只读核对，不产生新科研结果、不编译。原22份快照及本次12份文档快照保留。初次核查与首次纠偏仍是各自当日记录，当前以[二次核查](verification/second-pass-reuse-2026-10-11.md)为准；距离生成、FRAGSTATS工程和B站身份限制不升级。

## 工作区交接

本版一并保存整理前已有的规则、计划、交接和文献库更新；文献库原样纳入，本次未重新核验其元数据。修订前原字节快照保留，正文、正式图表、原始数据和有效F1链未变。本次按作者要求本地提交，不推送。历史任务中“当时未提交”的描述保留其时间含义，当前状态以Git记录为准。

下一次从3.1的12个独立本站基准接续，组织必要正文后再决定3.3的最小缺项。1.3 已有正文和图表，2026-10-11 授权编译后已检查第 2 页组成图及第 3 页通栏表，见[v2 核查补记](verification/sec13-figure-table-v2-2026-10-11.md)；全文仍有分页留白及字体、文献格式警告。五档未冻结，3.3 正文未写。上面的归档与提交记录仍指此前整理阶段。本轮按作者要求将 1.3 正文、图表、基础证据、核查和编译预览纳入本地提交，不推送；具体提交号以 Git 记录为准。

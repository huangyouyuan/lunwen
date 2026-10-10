# 论文交接

更新：2026-10-10。整理起点为 `a70e11b`；接手先检查 `git status --short` 和 `git log -3 --oneline`，以实际状态为准。规则见 [AGENTS.md](AGENTS.md)，总体计划见 [plan/outline.md](plan/outline.md)。

## 当前主线与优先级

四站空间背景 → 本站错误基准 → 跨站F1差距 → 错分变化与空间条件的对应关系。3.3解释3.2的具体模型、来源和方向差异；现有数据支持描述性对应，尚未证明因果机制。

| 章节 | 职责 | 当前状态 |
|---|---|---|
| 1.3研究区空间特征 | 四站参考组成、完整参考斑块分布及整站景观背景 | 两小节正文为空，已有底表待整理 |
| 3.1本站分类性能 | F1及必要的精确率、召回率和六向错分基准 | 主体和正式图已有，待最小补充 |
| 3.2跨站分类性能与差距 | 绝对F1、原尺度ΔF1、模型与来源差异 | 已有正文和表图，本次不变 |
| 3.3空间解释 | 差距对应什么错误、发生在哪里、怎样随模型来源变化 | 已有探索，正文未写；先完成基础材料 |

下一项：[1.3与3.1基础材料计划](plan/tasks/2026-10-10-sec13-sec31-foundations.md)。该计划尚未执行，不把已有底表当作新增章节已完成。正文润色交由Claude；不默认启动新统计或正文修改。

## 活动证据入口

| 用途 | 入口 |
|---|---|
| 正式F1与ΔF1 | `results/summary/f1_raw_scale/`；原矩阵在 `results/raw/` |
| 完整参考斑块与192份计数 | `results/processed/sec33_reference_patch_types/`；字典在对应summary目录 |
| 四站景观背景 | `results/summary/sec33_reference_patch_types/background_{class,landscape,adjacency}.csv`，读取 `scope=full` |
| 组成、分布与支持 | [参考分布入口](results/summary/sec33_indicator_grading_preparation/README.md) |
| 六向错分、模型分层与空间定位 | [定向混淆入口](results/summary/sec33_directional_confusion_closeout/README.md) |
| 全路径七带漏分与净贡献、逐次Δe配对 | [可复用结果索引](results/summary/README.md)中的距离表；已恢复原数值与清单，未重算 |
| 完整F1错分分量与距离共同权重 | [可复用结果索引](results/summary/README.md)中的整站表；不把分量称为因果贡献 |
| 3.3判断与缺项 | [3.3证据总览](results/summary/sec33_evidence_overview.md) |

原 `sec33_directional_confusion` 保留文件是修正脚本输入；`sec33_crop_spatial_context` 保留整站矩阵及少量可复用的整站/距离统计，其余图块和匹配结果仍归档。不得运行旧生产流程重建它们。

## 计算与解释边界

- A/B/C/D依次为iw_2023、iw2_2023、ida_2023、il_2023；12个独立本站模型—目标组合，12条迁移路径、36个模型—路径组合、180次跨站预测。
- 本站先加总测试折矩阵再算指标；跨站五次各自计算后取均值和样本标准差。来源重复关联的本站行不是独立实验。
- ΔF1=目标站本站F1−跨站五次均值，原0—1尺度；错误率增量=跨站−本站，可用百分点显示，符号与含义不同。
- 空间对象是整图同类参考连通斑块，键为 `target,PID`；不是128×128景观图块，也不等同于真实农业田块。
- 作物斑块筛选支持召回率、漏分率和定向率；完整F1必须含完整FP。净计数差不等于逐像元新增错误。
- 边界和距离作必要定位。历史距离数组、FRAGSTATS工程参数的验证范围不因计数闭合升级。

## 归档与验证

[本次归档](archive/2026-10-10-mainline/README.md)保存旧统计口径、图块分组、聚类、五档候选、旧脚本和任务。初次移入632份，复核后把27份可直接复用的底表与清单移回原结果目录，目前605份仍在归档。两段路径见[原迁移清单](archive/2026-10-10-mainline/archive-manifest.csv)和[恢复清单](archive/2026-10-10-mainline/restored-reusable.csv)。归档源码与历史测试以 `.source` 停用。

本次只整理入口和依赖，不产生科学结果、不编译。22份修订前快照保留；初次整理见[归档核查](verification/mainline-archive-2026-10-10.md)，归档范围纠偏见[复用核查](verification/mainline-retention-2026-10-10.md)。两次核查均不升级科学生成验证。B站身份限制见 [身份追溯](verification/iw2-identity-provenance.md)。

## 工作区交接

整理前已有规则、计划、交接及文献库的未提交修改；修订前已保存原字节快照。文献库修改保持原样，正文、正式图表、原始数据和有效F1链未变。本次未提交、未推送；后续提交须核查差异，不删除未跟踪文件。

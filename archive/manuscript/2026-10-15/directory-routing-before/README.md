# 玉米—大豆分类空间泛化论文

2026-10-14当前状态：景观格局及跨站均值表已保存于原历史`17eb1e4`，最新本地PDF为9页；下文带日期的“未提交”和8页说明为当时记录。详细章节主线、后续取舍与验证边界见[完整交接](HANDOVER.md)，写作执行见[流程](plan/writing-workflow.md)。

2026-10-15作者已取消缩小仓库计划。继续使用 `D:/AI/lunwen/`；额外上传副本及配套流程已归档，位置、原字节清单与用途复核见[归档说明](archive/2026-10-15-cancel-remote-plan/README.md)。AGENTS.md和忽略规则恢复到该计划前版本；完整交接、写作流程及科研成果保留。本轮未改论文或科学数据，未提交、推送。

2026-10-14景观格局更新：1.3.2围绕面积—形状联合分布组织；表1改为斑块数、AI、ENN等权P90和整站ED，联合图已接入为图3。原数据与旧版本保留，生成入口和核查见[现行展示说明](results/summary/sec13_landscape_display/README.md)；最新PDF以[预览入口](output/README.md)为准。本轮未自动提交。

当前主线：四站空间背景 → 本站错误基准 → 跨站F1差距 → 空间条件与错分变化的对应关系。

总体计划见 [plan/outline.md](plan/outline.md)，最新交接见 [HANDOVER.md](HANDOVER.md)，规则见 [AGENTS.md](AGENTS.md)。

2026-10-12现状：1.3已采用单张通栏景观表，AREA/SHAPE面积加权、ENN斑块等权；图表字体和图2/图3条形样式已统一。预览已按任务整理，最新与历史入口见[output/README.md](output/README.md)。此前成果恢复过程见[2026-10-11版本说明](plan/version-notes-2026-10-11.md)。

2026-10-13展示更新：F1及其标准差显示为百分数，F1差值显示为百分点，均保留两位小数；原尺度计算和完整精度数据不变。正文、表格和正式图的生成入口已同步，见[修改与核查清单](verification/f1-display-2026-10-13/README.md)。

2026-10-14后续调整：跨站主表仅显示平均F1，保留百分数和两位小数；逐次值与标准差保留在数据中。已更新[8页PDF](output/archive/2026-10-14/cross-f1-means-preview/manuscript.pdf)并检查表格，见[本次核查](verification/cross-f1-mean-only-2026-10-14.md)。热力图及科学结果未变，本次尚未提交。

## 活动目录

| 目录 | 用途 |
|---|---|
| `plan/` | 当前结构、口径、证据路由与具体任务 |
| `sections/`、`main.tex` | 当前正文；保存不自动编译 |
| `results/raw/` | 原始整数矩阵及FRAGSTATS结果表 |
| `results/processed/` | F1处理链、完整参考斑块和计数、可复用的逐次分析底表 |
| `results/summary/` | 科学数值权威入口，见其README |
| `figures/`、`tables/` | 正式图表及可复用探索图，后者不自动进入正文 |
| `scripts/`、`scripts/test/` | 当前数据与图表脚本、相关测试 |
| `bibliography/`、`evidence/` | 文献元数据与证据映射 |
| `verification/` | 当前核查、恢复的历史科学核查及B站身份说明 |
| `archive/` | 停用文件、原字节快照与迁移清单 |
| `legacy/`、`output/`、`word/` | 实验和写作参考、既有编译产物及投稿稿件 |

[1.3与3.1基础材料整理](plan/tasks/2026-10-10-sec13-sec31-foundations.md)已经完成，1.3已写入正文；后续从既有本站底表组织3.1必要补充，再决定3.3的具体证据。其余缺项见[当前进度](plan/progress.md)，不默认执行分级、聚类或联合建模。

## 保留脚本

| 脚本 | 职责 |
|---|---|
| `calculate_f1_raw_scale.py` | 两份raw矩阵→有效F1链，阅读前先校验已有产物 |
| `generate_core_tables.py`、`f1_display.py` | 生成12路径百分数展示表（仅平均F1）及正文数值宏；共用F1格式函数，逐次值和标准差仍保留于原数据，不写科学结果 |
| `generate_sec13_landscape_display.py` | 当前表1与面积—形状联合图；复用NP、AI、ENN等权P90、整站ED和v3联合汇总；`--check`只读核对 |
| `generate_sec13_spatial_tables.py` | 历史表1及分布核查；AREA/SHAPE面积加权、ENN等权中位数和极值原位保留 |
| `plot_sec13_composition.py` | 仅重绘现行组成图，避免调用历史组合生成器连带写入旧表 |
| `plot_within_site_f1.py`、`plot_within_site_map_D.py`、`plot_degradation_heatmap.py` | 正式图件，共享 `figstyle.py` |
| `sec33_metrics.py` | 只读指标和五次完整统计函数 |
| `explore_sec33_directional_confusion_closeout.py` | 从保留整数表计算收尾结果，已有结果本次不重跑 |
| `plot_sec33_directional_confusion_closeout.py` | 保留探索图来源，不自动写入正文 |

从仓库根目录执行必要的只读检查：

```powershell
python -B -m unittest scripts/test/test_sec33_directional_confusion_closeout.py scripts/test/test_sec33_directional_confusion.py scripts/test/test_f1_raw_scale.py scripts/test/test_f1_presentation.py -v
```

手动编译为 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`，只在授权任务中运行；2026-10-13已按F1展示统一任务重新编译为8页，完整页面预览及PDF哈希见[清单](output/preview-manifest.json)。[10月13日历史PDF快照](output/archive/2026-10-13/f1-percent-preview/manuscript.pdf)对应新展示规范；旧快照及修改前原字节备份保留，2026-10-14按作者指令随本次提交保存。

## 历史入口

初次[归档](archive/2026-10-10-mainline/README.md)范围过宽，现累计440份已恢复原路径，192份仍保留历史状态。[成果复用入口](results/summary/reuse-status.md)区分有效计数、可复用K2/K4探索、未批准五档候选与旧方案。192份按图块存储的联合计数已恢复并验证可无损恢复整站边界×距离矩阵；不将其作为图块景观分析的重启。

旧DR、重复数值链、图块AREA_MN与匹配方案、被替代主视图和旧任务仍在归档；历史源码以`.source`保留，可审阅但不自动运行。原路径按原迁移清单、首次及[第二次恢复清单](archive/2026-10-10-mainline/restored-second-pass.csv)解析。历史报告中的“K2主方案”等安排不代表当前决策。

不得删除文件或新增忽略规则制造干净状态。历史核查中的提交描述指各自记录时点；F1展示修改阶段未自动提交，2026-10-14按作者后续明确指令提交。

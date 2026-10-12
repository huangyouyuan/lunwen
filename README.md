# 玉米—大豆分类空间泛化论文

当前主线：四站空间背景 → 本站错误基准 → 跨站F1差距 → 空间条件与错分变化的对应关系。

总体计划见 [plan/outline.md](plan/outline.md)，最新交接见 [HANDOVER.md](HANDOVER.md)，规则见 [AGENTS.md](AGENTS.md)。

2026-10-12现状：1.3已采用单张通栏景观表，AREA/SHAPE面积加权、ENN斑块等权；图表字体和图2/图3条形样式已统一。预览已按任务整理，最新与历史入口见[output/README.md](output/README.md)。此前成果恢复过程见[2026-10-11版本说明](plan/version-notes-2026-10-11.md)。

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
| `generate_core_tables.py` | 仅生成现行12路径正文表，不生成旧口径和检验表 |
| `generate_sec13_spatial_tables.py` | 当前表1；优先用`--check`只读核对，AREA/SHAPE面积加权、ENN斑块等权 |
| `plot_sec13_composition.py` | 仅重绘现行组成图，避免调用历史组合生成器连带写入旧表 |
| `plot_within_site_f1.py`、`plot_within_site_map_D.py`、`plot_degradation_heatmap.py` | 正式图件，共享 `figstyle.py` |
| `sec33_metrics.py` | 只读指标和五次完整统计函数 |
| `explore_sec33_directional_confusion_closeout.py` | 从保留整数表计算收尾结果，已有结果本次不重跑 |
| `plot_sec33_directional_confusion_closeout.py` | 保留探索图来源，不自动写入正文 |

从仓库根目录执行必要的只读检查：

```powershell
python -B -m unittest scripts/test/test_sec33_directional_confusion_closeout.py scripts/test/test_sec33_directional_confusion.py scripts/test/test_f1_raw_scale.py scripts/test/test_f1_presentation.py -v
```

手动编译为 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`，只在授权任务中运行；当前稿件为8页，最新第3、5页预览及PDF哈希见[清单](output/preview-manifest.json)，本次归档与交接未重建。[当前PDF快照](output/previews/2026-10-12-figure23-bars/manuscript.pdf)及两组完整修改前备份均已纳入Git，详见[工作区交接](HANDOVER.md#工作区交接)。

## 历史入口

初次[归档](archive/2026-10-10-mainline/README.md)范围过宽，现累计440份已恢复原路径，192份仍保留历史状态。[成果复用入口](results/summary/reuse-status.md)区分有效计数、可复用K2/K4探索、未批准五档候选与旧方案。192份按图块存储的联合计数已恢复并验证可无损恢复整站边界×距离矩阵；不将其作为图块景观分析的重启。

旧DR、重复数值链、图块AREA_MN与匹配方案、被替代主视图和旧任务仍在归档；历史源码以`.source`保留，可审阅但不自动运行。原路径按原迁移清单、首次及[第二次恢复清单](archive/2026-10-10-mainline/restored-second-pass.csv)解析。历史报告中的“K2主方案”等安排不代表当前决策。

不得删除文件或新增忽略规则制造干净状态。本次按作者要求本地提交预览归档和交接更新，不推送；历史核查中的“未提交”指各自记录时点。

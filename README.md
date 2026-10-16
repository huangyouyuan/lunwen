# 玉米—大豆分类空间泛化论文

当前整稿只打开[output/main.pdf](output/main.pdf)。正文入口是根目录`main.tex`；命令行与VS Code默认编译到`output/`，辅助文件在`output/build/main/`。根目录PDF和原`output/previews/`已退出活动流程，见[归档与默认输出核查](verification/default-output-2026-10-15.json)。

## 从哪里开始

| 需要做什么 | 入口 |
|---|---|
| 查必须遵守的规则 | [AGENTS.md](AGENTS.md) |
| 看当前稿和编译文件 | [output/README.md](output/README.md) |
| 理清写作顺序、目录和各文档职责 | [写作与文件组织流程](plan/writing-workflow.md) |
| 看当前完成状态和下一步 | [progress.md](plan/progress.md) |
| 接手研究背景、决策与限制 | [HANDOVER.md](HANDOVER.md) |
| 找章节安排及已有证据 | [outline.md](plan/outline.md)、[results-map.md](plan/results-map.md)、[科学结果入口](results/summary/README.md) |
| 查旧稿和归档位置 | [archive/manuscript/README.md](archive/manuscript/README.md) |

本文件负责导航；完整文档职责与更新规则集中在写作流程中。下方带日期的状态和提交说明保留当时范围，不代表当前稿页数或本次复验。

## 既有状态记录（历史时点）

2026-10-14当前状态：景观格局及跨站均值表已保存于原历史`17eb1e4`，最新本地PDF为9页；下文带日期的“未提交”和8页说明为当时记录。详细章节主线、后续取舍与验证边界见[完整交接](HANDOVER.md)，写作执行见[流程](plan/writing-workflow.md)。

2026-10-15作者已取消缩小仓库计划。继续使用 `D:/AI/lunwen/`；额外上传副本及配套流程已归档，位置、原字节清单与用途复核见[归档说明](archive/2026-10-15-cancel-remote-plan/README.md)。AGENTS.md和忽略规则恢复到该计划前版本；完整交接、写作流程及科研成果保留。本轮未改论文或科学数据，未提交、推送。

2026-10-14景观格局更新：1.3.2围绕面积—形状联合分布组织；表1改为斑块数、AI、ENN等权P90和整站ED，联合图已接入为图3。原数据与旧版本保留，生成入口和核查见[现行展示说明](results/summary/sec13_landscape_display/README.md)；最新PDF以[预览入口](output/README.md)为准。本轮未自动提交。

当前主线：四站空间背景 → 本站错误基准 → 跨站F1差距 → 空间条件与错分变化的对应关系。

总体计划见 [plan/outline.md](plan/outline.md)，最新交接见 [HANDOVER.md](HANDOVER.md)，规则见 [AGENTS.md](AGENTS.md)。

2026-10-12现状：1.3已采用单张通栏景观表，AREA/SHAPE面积加权、ENN斑块等权；图表字体和图2/图3条形样式已统一。预览已按任务整理，最新与历史入口见[output/README.md](output/README.md)。此前成果恢复过程见[2026-10-11版本说明](plan/tasks/version-notes-2026-10-11.md)。

2026-10-13展示更新：F1及其标准差显示为百分数，F1差值显示为百分点，均保留两位小数；原尺度计算和完整精度数据不变。正文、表格和正式图的生成入口已同步，见[修改与核查清单](verification/f1-display-2026-10-13/README.md)。

2026-10-14后续调整：跨站主表仅显示平均F1，保留百分数和两位小数；逐次值与标准差保留在数据中。已更新[8页PDF](archive/manuscript/2026-10-14/cross-f1-means-preview/manuscript.pdf)并检查表格，见[本次核查](verification/cross-f1-mean-only-2026-10-14.md)。热力图及科学结果未变，本次尚未提交。

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
| `verification/` | 核查记录、B站身份说明；页面检查图片放在`layout/<任务>/` |
| `archive/` | 停用文件与原字节快照；稿件旧版、试排和备份集中在`manuscript/<日期>/<任务>/` |
| `output/` | 唯一当前整稿`main.pdf`、源码跳转信息与`build/`编译工作区 |
| `legacy/`、`word/` | 实验和写作参考、Word投稿稿件 |

[1.3与3.1基础材料整理](plan/tasks/2026-10-10-sec13-sec31-foundations.md)已经完成，1.3已写入正文；3.1四站差异案例与全站漏分衔接见[当前任务](plan/tasks/2026-10-16-sec31-spatial-error-figure.md)和[统计入口](results/summary/sec31_spatial_examples/README.md)。其余缺项见[当前进度](plan/progress.md)，不默认执行分级、聚类或联合建模。

## 保留脚本

| 脚本 | 职责 |
|---|---|
| `calculate_f1_raw_scale.py` | 两份raw矩阵→有效F1链，阅读前先校验已有产物 |
| `generate_core_tables.py`、`f1_display.py` | 生成12路径百分数展示表（仅平均F1）及正文数值宏；共用F1格式函数，逐次值和标准差仍保留于原数据，不写科学结果 |
| `generate_sec13_landscape_display.py` | 当前表1与面积—形状联合图；复用NP、AI、ENN等权P90、整站ED和v3联合汇总；`--check`只读核对 |
| `generate_sec13_spatial_tables.py` | 历史表1及分布核查；AREA/SHAPE面积加权、ENN等权中位数和极值原位保留 |
| `plot_sec13_composition.py` | 仅重绘现行组成图，避免调用历史组合生成器连带写入旧表 |
| `plot_within_site_f1.py`、`plot_degradation_heatmap.py` | 正式F1图件，共享 `figstyle.py` |
| `plot_within_site_errors.py` | 当前图4：四站最大对错分歧窗口、局部统计及作物对错图；`--prepare`后`--plot`，同名输出不覆盖 |
| `plot_within_site_map_D.py` | 历史D站示例来源，图件原位保留，不再作为当前正式入口 |
| `sec33_metrics.py` | 只读指标和五次完整统计函数 |
| `explore_sec33_directional_confusion_closeout.py` | 从保留整数表计算收尾结果，已有结果本次不重跑 |
| `plot_sec33_directional_confusion_closeout.py` | 保留探索图来源，不自动写入正文 |

从仓库根目录执行必要的只读检查：

```powershell
python -B -m unittest scripts/test/test_sec33_directional_confusion_closeout.py scripts/test/test_sec33_directional_confusion.py scripts/test/test_f1_raw_scale.py scripts/test/test_f1_presentation.py -v
```

手动编译为`latexmk -xelatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex`，只在授权任务中运行；`.latexmkrc`默认生成`output/main.pdf`。编译与归档步骤见[写作流程](plan/writing-workflow.md)。[10月13日历史PDF快照](archive/manuscript/2026-10-13/f1-percent-preview/manuscript.pdf)及旧快照、修改前版本继续保留，2026-10-14按作者指令随当次提交保存。

## 历史入口

初次[归档](archive/2026-10-10-mainline/README.md)范围过宽，现累计440份已恢复原路径，192份仍保留历史状态。[成果复用入口](results/summary/reuse-status.md)区分有效计数、可复用K2/K4探索、未批准五档候选与旧方案。192份按图块存储的联合计数已恢复并验证可无损恢复整站边界×距离矩阵；不将其作为图块景观分析的重启。

旧DR、重复数值链、图块AREA_MN与匹配方案、被替代主视图和旧任务仍在归档；历史源码以`.source`保留，可审阅但不自动运行。原路径按原迁移清单、首次及[第二次恢复清单](archive/2026-10-10-mainline/restored-second-pass.csv)解析。历史报告中的“K2主方案”等安排不代表当前决策。

不得删除文件或新增忽略规则制造干净状态。历史核查中的提交描述指各自记录时点；F1展示修改阶段未自动提交，2026-10-14按作者后续明确指令提交。

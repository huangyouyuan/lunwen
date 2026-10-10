# 3.3 第三轮探索：边界距离带与跨站净增错误

## 范围

本轮复用既有七个边界距离带的整数混淆矩阵，分析跨站相对本站增加的类内漏分率、净增错误数及其对全站漏分率差的带内贡献。结果均为 `derived / exploratory`，不写入正文，不修改 3.1、3.2、冻结分组或历史边界结果，不重训、不重新推理、不重跑 FRAGSTATS、不编译、不推送。

## 执行步骤

1. 核对 Git 状态、AGENTS、实验协议、前两轮报告、旧边界脚本、距离定义、边界矩阵和历史身份核查。
2. 不运行会写回 `results/processed/sec33_exploration/` 的旧生产流程；从既有 `boundary_within_cm.csv`、`boundary_cross_fold_cm.csv` 及当前总体 CM 只读派生。
3. 核查七带键、三类矩阵、模型/来源/目标/五次覆盖、七带求和恢复总体矩阵，并记录旧距离数组、标签身份和 GeoKey 限制，不自动修补。
4. 按目标站、作物、模型、来源和距离带计算本站漏分率、跨站五次漏分率均值/标准差、差值、像元占比、净增错误数和带内总体漏分率差贡献；保留全体像元和其它类补充结果。
5. 针对最近带与 `>6` 带按相同源模型预测逐次配对，保留方向、范围和负值；针对 D 站大豆提取大豆→玉米、大豆→其它两种漏分率差，并核查两者恢复大豆 Δe。
6. 生成独立目录 `results/processed/sec33_round3_distance/`、`results/summary/sec33_round3_distance/`、`figures/exploratory/sec33_round3_distance/`，包括完整底表、汇总表、核查表、哈希清单、图件和探索报告。
7. 新增必要内存测试至 `scripts/test/`；实际查看图件和运行测试，记录 Verified / Partially verified 状态。

## 计算口径

距离带固定为 `(0,1]`、`(1,2]`、`(2,3]`、`(3,4]`、`(4,5]`、`(5,6]`、`>6` 像元。本站先汇总分带矩阵后计算漏分率；跨站每次分别计算后取五次均值和样本标准差。`Δe = 跨站均值 - 本站`，`p = N(c,b)/N(c,全站)`，带内净增错误为跨站错误数均值减本站错误数，`C = p × Δe`。七带 C 之和必须恢复全站漏分率差。不得以带内错误率代替贡献，也不以 ΔF1 替代漏分率差。

## 预期交付

- `scripts/explore_sec33_round3_distance.py`
- `scripts/test/test_sec33_round3_distance.py`
- 独立 processed / summary / figure 目录
- `verification/sec33-round3-distance-2026-10-05.md`
- 本文件执行记录及 `results/summary/sec33_round3_distance/run_manifest.json`

## 执行记录

- 计划建立：2026-10-05。
- HEAD：`db026b4`；接手时未跟踪 `.claude/settings.local.json` 原样保留。

## 执行结果（2026-10-05）

- 已完成 `scripts/explore_sec33_round3_distance.py`，只读取既有七带混淆矩阵和当前总体矩阵，产物写入独立的 `sec33_round3_distance` 目录，未覆盖历史边界结果。
- 已生成 336 条站内分带指标、5040 条跨站逐次分带指标和 1008 条跨站分源汇总，保留全体、玉米、大豆和其它类；另生成最近带—`d>6` 配对、带内贡献闭合及 D 站大豆两类漏分方向分解。
- 386 项脚本核查均为 `Verified`：七带完整性、键唯一、五次覆盖、分带矩阵恢复总体矩阵、目标支持量一致、带内贡献闭合和 D 站大豆分解闭合均通过。
- 已实际查看四张探索图。总体漏分率图同时显示站内与三源等权跨站均值；贡献图同时显示带内贡献和目标类像元占比；D 站大豆图保留三模型、三来源和两类漏分方向。
- 主要发现已写入 `results/summary/sec33_round3_distance/exploration-report.md`：绝对漏分率在最近带普遍更高，但相对本站的额外漏分并非总在最近带最大；D 站大豆 B 源 ConvGRU 的内部额外漏分主要由大豆错成玉米维持，模型和来源会改变距离分布。
- 新增数据字典 `results/summary/sec33_round3_distance/data_dictionary.md` 和核查记录 `verification/sec33-round3-distance-2026-10-05.md`。
- 空间指标仍标为 `Partially verified`：本轮未重新执行原始 EDT；历史记录中的 2 处参考指纹不一致和 1 处 GeoTIFF 缺完整 CRS GeoKey 保留为限制，未自动修补。
- 新增内存测试 6 项已通过；尚待在提交前运行 `python -B -m unittest discover -s scripts/test -p "test_*.py" -v`、`git diff --check` 和最终 `git status --short`。

## 文档补记（2026-10-05）

- 已补充第三轮执行后实验说明：`results/summary/sec33_round3_distance/experiment-and-results.md`。
- 已补充前三轮 3.3 执行后汇总：`results/summary/sec33_experiments_and_results.md`。该文档汇总共同口径、三轮结果、证据衔接、局部例外、未获支持的关系、类别组成限制及验证状态，不替代事前计划，也不写入论文正文。
- 本次仅进行了文档整理、路径核对和 SHA-256 计算，没有重新运行分析脚本、测试套件或论文编译。
- 文档 SHA-256：
  - `results/summary/sec33_round3_distance/experiment-and-results.md`：`B6A7CEBCEEB34A5706B24B6EA15024C9CC8903272542827E8170BC878F08D309`
  - `results/summary/sec33_experiments_and_results.md`：`98BA8510B6B80A8DBA37E52B75D05DEFFCB33C17CAD52609B176AFBBAC7FA98C`

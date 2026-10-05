# 3.3 第二轮探索：探索图与 D 站大豆误差分解

## 范围

本轮基于提交 `3df36f8` 的 AREA_MN 原尺度 ΔF1 结果，制作探索图并对 D 站大豆的四类混淆去向进行针对性分解。结果均标记为 `derived / exploratory`，不修改 3.1、3.2、正文、冻结分组和历史 DR 结果，不重训、不重新推理、不重跑 FRAGSTATS、不编译、不推送。

## 执行步骤

1. 核对 Git 状态、上一轮探索报告、数据字典、核查记录、分组矩阵和现有输入哈希。
2. 复用 `sec33_f1_raw_scale` 的冻结分组、分组特征和整数混淆矩阵，先做 D 站大豆误差分量的内存重算与闭合核查。
3. 新增独立脚本，输出总体关系图、D 站大豆分源图、组成对照图，以及完整分解底表和汇总表到 `figures/exploratory/sec33_round2/`、`results/processed/sec33_round2/` 和 `results/summary/sec33_round2/`；不覆盖历史目录。
4. 对四类误差分别计算本站分量、跨站五次逐次分量、五次均值及其差值；核查四项差值之和恢复同组 ΔF1，并保留 NA、负值、支持量和五次方向一致性。
5. 对图件执行数值来源、键覆盖、单位、图例、坐标范围和导出文件核查；只增加与新计算直接相关的内存测试。
6. 形成简短报告，回答总体关系、D 站大豆例外、模型与来源差异、类别组成伴随变化及最小后续方案；不写正文。

## 预期交付

- `scripts/explore_sec33_round2.py`
- `scripts/test/test_sec33_round2.py`
- `results/processed/sec33_round2/`
- `results/summary/sec33_round2/`
- `figures/exploratory/sec33_round2/`
- `verification/sec33-round2-2026-10-05.md`
- 本文件的执行记录

## 验证口径

本站按组汇总 OOF 混淆矩阵后计算 F1；跨站五次分别汇总同组混淆矩阵、分别计算 F1 和误差分量后取算术均值，标准差使用 `ddof=1`。大豆 `Z=2TP+FP+FN`，四项误差分量分别为 `FN_soy_to_corn/Z`、`FN_soy_to_other/Z`、`FP_soy_from_corn/Z`、`FP_soy_from_other/Z`；四项之和等于 `1-F1_soy`。跨站均值分量减本站分量的四项之和必须等于 ΔF1。按真实类别像元数归一化的误分类率与上述 F1 分量分开保存和解释。

## 执行记录

- 计划建立：2026-10-05。
- Git 基线：`3df36f8`；原有 `.claude/worktrees/` gitlink 工作区状态按既有本地排除设置保留。
- 实际执行和核查结果在本文件末尾追加，不覆盖本计划内容。

## 执行记录（2026-10-05）

- **Verified**：基于 `3df36f8` 复用第一轮 `sec33_f1_raw_scale` 的冻结分组、分组特征和整数混淆矩阵；未重新分组、重训、重新推理、重跑 FRAGSTATS、编译或推送。原始目录未触发回溯，原因和核查范围见 `verification/sec33-round2-2026-10-05.md`。
- **Verified**：生成总体 AREA_MN—F1/ΔF1 图、D 站大豆三模型三来源 F1/ΔF1 图、类别组成对照图和四类误差分量图；图件使用实际组内 AREA_MN 中位数，分源结果保留，误差线明确为五次预测的样本标准差而非置信区间。总体 ΔF1 图图注已修正为 ΔF1 含义。
- **Verified**：D 站大豆覆盖 12 个本站模型—组结果、180 个跨站逐次预测和 36 个模型—来源—组汇总；保留支持量、Precision、Recall、按真实类别分母的误分类率和 `Z` 归一化的 F1 误差分量。
- **Verified**：四类分量之和恢复 `1-F1`，最大绝对误差 `5.55e-17`；四项分量差值之和恢复原尺度 ΔF1，最大绝对误差 `1.70e-16`；五次方向标签写入 `d_soybean_key_contrasts.csv`。
- **Verified**：`python -B -m unittest discover -s scripts/test -p "test_*.py" -v` 共 39 项通过；`python -B scripts/explore_sec33_round2.py --check-only` 通过；`git diff --check` 通过。独立核查记录见 `verification/sec33-round2-2026-10-05.md`，运行输入、脚本和产物 SHA-256 见 `results/summary/sec33_round2/run_manifest.json`。
- **Partially verified**：空间指标 AREA_MN 和类别组成沿用第一轮已核验表，本轮没有从原始标签重新计算；因此报告仅作对应关系解释，不作独立作用或因果结论。

# 论文写作系统交接文档

**最后更新**：2026-10-09（3.3 证据总览与状态同步；未注明日期的其余内容沿用 2026-10-03 交接）

## 一句话状态

本项目仅维护美国四站点空间泛化论文，围绕“站内基准 → 美国站间退化 → 空间解释”组织正文与结果。

## 角色与边界

- 用户是作者：确定论点、骨架、图表设计、目标期刊和最终文字；所有“要不要”的决定归用户。
- AI 负责执行与核查：从权威数据现算数字、出草稿、画图、编译、维护计划文件与 Git。
- 正文数字只从 `results/summary/` 读取并现算，必须能回溯到脚本、processed 和 raw。
- 不改变 `results/`、`tables/` 的既有口径；如需新增口径，先建立处理链并验证。
- 不 push；提交前只暂存本步相关文件。
- 正常正文修改不自动编译；用户要求验证、复杂 LaTeX 修改或最终检查时才编译。
- 文件职责（作者 2026-09-30—10-01 明确）：`AGENTS.md` 是最终硬规则，一般不改；本文件只在交接时更新；任务计划和执行记录放 `plan/tasks/`。写作口径归 `plan/style-guide.md`，指标定义归 `plan/experiment-protocol.md`，论点与数据映射只做必要局部同步。一次任务先限定文件范围，不顺带改流程、配色或无关文档；需回退时先保全再选择性迁移，不整文件覆盖。

## 论文范围

暂用题目：**时空深度学习模型在玉米—大豆分类中的空间泛化能力分析**

主线：**站内基准 → 美国站间退化 → 空间解释**

数据范围：美国 4 站点 2023 年（A、B 爱荷华州，C 印第安纳州，D 伊利诺伊州）；ConvGRU、3D U-Net、U-TAE；站内 12 组实验；跨站 12 条有向迁移路径 × 3 模型 = 36 个模型—路径组合、180 次完整目标站预测。

顶层 `plan/`、`sections/`、`results/`、`tables/` 和现有结果图服务于该文。

## 当前状态

- 3.1 已润色定稿：第一段讲三模型共同表现，第二段结合图 3 讲差异。
- 图 2、图 3 已按 3.8 cm 基本单元、逐子图 PDF、LaTeX 文本图题与图例的规范提交。
- 结果章固定为 3.1—3.3，当前不设第三级标题。
- 3.2 三段已按科学准确、通俗易懂完成两轮润色（2026-10-03，第一轮 `e889255`，第二轮按作者审阅意见修改，待作者终审）：
  - 第一段：段首给出“36 个模型—路径组合的两作物跨站 F1 均低于同一模型目标站站内汇总 F1”，再给范围。A/C 站改为“按目标站对 3 条路径取平均”比较——原“玉米最低值在 C”依赖 ConvGRU B→C 与 B→D 仅差 0.0005（表中均为 0.86），读者无法核对；平均后 A 最高、C 玉米最低在三模型中均成立，大豆最低目标站因模型而异。
  - 第二段：段首判断为“ConvGRU 的跨站 F1 均值最低，但平均 F1 差值最小”。不要写“两项指标排序不同”——按数值从大到小两项顺序相同（U-TAE、3D U-Net、ConvGRU），差别在于高跨站 F1 与小差值没有出现在同一模型。差距写“约低 0.01～0.02”。
  - 第三段：固定目标站 D 的 ConvGRU 大豆例子保留五次范围（C→D 五次均约 0.01，B→D 五次 0.03～0.11），用途已写明：B→D 每次都高于 C→D，同时五次波动更大。B↔D 方向差异限于五次均值，不推广；结尾以“将在后文结合地物组成与景观结构分析”衔接 3.3。
- 当前口径（2026-09-30 决定，54a2a18 已实现）：跨站绝对 F1 + 原尺度差值 ΔF1，显示两位小数；差值为同模型目标站站内汇总 F1 减跨站五次均值，不除基准、不乘 100。旧 DR 选择已被替代；不作显著性结论、路径计数只作描述的限制仍有效。
- 四站所在州已按研究区 SHP / 标签 GeoTIFF 叠加州界核实，`02_data.tex` 原“明尼苏达州”已改正。
- 3.3 回答两个问题并覆盖全部站点和路径：目标站在哪些空间条件下退化较大；同一目标站的退化随源站变化与站点间哪些差异相对应。2026-10-05—09 已完成原尺度 ΔF1 分组、距离带、作物空间背景、整图单斑块类型（K=2 主、K=4 敏感性）、六向定向混淆及指标分级准备等探索，均已提交，结果为 derived / exploratory，正文未引用。**证据入口为 `results/summary/sec33_evidence_overview.md`**：逐条列出 3.2 现象能解释到哪一步、候选发现、不能写的结论、未落盘的预检和待定事项。要点：碎片化（微小斑块）对应“本来就难”而非跨站新增；主体斑块的新增错误集中在边界带并错向对侧类别；B→D 大豆→玉米延续到斑块内部；源站依赖不能由现有空间特征解释。派生计数 Verified；历史距离生成与 FRAGSTATS 原工程配置 Partially verified。旧 DR 探索（`results/*/sec33_exploration/`）仅作历史。
- 编译核查（2026-10-03）：`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` exit 0，PDF 6 页；第 2 页方法（含 ΔF1 公式），第 3 页 3.1 与图 2，第 4 页图 3 与 3.2 三段，第 5 页表 1 与图 4，第 6 页起 3.3。日志无 Overfull/Underfull、无未定义引用；字体替代与空参考文献为既有提示，不为消告警改版式。预览 `output/sec32_p-{2,3,4,5}.png` 与两个表图副本已重导出，逐页独立渲染哈希一致，绑定见 `output/preview-manifest.json`。编译前 PDF 与清单副本在 `D:/AI/lunwen_archive/before-build-20261003-142140/`。
- 引言、1.3、2.1 三模型、结论与摘要尚未完成。
- 段落与各级标题前后间距统一为 0 pt，取消栏底对齐和浮动页间距拉伸；图表间距固定 3 pt（2026-09-23）。

3.2 核心命题：**站内分类精度在跨站后能否保持，以及相对目标站当地训练基准的差距如何随模型和源—目标组合变化。**

## 可用数据与结果

- `results/summary/f1_raw_scale/within_site_crop_f1.csv`：站内汇总玉米 F1、大豆 F1、OA。
- `results/summary/f1_raw_scale/within_site_crop_f1_fold_stats.csv`：五折均值与折间标准差。
- `results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv`：36 个模型—路径组合的跨站绝对精度（5 次预测均值与标准差）。
- `results/summary/f1_raw_scale/crop_f1_difference_36paths.csv`：当前正文与图 4 的原尺度 F1 差值。
- `results/summary/crop_f1_relative_degradation_36paths.csv`：历史 DR，仅供追溯，不作当前正文数据。
- `results/summary/crop_f1_degradation_36paths.csv`：百分点差值，仅备查，正文不引用。
- `tables/table2_cross_site_f1_12paths.csv`：3.2 正文表，12 条迁移路径的三模型玉米和大豆 F1。
- `tables/table2_cross_site_summary.csv`：模型与作物汇总，只作分析备查。
- `tables/table3_significance_tests.csv`：Friedman、Wilcoxon 与 Holm 校正结果，仅供追溯，不进入正文。

当前数据链：`scripts/calculate_f1_raw_scale.py` 从 `results/raw/` 整数混淆矩阵经 `results/processed/f1_raw_scale/` 生成上列 `f1_raw_scale/` 汇总（17 位有效数字），正文、表、图只在显示时保留两位小数；类别顺序为玉米、其它、大豆。`scripts/test/` 共 25 项测试（3.3 协议 7、F1 数据链 15、表图呈现 3），2026-10-03 全部通过。迁移过程、选择性取用和验证范围见 `plan/tasks/f1-scale-migration-checklist.md`；口径入口清理见 `plan/tasks/2026-10-02-guidance-cleanup.md`。2026-10-03 润色时 3.2 每个数字与比较均从全精度数据复核。差值以同一模型在目标站的站内汇总 F1 为基准，表示相对当地训练基准的差距，不是理论上限。更早的旧口径核查见 `plan/progress.md` 与 `verification/verification-report.md`，仅作历史。

仍为旧口径、不作当前入口的：`scripts/run_all_updates.ps1`（旧四步流程，含 DR 与历史备查表）、`tables/table1*`、`table2_cross_site_summary.csv`、`table3_significance_tests.csv`、`results/summary/` 根目录下的六位小数汇总。

## 写作入口

- 主线与边界：`plan/paper-context.md`
- 章节框架：`plan/outline.md`
- 论点与数据链：`plan/claims.md`
- 实验定义：`plan/experiment-protocol.md`
- 节与数据映射：`plan/results-map.md`
- 当前进度：`plan/progress.md`
- 唯一写作规范：`plan/style-guide.md`
- 排版与绘图规范：`plan/format-spec.md`

## 下一步

1. 作者终审 3.2 二轮润色稿；数字与版面已核查。3.1 若需按同一标准润色，先读 3.1 现文与 `plan/claims.md` 顶部当前证据表。
2. 3.3（2026-10-09）：按证据总览第 5 节逐项定稿——图块尺度与斑块尺度结论的统一（边界比例桥接未检验）、边界带取 ≤1 还是 ≤2 像元、是否做 AREA/SHAPE 共同分档（ENN 不可分级）、选 1—2 张图——再起草正文。第 4 节预检数字须正式复算落盘后才能引用。3.3 依赖 1.3 地物组成与景观格局，二者正文仍为空。
3. 完成引言、1.3、2.1 三模型、结论与摘要（正文中这些小节目前为空，管理注释已移到 `plan/tasks/2026-10-02-guidance-cleanup.md`）。结论按当前证据起草，不迁移旧 Word 内容。

## 历史 3.3 探索协议（冻结 DR，不作当前差值分析指令）

plan/sec33-exploration-protocol.md：3.3 第一轮探索协议，固定文档化分组规则（ED与AREA_MN线性插值分位点、低中高组、缺失组、CM闭合）、精度与退化计算（DR、站内F1/跨站F1五次均值）、描述性比较、边界距离指标（带内错误率、像元占比、对总体贡献）。不撰写正式正文、不编译、不改3.2。所有新结果标为 derived / exploratory。

## 系统整理入口（2026-09-29）

禁止删除任何文件，只归档；具体规则见 `AGENTS.md`。唯一确认的协议单元测试已集中至 `scripts/test/`，两种运行入口各 7 项通过。停用迁移地图与五张历史预览位于 `archive/2026-09-29-system整理/`；旧路径与 SHA-256 见归档清单，当前预览入口不变。当前脚本分层与测试命令见 `README.md`，当时核验及限制见 `verification/system-audit-2026-09-29.md`。上述整理已在 `8eb43b6` 提交；禁止为了满足“工作区干净”删除未跟踪成果。

## B 站身份问题：接手必读（2026-09-30）

完整来龙去脉见 [B 站身份问题追溯](verification/iw2-identity-provenance.md)。B 站生产时曾沿用 A 站身份，已有数据及运行迁移；U-TAE 五折共 400 行冗余 site 字段修复经备份对比确认仅此字段变化，15 条 B 来源跨站 CM 关联一致。3D U-Net 与 U-TAE 的两条旧参考指纹已精确复算定位：旧 dataset_id 和 UID 前缀生成的指纹未随身份迁移更新，实际标签及空间契约一致。U-TAE B 站站内 TIFF 存在并有 B 站定位，只缺完整 CRS GeoKey，不是标签缺失，也不是指纹差异的原因。上述限定范围 Verified；旧契约完整字节恢复仍 Partially verified。不得要求为此重跑景观指数或边界清单，不改历史报告布尔值。

## Git 追溯

作者要求整个写作系统的有效改动入库，任务收尾时核对暂存区、工作区和未跟踪文件。参考论文 PDF、编译辅助文件及指定名称的页面预览按既有规则排除；已跟踪的 `output/sec32_p-{2,3,4,5}.png` 继续更新并入库，`output/preview-manifest.json` 同步记录其来源。正式图件、文献库和全部计划继续跟踪。范围与预览重建命令见 `README.md`。禁止用删除文件或新增忽略规则制造干净状态；不 push。

交接时的 Git 现状（2026-10-03）：
- 主分支 `master`；本地保留分支 `wip/f1-scale-review`（F1 口径中途现场，含两轮快照，只供追溯，不整体合并）、`chore/system-cleanup-20260930`、`fix/*`（均已快进并入）。独立副本 `D:/AI/lunwen_archive/f1-scale-review-1704e3e/` 及若干编译前、清理前副本也在 `D:/AI/lunwen_archive/`。
- 2026-10-09 同步：HEAD `729eff5`；`bibliography/references.bib` 有作者导入的未提交修改（新增 Wei 等 2020、陈万旭等 2024，另有若干条目被导出改为 `eid` 等格式，提交前需核对出版信息）。下条所述两个 gitlink 仍被跟踪，但当前 `git status` 已不显示其标记。
- `.claude/worktrees/agent-a47dd4da14feaac10`、`agent-a5294d1b5a8ca0e65` 是临时子代理工作区。`b240e2f` 曾将其解除跟踪，但作者提交 `e889255` 时又以 gitlink 形式纳入（无 `.gitmodules`），两个工作区内部分别有未提交修改和未跟踪文件，故 `git status` 显示 `m` 和 `?`。是否保留跟踪由作者决定；不要删除这两个目录。

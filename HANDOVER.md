# 论文写作系统交接文档

**最后更新**：2026-09-30

## 一句话状态

本项目仅维护美国四站点空间泛化论文，围绕“站内基准 → 美国站间退化 → 空间解释”组织正文与结果。

## 角色与边界

- 用户是作者：确定论点、骨架、图表设计、目标期刊和最终文字；所有“要不要”的决定归用户。
- AI 负责执行与核查：从权威数据现算数字、出草稿、画图、编译、维护计划文件与 Git。
- 正文数字只从 `results/summary/` 读取并现算，必须能回溯到脚本、processed 和 raw。
- 不改变 `results/`、`tables/` 的既有口径；如需新增口径，先建立处理链并验证。
- 不 push；提交前只暂存本步相关文件。
- 正常正文修改不自动编译；用户要求验证、复杂 LaTeX 修改或最终检查时才编译。

## 论文范围

暂用题目：**时空深度学习模型在玉米—大豆分类中的空间泛化能力分析**

主线：**站内基准 → 美国站间退化 → 空间解释**

数据范围：美国 4 站点 2023 年（A、B 爱荷华州，C 印第安纳州，D 伊利诺伊州）；ConvGRU、3D U-Net、U-TAE；站内 12 组实验；跨站 12 条有向迁移路径 × 3 模型 = 36 个模型—路径组合、180 次完整目标站预测。

顶层 `plan/`、`sections/`、`results/`、`tables/` 和现有结果图服务于该文。

## 当前状态

- 3.1 已润色定稿：第一段讲三模型共同表现，第二段结合图 3 讲差异。
- 图 2、图 3 已按 3.8 cm 基本单元、逐子图 PDF、LaTeX 文本图题与图例的规范提交。
- 结果章固定为 3.1—3.3，当前不设第三级标题。
- 3.2 三段已完成本轮收尾（2026-09-29，待作者审阅）。第一段只报告跨站 F1、目标站基准及 A/C 站观察，不推断分类难度；第二段集中比较 12 条路径的平均 F1 与平均 F1 差值，删去重复排名和模型差距数字；第三段保留固定目标站 D 的源站差异与 B↔D 两模型方向差异，限于五次预测均值，用一句话衔接空间分析。
- 当前口径（2026-09-30 决定，54a2a18 已实现）：跨站绝对 F1 + 原尺度差值 ΔF1，显示两位小数；差值为同模型目标站站内汇总 F1 减跨站五次均值，不除基准、不乘 100。旧 DR 选择已被替代；不作显著性结论、路径计数只作描述的限制仍有效。
- 四站所在州已按研究区 SHP / 标签 GeoTIFF 叠加州界核实，`02_data.tex` 原“明尼苏达州”已改正。
- 3.3 回答两个问题并覆盖全部站点和路径：目标站在哪些空间条件下退化较大；同一目标站的退化随源站变化与站点间哪些差异相对应。2026-09-29 接手核查发现分组 F1/DR 与边界探索链已有成果，现已入库；DR 为历史探索口径，新差值分析尚未迁移，位于 `results/processed/sec33_exploration/` 和 `results/summary/sec33_exploration/`，不再是“待建”。本轮核对现有清单哈希一致；整体 Partially verified，未从标签重算空间指标，边界元数据仍有异常，候选图目录不存在。详见 `verification/system-audit-2026-09-29.md`。外部输入仍在 `D:/label/fragstats_results/` 和 `D:/cross_site_all_20260916/paper_tables/Patch级空间误差底表/`。
- 图表位置已编译核查（2026-09-29）：新 PDF 第 4 页为图 3 与 3.2 三段正文，第 5 页为表 1 和图 4，第 6 页起为 3.3 标题。允许通栏表图延后，未调整间距强行塞页；无未定义引用、文字截断或溢出。当前预览 `output/sec32_p-{3,4,5}.png` 及两个表图预览入口均来自新 PDF；生成时间、哈希与构建时版本状态见 `output/preview-manifest.json`，不用历史 `results_layout-*`、`results_spacing-*` 判断当前版面。
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

数据处理链的既有验证见 `plan/progress.md` 2026-09-26—27 记录；类别顺序为玉米、其它、大豆。2026-09-29 本轮从 summary 核对 3.2 全部数值、表格和热力图，未重跑 raw→summary 全链；实验数据、处理脚本和正式图件未变。退化以同一模型在目标站的站内汇总 F1 为基准，表示相对当地训练基准的差距，不是理论上限，也不意味着已消除目标站差异。详细范围与未验证项见 `verification/verification-report.md` 本轮记录。

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

1. 作者审阅 3.2 收尾稿；本轮数字与版面已核查，当前 PDF、预览和验证范围均已记录。
2. 审阅已有 3.3 探索产物及未解决验证项，不从头覆盖重建；正式正文和候选图仍待后续。先区分清单一致性、独立复算及作者是否采纳。
3. 完成引言、1.3、2.1、结论与摘要，投稿空间泛化篇。

## 历史 3.3 探索协议（冻结 DR，不作当前差值分析指令）

plan/sec33-exploration-protocol.md：3.3 第一轮探索协议，固定文档化分组规则（ED与AREA_MN线性插值分位点、低中高组、缺失组、CM闭合）、精度与退化计算（DR、站内F1/跨站F1五次均值）、描述性比较、边界距离指标（带内错误率、像元占比、对总体贡献）。不撰写正式正文、不编译、不改3.2。所有新结果标为 derived / exploratory。

## 系统整理入口（2026-09-29）

禁止删除任何文件，只归档；具体规则见 `AGENTS.md`。唯一确认的协议单元测试已集中至 `scripts/test/`，两种运行入口各 7 项通过。停用迁移地图与五张历史预览位于 `archive/2026-09-29-system整理/`；旧路径与 SHA-256 见归档清单，当前预览入口不变。当前脚本分层与测试命令见 `README.md`，本轮实际核验及限制见 `verification/system-audit-2026-09-29.md`。本轮未暂存、提交或 push；禁止为了满足“工作区干净”删除未跟踪成果。

## B 站身份问题：接手必读（2026-09-30）

完整来龙去脉见 [B 站身份问题追溯](verification/iw2-identity-provenance.md)。B 站生产时曾沿用 A 站身份，已有数据及运行迁移；U-TAE 五折共 400 行冗余 site 字段修复经备份对比确认仅此字段变化，15 条 B 来源跨站 CM 关联一致。3D U-Net 与 U-TAE 的两条旧参考指纹已精确复算定位：旧 dataset_id 和 UID 前缀生成的指纹未随身份迁移更新，实际标签及空间契约一致。U-TAE B 站站内 TIFF 存在并有 B 站定位，只缺完整 CRS GeoKey，不是标签缺失，也不是指纹差异的原因。上述限定范围 Verified；旧契约完整字节恢复仍 Partially verified。不得要求为此重跑景观指数或边界清单，不改历史报告布尔值。

## Git 追溯

作者要求整个写作系统的有效改动入库，任务收尾时核对暂存区、工作区和未跟踪文件均为空。参考论文 PDF、编译辅助文件及指定名称的页面预览按既有规则排除；已跟踪的 `output/sec32_p-{3,4,5}.png` 继续更新并入库，`output/preview-manifest.json` 同步记录其来源。正式图件、文献库和全部计划继续跟踪。范围与预览重建命令见 `README.md`。禁止用删除文件或新增忽略规则制造干净状态；不 push。

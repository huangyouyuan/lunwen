# 论文交接

更新：2026-10-12。`1d0bc9f`已保存页面预览归档与交接更新；本次在其基础上补齐两组修改前备份的完整归档、Git保存及可传递PDF。论文内容仍以`e25df0c`（图表字体、通栏表格及图2/图3样式）为基线，1.1首段润色已在`3841b8f`中。接手先检查`git status --short`和`git log -5 --oneline`，以实际文件与Git状态为准，不把本文件或旧提示词当作任务已经完成的证据。规则见[AGENTS.md](AGENTS.md)，总体计划见[plan/outline.md](plan/outline.md)，当前缺项见[进度](plan/progress.md)；2026-10-11整理过程见[历史版本说明](plan/version-notes-2026-10-11.md)。

## 当前主线与优先级

四站空间背景 → 本站错误基准 → 跨站F1差距 → 错分变化与空间条件的对应关系。3.3解释3.2的具体模型、来源和方向差异；现有数据支持描述性对应，尚未证明因果机制。

| 章节 | 职责 | 当前状态 |
|---|---|---|
| 1.1研究区概况 | 四站范围、经纬度和分类图 | 润色及2023年CDL追溯已提交；仅使用经纬度与分类图，不补写未经核实的行政区；图1在1.1末尾 |
| 1.3研究区空间特征 | 四站参考组成、完整参考斑块及整站景观背景 | 地物组成、景观格局两小节；图2及一张双栏表1。AREA/SHAPE面积加权、ENN斑块等权；当前PDF为8页，表1在第4页 |
| 3.1本站分类性能 | F1及必要的精确率、召回率和六向错分基准 | 主体和正式图已有，补充底表已核验，正文待最小补充 |
| 3.2跨站分类性能与差距 | 绝对F1、原尺度ΔF1、模型与来源差异 | 已有正文和表图，本次不变 |
| 3.3空间解释 | 差距对应什么错误、发生在哪里、怎样随模型来源变化 | 已有探索和最小衔接表，正文未写；先围绕3.2选择具体差异 |

基础材料的整理与核查已完成，见[1.3与3.1基础证据](results/summary/sec13_sec31_foundations/README.md)及其[段落—证据提纲](results/summary/sec13_sec31_foundations/paragraph_evidence_outline.md)，不再把它列为尚未开始的任务。3.1保持现有主体，3.3正文仍未写；2.1模型原理、引言、摘要与结论也未完成。后续优先从既有12个独立本站基准组织3.1的必要补充，再从3.2选择3.3的具体比较对象，不自动启动聚类、共同五档或联合建模。

## 1.3与图表的现行决定

- 1.3.1沿用2023年整站三类面积占比，正文、图例统一写“玉米、大豆、其它地类”。表1只列玉米、大豆，共8组；其它地类仍计入组成图及整站ED。
- 1.3.2按“单像元斑块数量多、面积少 → 面积加权理由 → 四站共性 → 站间差别”连续写三段。参考斑块来自30 m标签的8邻域同类连通区域，不等同于农业田块；保留单像元及外框接触斑块，不据此预判分类难度。
- 表1斑块级包含AREA、SHAPE、ENN及斑块数。AREA/SHAPE用参考像元数为权重的加权中位数，ENN每个完整斑块计一次、采用等权中位数；三项均显示“中位数（全体最小值～最大值）”，不能将范围写成多数斑块的区间。现行八组ENN中位数均为67.08 m，旧面积加权版的60 m不是当前表值。
- 类别级PD、AI及景观级ED均用`scope=full`的结果。PD分母为整站面积，ED覆盖三类景观、同站合并单元格；不混入128×128图块尺度。PD与斑块数在等面积站点中成比例，不作为两条独立证据反复强调。
- 活动表体为[tables/sec13_spatial_metrics_enn_equal_rows.tex](tables/sec13_spatial_metrics_enn_equal_rows.tex)，来源及独立复核见[ENN等权核查](verification/sec13-enn-patch-equal-2026-10-12.md)。旧双表、双权重分布和ENN面积加权表均保留为历史成果；PD/AI/ED恢复到正文源于作者决定，不代表旧数据失效。
- 表格占满所选一栏或两栏，使用三线表并合理分配行列间距；表1铺满双栏17.4 cm，PD/ED单位与指标同行。图表文字、图题、表题、图例和注均为小五9 pt宋体与Times New Roman。图2和图3(a,b)有效图框均为7.6×5.7 cm、条形厚3.705 mm，间距和网格共用`figstyle.py`参数。
- 图1在1.1末尾；图2在1.3.1与1.3.2之间；表1在1.3.2与第2节之间。当前页码见下方核查记录，后续改稿不可沿用旧页码推断排版已通过。

## 活动证据入口

| 用途 | 入口 |
|---|---|
| 正式F1与ΔF1 | `results/summary/f1_raw_scale/`；原矩阵在 `results/raw/` |
| 1.3与3.1基础阅读表及本次核查 | [基础证据目录](results/summary/sec13_sec31_foundations/README.md)；输入、脚本与输出哈希见其中`manifest.json` |
| 当前表1统计与生成入口 | `scripts/generate_sec13_spatial_tables.py --check`；独立核对为`scripts/test/check_sec13_spatial_enn.py`，不带`--report`时不写报告 |
| 当前组成图生成入口 | `scripts/plot_sec13_composition.py`；历史组合生成器保留，不能为重绘图2而连带写入旧表 |
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

2026-10-11恢复阶段仅恢复与只读核对，没有生成新科研结果或编译；该阶段原22份快照及12份文档快照保留。初次核查与首次纠偏仍是各自当日记录，成果恢复以[二次核查](verification/second-pass-reuse-2026-10-11.md)为准；距离生成、FRAGSTATS工程和B站身份限制不升级。

2026-10-12页面预览整理已完成：原`output`根目录58张图片中，最新2张放入`output/previews/2026-10-12-figure23-bars/`，其余56张按任务放入`output/archive/2026-10-12/`；配套文本与旧清单一并保存，共移动60个文件。原125个output文件全部保留，14份引用文档原字节快照、移动前后SHA-256及13份引用路径更新均已核对；根目录不再散放图片，递归图片总数仍为68。入口见[预览索引](output/README.md)、[归档索引](output/archive/2026-10-12/README.md)和[迁移核查](verification/output-preview-archive-2026-10-12.json)。旧清单和文档快照中的旧路径按迁移映射解析，不改写历史原件。

## 验证状态与尚未验证事项

| 状态 | 范围与证据 |
|---|---|
| Verified | 既有数据核查复核149234条作物斑块记录、统计权重、单位、极值及`scope=full`；见[ENN核查](verification/sec13-enn-patch-equal-2026-10-12.md)。本次归档与交接没有重新计算这些指标 |
| Verified | 最近一次编译为8页，图2/图3样式核查查看第3、5页；当前PDF哈希与[最新记录](verification/figure23-bars-2026-10-12.json)及[预览清单](output/preview-manifest.json)一致。5图2表字体的既有检查见[字体核查](verification/figure-table-fonts-2026-10-12.md)，随后仅图2/图3样式变化，以后者记录的哈希为准 |
| Verified | 本次归档核对文件字节、哈希和入口引用，357份正文、图件、脚本及汇总文件保持不变；没有重绘或编译。归档报告中的暂存区未变和未提交描述指归档核验时点，随后按作者授权提交；后续交接文字更新不回写历史核查结论 |
| Partially verified | ENN复用既有空间距离，未重算距离或恢复全部FRAGSTATS工程参数；C站玉米ENN最大值涉及外框斑块`ida_2023, PID=69765`。距离限于窗口内最近同类斑块边界像元中心，不是田块净空距离。B站限制见[身份追溯](verification/iw2-identity-provenance.md) |
| Not verified | 全文最终分页、留白、文献格式及尚未完成章节的科学论述；既有字体替代、xeCJK、caption等警告未作为本次任务处理。图表字体通过不等于论文已定稿 |

最新预览只包含最近查看的第3、5页，不是整篇逐页预览。此前7页稿件、表1位于第3页的记录均为历史状态；当前表1在第4页。本地`main.pdf`仍按既有规则忽略，但本次已将同字节的[8页PDF快照](output/previews/2026-10-12-figure23-bars/manuscript.pdf)纳入Git，换机可直接查看；PDF哈希及来源见[预览清单](output/preview-manifest.json)，后续改稿需重新核对版本。

## 工作区交接

本次提交补齐备份归档、可传递PDF、引用修正和交接文档；正文、正式图件、表体、数据及生产脚本沿用`e25df0c`，未重绘、编译或重算科研结果，不推送。归档目录采用保留字节的Git属性，避免换行转换改变历史快照SHA-256；未新增忽略规则。

上一提交遗漏的两组本地备份已完整迁至[源码备份归档](output/archive/2026-10-12/source-backups/)，共32个文件，含2份原先被忽略的PDF、2份日志、源码、图件、暂存补丁和原始清单，全部纳入Git。原清单内容不改写，旧路径按[收尾映射与核查](verification/output-handoff-closeout-2026-10-12.json)解析。迁移前后和Git保存内容均核对SHA-256，接手无需另外复制这两组备份；旧源码仅供审阅，不是活动运行入口。此前报告的“保留原位、未跟踪”只表示`1d0bc9f`当时状态。

接手顺序：核查Git和实际文件 → 读规则、写作/格式规范与当前正文 → 读[进度](plan/progress.md)及对应底表 → 在作者新任务范围内继续。若续写3.1，先读`plan/experiment-protocol.md`、`sections/03_methods.tex`、`plan/results-map.md`及正式summary；若核对1.3表，优先运行只读检查，不运行历史生产脚本。保存正文默认不编译，只有作者要求或规则允许的验证任务才执行`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`。每次编译后更新预览目录与清单，保留历史文件。

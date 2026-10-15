# 论文写作与交接流程

本文件说明从研究证据到正文、图表、编译稿和交接的工作顺序，并集中规定文档职责。2026-10-15按作者决定统一整稿输出为`output/main.pdf`；原流程与入口说明保留在[修改前版本](../archive/manuscript/2026-10-15/default-output/before/plan/writing-workflow.md)。

## 文档职责与更新位置

| 文档或目录 | 回答的问题 | 何时更新 |
|---|---|---|
| [AGENTS.md](../AGENTS.md) | 哪些项目规则必须遵守，信息冲突时以何处为准 | 作者改变规则或文件约定时；不放每轮任务日志 |
| [README.md](../README.md) | 从哪里进入项目、阅读当前稿和找到材料 | 入口或目录职责变化时；不复制完整交接 |
| [HANDOVER.md](../HANDOVER.md) | 接手需要知道哪些决策、历史背景和未决限制 | 影响后续工作的决定发生时；历史段落保留原时点 |
| [progress.md](progress.md) | 当前哪些正文已完成，下一步做什么 | 写作或核验状态变化时；不把有数据等同于已写完 |
| [writing-workflow.md](writing-workflow.md) | 按什么顺序写、查、编译和交付，各文档各管什么 | 工作流程或分工改变时；文件组织说明集中在这里 |
| [paper-context.md](paper-context.md) | 本文为什么研究这个问题、解释到哪里为止 | 核心问题或解释范围改变时 |
| [outline.md](outline.md) | 各章节承担什么任务、怎样推进 | 章节结构或写作顺序改变时 |
| [experiment-protocol.md](experiment-protocol.md) | 实验身份、分析单元、指标和分母怎样定义 | 有证据支持的方法口径改变时 |
| [results-map.md](results-map.md) | 某个章节判断该查哪份底表、图表和脚本 | 证据路径或正文图表选择变化时 |
| [claims.md](claims.md) | 哪些论点有证据，例外和表述边界是什么 | 核验支持范围发生变化时；不替代正式数值表 |
| [style-guide.md](style-guide.md)、[terminology.md](terminology.md) | 文字怎样写，术语怎样统一 | 写作模式或术语约定改变时 |
| [format-spec.md](format-spec.md) | 页面、字体、图表和公式按什么规范排版 | 排版标准改变时；目录流程引用本文件 |
| [chapter-blueprints/](chapter-blueprints/) | 复杂段落怎样组织论点和证据 | 开写或重组复杂段落时；未建提纲不代表已完成 |
| [review/](review/) | 结构、语言和证据覆盖查了哪些项目 | 实际审查后填写；模板与未检查项不是通过记录 |
| [tasks/](tasks/) | 作者指定的重大任务怎样规划，各时间节点作出什么决定、完成什么 | 仅在作者明确命令建立重大任务规划时新建；执行中按实际节点更新同一份文档，小修不新建 |
| [papers/](papers/)、[evidence/](../evidence/) | 文献具体支持哪条判断，原文证据在哪里 | 阅读并确认文献内容后；`evidence-map.md`负责论点映射 |
| [bibliography/](../bibliography/) | 引文元数据和全文在哪里 | 新增或更正文献时；`references.bib`是引用元数据权威，风格报告只是写作参考 |
| [results/summary/README.md](../results/summary/README.md) | 正式科学结果从哪里读 | 科学结果入口改变时；数值以实际summary为准 |
| [results/summary/reuse-status.md](../results/summary/reuse-status.md) | 已有成果属于当前证据、可复用探索还是待审阅候选 | 成果用途改变时；不用删除或搬走数据表示“不采用” |
| [results/summary/sec33_evidence_overview.md](../results/summary/sec33_evidence_overview.md) | 3.3已有证据怎样连接到3.2 | 证据综合和取舍改变时；统计口径仍查原底表与协议 |
| 各成果目录的`README.md`、报告和manifest | 这份结果怎样产生、输入输出是什么、核验到哪一步 | 对应产物实际变化时；不改历史manifest冒充重新生成 |
| [verification/](../verification/) | 本次实际验证了什么，证据和限制是什么 | 做完相应检查后；记录日期与范围，页面图片放`layout/<任务>/` |
| [output/README.md](../output/README.md) | 当前PDF与编译文件在哪 | 编译入口改变时；只保留简短查看说明 |
| [archive/manuscript/README.md](../archive/manuscript/README.md) | 旧稿、备份和迁移记录在哪 | 历史文件迁入时；归档文件不作为活动运行入口 |

同一信息只在负责它的文档维护完整内容，其他入口以链接说明。小范围正文修改通常只更新正文和对应进度；只有影响接手判断时才更新交接，不机械地把每次编译写进所有文档。发现旧记录与当前不一致时先看日期、当前源码和权威底表，不通过删减历史消除差异。

## 重大任务计划与节点记录

`plan/tasks/`集中保存由作者直接命令建立的重大任务规划，以及该任务各时间节点的检查和阶段说明。只有作者明确要求为重大任务制定规划或建立任务文档时才新建；AI不得因任务较复杂、耗时较长、发生编译或日期变化而自动创建。日常润色、图表微调、局部排版和常规编译等小修不建立任务文档，按需更新负责该事项的现有文件即可。

任务文档记录触发指令及日期、目标与范围、已有依据、执行安排和重要时间节点。执行中的决定、已完成事项、实际核验状态与未决问题按日期续记在同一份文档中，不为每个小步骤另开计划。计划与完成状态分别表述，历史节点保留当时判断；后续进展另记日期，不回写旧节点冒充当时已完成。必要核验照常进行，详细证据链接到`verification/`，不重复抄录整套检查日志。

新建文档采用`日期-任务名.md`，已有文件可保留名称。[2026-10-11主线整理与下一阶段起点](tasks/version-notes-2026-10-11.md)属于此类重大任务的节点说明，归入`plan/tasks/`，保留其原时间点和历史状态。

## 从源码到文件的关系

`results/raw → results/processed → results/summary`保存科学追溯链；绘图和表格脚本读取已验证结果，生成`figures/`、`tables/`中的正式展示。`main.tex`汇入`sections/*.tex`，并引用图表及`bibliography/references.bib`。只有授权编译后，才由这些源码生成`output/main.pdf`。PDF和页面图片是展示产物，不是数字或正文的编辑源。

| 文件位置 | 职责 |
|---|---|
| 根目录`main.tex`、`sections/` | 主稿入口和章节源码 |
| `.latexmkrc`、`.vscode/settings.json` | 命令行与编辑器共用的默认输出约定；自动编译和自动清理关闭 |
| `output/main.pdf` | 唯一当前整稿，不再复制到根目录或`output/previews/` |
| `output/main.synctex.gz` | 编译时生成的源码与PDF跳转信息 |
| `output/build/main/` | 主稿辅助文件、LaTeX/BibTeX日志和本次控制台输出 |
| `output/build/<图件任务>/` | 独立图件编译工作区；正式可引用图件仍在`figures/` |
| `verification/layout/<任务>/` | 需要核验的页面图片；不为无内容变化的编译重复生成整套图片 |
| `archive/manuscript/<日期>/<任务>/` | 已替代稿、试排与必要修改前版本；有用途说明、迁移路径和SHA-256 |
| `word/`、`legacy/manuscript/` | Word交付位置与旧稿/模板来源；本次没有生成Word，也不覆盖旧Word |

当前稿文件名固定，不再用复制多份当前PDF的方法交付。历史`output/build/`任务保留各自来源，本次不为整理目录移动其编译文件或重跑绘图。

## 接手与限定任务

先读`AGENTS.md`、`HANDOVER.md`和`plan/progress.md`，检查Git与实际正文。继续使用完整科研工作区 `D:/AI/lunwen/`，保留现有历史。检查已有修改，正文只改作者指定范围；不把某处缺少大表或数组当作实验结果尚不存在。

写作主线保持：1.3四站背景 → 3.1本站基准 → 3.2跨站绝对F1与相对目标本站的差距 → 3.3具体错误变化及其空间条件。没有独立Discussion或补充材料。当前1.3与3.1/3.2主体已存在，3.3、2.1模型原理、引言、结论及摘要仍未完成，以实际源码为准。

## 从证据到段落

1. 用一两句话确定本段要回答的读者问题，查`plan/results-map.md`定位已有底表。先检查能否复用，不以缺少亮点为由重启指标探索、重训或推理。
2. 修改结果前读实验协议、对应方法和实际summary；按模型、来源、目标、作物、预测身份连接。不从正文舍入值反算。缺少大表或数组时，先按对应成果README、字典和输入清单定位原件；依赖未取得时明确限制，不能以占位数据补齐或声称全面复验。
3. 每个关键判断列出“对象/分母/相减方向/支持数据/例外/可写到什么程度”。写在`plan/`或核查记录，不写入论文。引言和解释段的文献判断先补`evidence/evidence-map.md`；复杂段落需要`plan/chapter-blueprints/`中的提纲。文献标题和已有BibTeX条目不等于证据。
4. 按`plan/style-guide.md`用连续段落写，先共性后差异，选少量能支持判断的数字。图表分工清晰，不逐行复述。1.3描述空间背景，不能提前安排分类难度或因果结论。
5. 回读该节与上下节：3.3必须接住3.2的具体比较；固定目标的空间格局不能单独解释来源差异。边界错误较多只作定位，不能代替模型优势、路径反例与实际错误贡献的判断。

## 当前可直接复用的三组空间证据

以下结果目录及其逐次表、完整参考特征和数组保留原位。使用结论前检查对应README、报告、底表和计数是否齐全，不能只取结论；当前取舍见`results/summary/reuse-status.md`，不因尚未写入正文而重做统计。

| 目的 | 本地入口 | 使用边界 |
|---|---|---|
| 全路径空间条件与错误定位 | `results/summary/spatial_error_conditions/` | 同时看错误率与实际贡献，保留负值、无支持及反例 |
| C/D大豆条件性差异 | `results/summary/spatial_findings_refinement/` | 共同来源和共同支持；三套权重不混合，不称独立形状效应 |
| 本站模型优势及跨站保持 | `results/summary/model_advantage_spatial_conditions/` | 优势为ConvGRU漏分率减对照模型；漏分排序不能替代完整F1 |

本站五折测试计数先汇总；跨站五次分别算后求均值和样本标准差。F1显示百分数、差值显示百分点，均两位小数；主表只显示平均F1。真实作物分组只解释漏分和去向，完整F1还需要FP。三套问题分别表述：本站本来难不难、跨站绝对精度高不高、相对本站额外变差多少。

## 保存、验证与交付

正常修改保存后不自动编译。作者要求编译、验证或最终检查时，按现有入口生成受影响表图，再编译并实际查看受影响页面。不重算无关科学统计，不以“图看起来正常”替代数值核对。测试放`scripts/test/`，生产脚本放`scripts/`。

从仓库根目录执行`latexmk -xelatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex`。`.latexmkrc`默认将PDF写到`output/`、辅助文件写到`output/build/main/`；VS Code的Build与PDF查看使用同样位置。无需给每次整稿编译另设任务输出目录，也不再手工同步根目录PDF。直接调用`xelatex main.tex`会绕过这套默认配置，不作为主稿编译入口。

替换已有稿件前，先核对是否已有同字节历史版本；有则引用其路径和哈希，没有则只保存一次必要版本。编译后检查退出码、日志、引用及受影响页面；交付时只链接`output/main.pdf`，核查记录明确对应文件哈希。历史预览清单留在归档中，不继续维护第二份“当前稿”清单。禁止通过自动清理、删除或扩大忽略规则制造整洁状态。

核查只用Verified / Partially verified / Not verified，并注明本次范围和时点；历史核查不升级为全面复验。交付说明具体改了什么、证据在哪里、测了什么、还有什么限制。原文件和历史版本保留，归档记录原路径、新路径、原因与SHA-256。未经作者指令不提交或推送。

2026-10-15取消的仓库缩小流程仅作历史保存，见[归档说明](../archive/2026-10-15-cancel-remote-plan/README.md)；不再维护额外上传副本或调用其准备、检查命令。

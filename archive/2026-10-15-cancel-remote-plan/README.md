# 取消仓库缩小计划后的归档与用途核查

2026-10-15；起点HEAD `4e2562c`，开始时原工作区干净。作者已放弃缩小计划，并要求将额外副本归档。继续在 `D:/AI/lunwen/` 工作；本次没有新建工作仓库、删文件、改写历史、提交或推送。

## 实际归档范围

| 原位置 | 归档位置 | 原因 |
|---|---|---|
| `D:/AI/lunwen-remote-2026-10-14/` | `D:/AI/lunwen_archive/2026-10-15-cancel-remote-plan/lunwen-remote-2026-10-14/` | 取消的上传副本，含.git整体移动，不再同步或用作推送入口 |
| `plan/submission-policy.json`、`remote-copy-manifest.json`、`remote-local-files.json`、`remote-preparation-check.md`、`remote-storage.md` | 本目录 `history/plan/`，同名保存 | 取消计划专用规则、范围清单及历史核查，共5份 |
| `plan/tasks/2026-10-14-source-only-handoff.md` | 本目录 `history/plan/tasks/`，同名保存 | 该任务已经取消 |
| `scripts/manage_remote_repository.py`、`scripts/test/test_remote_repository_scope.py` | 本目录 `history/scripts/`及其`test/`，原名加`.source` | 准备脚本与配套测试退出活动入口，原字节仅供审阅 |
| `.githooks/pre-commit`、`.githooks/pre-push` | 本目录 `history/.githooks/`，原名加`.source` | 原仓库未配置启用这套钩子；退出活动入口，副本内的原配置随副本保存 |

原/新绝对路径、原因、每份文件大小和SHA-256见[清单](manifest.json)。外部副本共1,242份文件，包含.git为79,081,775字节；这个数值只描述已归档副本，不表示远端体积或新的限制。其历史HEAD为`2fd7e58`，原科研仓库HEAD仍为`4e2562c`。

`snapshots/`只保存本轮改动的7份活动文件修改前原件。AGENTS.md仅撤回末尾“远端保存与交接（作者2026-10-14决定）”一节，完整字节恢复为该计划前版本，SHA-256为`ca2e429d621c087603fbcb4cdacc5a8fdbb6c45d79849dd16d7c5113f11ab8bd`；其它科研、编辑、归档与验证准则未改。.gitignore恢复同一时点原件，SHA-256为`c5f34659abe878ab15cd508ea381f5945edeac22f89f90d168fe982fb1c0d63e`。完整交接、README、进度、写作流程及成果用途索引只同步取消决定和阅读优先级。

历史文件内部的相对路径、命令、100 MB及2 MB门槛均为原计划记录，不是现行要求。查原路径按清单定位；不要从本目录运行历史准备脚本、测试或钩子。旧记录中的外部副本原路径已失效，由本清单映射到新位置。

本轮未暂存，Git状态中的10项`D`对应上述文件已迁出的原路径，新位置显示在未跟踪的本归档目录下；每份原件均在新位置保存并核对SHA-256，没有删除其内容。

## 深入核查后的保留与重点

| 文件或成果 | 本轮决定 | 用途与依据 |
|---|---|---|
| `AGENTS.md`、完整`HANDOVER.md`、`plan/writing-workflow.md` | 保留活动 | 项目准则、完整交接与证据到段落的流程仍必需；缩小计划取消不影响写作规则 |
| `sec13_landscape_display/`、`sec13_sec31_foundations/`、`area_shape_joint_bubbles_v3/` | 原位保留，1.3现行依据 | 正文实际引用现行表体和联合图；生成器导入`plot_area_shape_joint_bubbles.py`并读取v3份额，旧气泡成果并非无依赖文件 |
| `model_advantage_spatial_conditions/` | 原位保留，3.1/3.3优先阅读 | 16个本站比较、48条跨站模型对照已完成。写作重点为本站优势的空间来源，以及固定D换B/C来源后的变化 |
| `spatial_findings_refinement/`、`spatial_error_conditions/` | 原位保留，针对性补充 | 后续模型比较直接复用早先权重、参考特征与计数；用于C/D大豆、共同支持和反例，不能只留短报告而移走底表 |
| `f1_raw_scale/`、定向混淆收尾、完整矩阵 | 原位保留，持续核对 | 真实作物漏分不能解释完整F1；FP、其它地类、五次结果及相减方向仍须保留 |
| 完整参考斑块、192份预测计数、七带和按图块存储的联合计数 | 原位保留 | 是多个活动分析与检查脚本的输入；文件大或采用128×128存储分区不构成归档理由 |
| K2/K4、共同五档候选、ENN及其它背景指标 | 原位保留，暂不扩展 | 保存定义、支持、反例与复用价值；不再重新聚类或遍历指标。共同五档尚未冻结，也没有等级错误结果 |
| 旧表1、PD、AREA/SHAPE中位数与极值、旧图表及其生成器 | 原位保留，历史展示/核查 | 已退出现行展示，但仍被说明、核查或复现链引用；不能仅凭图号或日期移动 |
| 其余6份`plan/tasks/`记录、历史核查、旧Word及既有预览 | 原位保留，按用途阅读 | 任务记录仍被对应成果或核查引用；完成的任务不自动重启，旧Word仍是写法和格式参考 |
| 既有归档、原Git、旧refs备份及工作树 | 原位保留 | 保持恢复链和并行工作完整；本轮不再扩大归档范围 |

1.3已经提供空间背景；当前应把已有本站模型优势写入3.1，再以固定D换来源组织3.3，用C/D大豆、C玉米或B↔D作为有限补充。K2/K4、五档、ENN和整站指标暂不成为新一轮任务。详细科学边界仍以[交接](../../HANDOVER.md)和[用途索引](../../results/summary/reuse-status.md)为准，本次没有复算或新增发现。

## 本轮验证范围

**Verified（2026-10-15，文件与入口范围）**：归档副本1,242份文件、10份迁移文件和7份修改前快照全部通过原字节核对；其余1,563份已跟踪普通文件保持原字节，覆盖正文、数值数据、图件、旧Word及CC的三处证据路由。6份修改或新增说明中的136个本地Markdown链接均可定位；活动入口不再调用取消的脚本或规则。AGENTS.md和.gitignore与计划前原件一致，Git HEAD、refs、工作树登记、暂存内容和.gitattributes保持原状。

逐项结果记录于`manifest.json`的`verification`字段。本轮不执行历史远端测试，不重跑科学统计或编译；历史科研核查保留原范围，不能升级为本轮全面复验。未提交、未推送。

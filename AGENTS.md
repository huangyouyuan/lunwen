# AGENTS.md — 项目最高级规则

本文件是 AI 辅助科研写作的最高级项目规则。所有 AI 操作必须遵守。

## Source of Truth 分层

| 优先级 | 信息类型 | 权威来源 |
|--------|----------|----------|
| 1 | 科学数字（mIoU, UA, PA, F1, Kappa, OA 等） | `results/summary/` |
| 2 | 论文逻辑与结构 | `plan/` |
| 3 | 写作模式 | `legacy/manuscript/` + `plan/style-guide.md` |
| 4 | 最终格式规范 | `legacy/manuscript/` + `plan/format-spec.md` |
| 5 | 文献元数据 | `bibliography/references.bib` |
| 6 | 当前正文 | `sections/*.tex` |

正文数字与 `results/summary/` 冲突时，以已验证的 summary 为准。

## Scientific Integrity

- **禁止捏造实验结果。**
- **禁止捏造参考文献。**
- **禁止将 placeholder 数据呈现为真实数据。**
- **禁止在缺乏证据支撑时强化论点。**
- 所有正文数字必须可追溯：summary → processed → raw。

## Editing 规则

- 默认只修改用户指定的范围。
- 大范围改动前必须读取必要上下文文件。
- 不无目的加载整个仓库。
- 不因语言润色改变科学含义。
- **禁止删除任何文件（包括未跟踪文件、测试产物、历史预览和过时脚本）。过时内容只能归档，不得以清理、重构或节省空间为由删除。**
- 归档前必须核查用途和引用；保留原始内容，记录原路径、归档路径、原因和 SHA-256，并同步修正活动入口。无法确认是否过时的文件原位保留，不能凭文件名或时间判定。
- 不得用覆盖同名文件的方式归档；移动前确认目标不存在。禁止执行删除型清理命令（如 `git clean`、`latexmk -c/-C`）或会删除文件的测试清理流程。
- 旧版本不再参与当前流程时，只改为历史入口；不得让归档脚本自动写入当前正式结果目录。
- 测试脚本统一放在 `scripts/test/`，生产数据处理与绘图脚本保留在 `scripts/`。移动测试后必须修正导入、仓库根路径和调用说明，并实际运行适用测试。
- 任何 AI 接手时先核查 Git 状态与现有成果，不覆盖未提交工作，不把旧交接说明当作当前完成状态；验证清单中的历史状态与本次核验必须区分。
- 禁止删除或覆盖 `legacy/manuscript/` 中的旧 Word。

## Writing 规则

- 论文定位为普通中文核心期刊短文，写作通俗易懂、科学准确。
- 论文以中文为主；模型名称、数据产品、通用指标缩写（F1、OA）除外。**公式角标也用中文**（$F1_{\text{玉米}}$、$F1_{\text{站内}}$），不用 corn / within / cross。
- 正文不用 fold、checkpoint、OOF 等工程词，写"折""每折一个模型""汇总精度"。
- 遵循旧 Word 的写作模式（见 `plan/style-guide.md`）。
- 遵循 `plan/terminology.md` 的术语表。
- 正文优先连续论述，不使用列表代替学术段落。
- 避免机械 AI 过渡词（"首先……其次……此外……最后"）和翻译腔（"统计学上的显著差异"）。
- 不把项目管理语言（TODO、待确认、用户要求等）写入正文。

## Body Contamination Firewall

以下内容**绝不能**出现在 `sections/*.tex` 正文中：

- TODO / FIXME / HACK
- 用户要求、AI 提示词
- "这里以后补"、"用户需要确认"
- "写得自然"、"避免AI味"
- "这一段是模板"
- 任何项目管理信息

这些只能存在于 `plan/`、blueprint、review、comments。

## Results 章节规则

修改 Results 前，必须读取：
1. `plan/experiment-protocol.md`
2. 对应的 Methods 章节
3. `plan/results-map.md`
4. `results/summary/` 中的实际数据

## Discussion 章节规则

修改 Discussion 前，必须读取：
1. 对应的 Results 章节
2. `plan/claims.md`
3. `evidence/evidence-map.md`
4. 必要文献证据

## Literature-Driven Writing

- 引言和 Discussion 的文献论点必须建立 evidence mapping。
- 复杂段落需要 chapter blueprint（`plan/chapter-blueprints/`）。
- 一条引用必须能支持一个具体 claim；论文标题本身不是证据。
- 禁止文献罗列（A 研究了……B 研究了……C 又研究了……）。

## 反文献罗列规则

文献段落按以下维度组织：
- 方法路线 / 共同问题 / 共性局限 / 技术演进 / 与本文的关系

每个文献段落至少完成两个任务。

## LaTeX 编译规则

- 正常修改正文时：修改 → 保存 → **不自动编译**。
- 仅在以下情况执行 Build：
  - 用户明确要求编译
  - 用户要求验证
  - 修改了复杂 LaTeX 结构且任务要求验证
  - 最终检查

## 数据真实性

- 必须明确区分：real / derived / placeholder / mock。
- 禁止使用 mock 数据进入论文正文。
- placeholder 必须标记：`PLACEHOLDER — NOT REAL RESULT`。

## Verification

- 不能以"看起来正常"作为完成依据。
- 必须实际验证（编译、数据核对、citation key 检查等）。
- 验证结果只允许：Verified / Partially verified / Not verified。

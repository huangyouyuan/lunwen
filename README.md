# 时空深度学习模型在玉米—大豆分类中的空间泛化能力分析

科研论文工程化写作仓库。

本仓库仅维护美国四站点空间泛化论文，主线为“站内基准 → 美国站间退化 → 空间解释”。

## 目录结构

```
├── AGENTS.md              # AI 辅助写作最高级规则
├── main.tex               # LaTeX 主文件（XeLaTeX + ctex）
├── sections/              # 论文各章节 .tex 文件
├── plan/                  # 当前论文规划（大纲、术语、实验与探索协议）
├── legacy/manuscript/     # 旧 Word 论文（仅参考写作风格和格式，不作为内容来源）
├── evidence/              # 文献证据映射
├── bibliography/          # BibTeX 文献数据库
├── results/               # 实验数据（raw → processed → summary）
├── tables/                # 表格定义与生成
├── figures/               # 图表及数据映射
├── scripts/               # 当前数据处理与图表生成脚本
│   └── test/              # 测试脚本（不向正式结果目录写入测试数据）
├── archive/               # 已停用文件与脚本，保留原内容和迁移清单
├── verification/          # 验证报告
├── output/                # 编译输出
└── word/                  # 最终 Word 投稿稿件
```

## 工作流

明确的大任务先在 `plan/tasks/` 写行动计划，再拆分步骤执行；小修改无需任务计划。计划按 `YYYY-MM-DD-主题.md` 命名，记录任务范围、执行步骤和核验结果，便于审计。

```
论文问题与实验事实 → plan → evidence / results → tables/figures
                                          ↓
                                    sections/*.tex
                                          ↓
                                    手动 LaTeX Build
                                          ↓
                                      PDF 预览
                                          ↓
                                      内容冻结
                                          ↓
                                     Word 输出
```

## LaTeX 编译

- 编译器：XeLaTeX（通过 latexmk）
- 编译模式：**手动**（保存 ≠ 编译）
- VS Code 快捷键：`Ctrl+Alt+B`（LaTeX Workshop Build）
- PDF 预览：VS Code 内置 Tab

## 文献管理

Zotero → Better BibTeX → Keep Updated → `bibliography/references.bib`

## Git 追溯范围

正文、论文计划、交接与验证记录、文献库、数据处理脚本、结果汇总、表格和正式图件均纳入版本控制。参考论文 PDF 只保留在本地，文献元数据与阅读记录继续跟踪；已移出索引的 PDF 仍可从既有提交中追溯。

`main.pdf`、LaTeX 辅助文件和 `.gitignore` 已指定的页面预览不入库；已跟踪的 `output/sec32_p-{2,3,4,5}.png` 继续随编译更新，不移出索引。`output/preview-manifest.json` 记录当前 PDF、源码和预览的 SHA-256、生成时间、页码及构建时版本状态。未新增忽略规则，也不整体忽略 `output/`。

### 当前 3.2 PDF 与预览（2026-10-01—02）

- [当前 PDF](main.pdf)：本轮编译生成，6 页；第 4 页为图 3 与 3.2 正文，第 5 页为完整跨站 F1 表与图 4。
- [第 2 页方法](output/sec32_p-2.png)、[第 3 页](output/sec32_p-3.png)、[第 4 页正文](output/sec32_p-4.png)、[第 5 页表与图](output/sec32_p-5.png)：均从该 PDF 以 150 dpi 导出。
- `output/table_page_preview.png`、`output/figure4_page_preview.png` 同步为当前第 5 页的副本；`results_layout-*`、`results_spacing-*` 已移至 `archive/2026-09-29-system整理/output/`，仅作历史预览，不作为当前版面依据。
- 编译：`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`。渲染：`pdftoppm -png -r 150 -f 2 -l 5 main.pdf output/sec32_p`。每次重建后按实际分页更新预览入口和 [预览清单](output/preview-manifest.json)，不得只更新 PDF 而继续使用旧 PNG。

提交后以 `git status --porcelain=v1 --untracked-files=all` 输出为空核对工作区干净。未经作者指示不 push。

## 文件保留与脚本分层

- **不删除任何文件**，包括未跟踪文件、历史结果、旧图、测试产物和过时脚本。只允许有记录地归档，不用删除或新增忽略规则制造干净工作区。
- 当前规则以 `AGENTS.md` 为准；`README.md` 维护运行入口，`plan/` 维护科学协议，`verification/` 记录实际验证范围。交接提示和旧报告不覆盖磁盘现状。
- 测试脚本统一放在 `scripts/test/`，其他当前脚本放在 `scripts/`；保持目录职责清晰、入口准确，避免重复文件和冗余说明。测试使用内存构造数据，不将 mock/placeholder 写入正式结果。
- `archive/` 仅保存已确认停用的内容；归档清单必须记录原路径、新路径、原因和 SHA-256。先核查依赖再移动，目标同名时停止，不覆盖。用途不明的内容原位保留。
- 不执行删除型清理命令，不运行会自动删除临时文件的测试清理流程。归档脚本只供追溯，不作为当前运行入口。
- 3.3 现有成果为 `derived / exploratory`，不自动进入正文；历史清单的 `Verified` 不等于本轮重新验证。接手时先检查脚本、输入、产物和协议哈希。

## 脚本入口与测试

从仓库根目录运行。当前正文数据入口为 `scripts/calculate_f1_raw_scale.py` → `results/summary/f1_raw_scale/`，使用原尺度 F1 和差值、两位小数。正文表使用 `generate_core_tables.py` 中的 `generate_table2_cross_site_f1_paths()` 和 `write_table2_cross_site_f1_latex_rows()`；默认全量运行仍生成历史备查表及检验表，不等于只更新正文表。

| 用途 | 当前入口 | 边界 |
|---|---|---|
| 当前 F1 数据 | `scripts/calculate_f1_raw_scale.py` | 原始 CM → 全精度 F1/差值，写入 f1_raw_scale 子目录 |
| 历史全量更新 | `scripts/run_all_updates.ps1` | 包含旧 DR 与备查表，不是当前正文的推荐入口；保留脚本，不在本轮运行 |
| 正式图件 | `scripts/plot_within_site_f1.py`、`scripts/plot_within_site_map_D.py`、`scripts/plot_degradation_heatmap.py` | 共享 `scripts/figstyle.py` |
| 历史 3.3 分组探索（DR） | `scripts/explore_sec33.py` | `prepare` 固定分组，`analyze` 计算；现有成果不得未经检查覆盖重跑 |
| 3.3 边界探索 | `scripts/explore_sec33_boundary.py` | 当前探索入口，不是单元测试，不代表正式纳入正文 |
| 3.3 候选图 | `scripts/plot_sec33_exploration.py` | 已有脚本；本次核查未发现候选图目录 |
| 旧指标分析核对 | `scripts/analyze_generalization_36paths.py` | Crop-mIoU 备查支线，不是正文 F1 数据入口；仍有引用，暂不归档 |
| 协议单元测试 | `scripts/test/test_sec33_protocol.py` | 7 项内存边界用例，不替代原始数据全链验证 |

测试命令（不生成字节码缓存、不编译论文）：

```powershell
python -B -m unittest discover -s scripts/test -p "test_*.py" -v
python -B scripts/test/test_sec33_protocol.py
```

`legacy/manuscript/HLS-Crop/test_semantic.py` 是历史跨站推理入口，不因名称带 `test` 就迁入单元测试目录。显著性表仍由现有表格脚本生成，仅供追溯；本轮不移动它或改动生成口径。

本次整理和探索核验范围见 [核查记录](verification/system-audit-2026-09-29.md)；归档原路径与 SHA-256 见 [归档清单](archive/2026-09-29-system整理/archive-manifest.json)。

## 核心原则

- 证据优于声称
- 真实数据优于旧正文
- 验证优于"看起来完成"
- 论文正文和项目管理信息严格分离
- 旧 Word 仅参考写作风格和最终格式，不迁移论点、数据或正文；[已归档的迁移地图](archive/2026-09-29-system整理/plan/migration-map.md) 仅保留已停用的历史安排

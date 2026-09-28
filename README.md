# 时空深度学习模型在玉米—大豆分类中的空间泛化能力分析

科研论文工程化写作仓库。

本仓库仅维护美国四站点空间泛化论文，主线为“站内基准 → 美国站间退化 → 空间解释”。

## 目录结构

```
├── AGENTS.md              # AI 辅助写作最高级规则
├── main.tex               # LaTeX 主文件（XeLaTeX + ctex）
├── sections/              # 论文各章节 .tex 文件
├── plan/                  # 论文规划（大纲、术语、迁移地图等）
├── legacy/manuscript/     # 旧 Word 论文（仅参考写作风格和格式，不作为内容来源）
├── evidence/              # 文献证据映射
├── bibliography/          # BibTeX 文献数据库
├── results/               # 实验数据（raw → processed → summary）
├── tables/                # 表格定义与生成
├── figures/               # 图表及数据映射
├── scripts/               # 数据处理与图表生成脚本
├── verification/          # 验证报告
├── output/                # 编译输出
└── word/                  # 最终 Word 投稿稿件
```

## 工作流

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

`main.pdf`、LaTeX 辅助文件和 `.gitignore` 已指定的页面预览不入库；已由 `92b58a2` 跟踪的 `output/sec32_p-{3,4,5}.png` 本轮继续跟踪并更新，不移出索引。`output/preview-manifest.json` 记录当前 PDF、源码和预览的 SHA-256、生成时间、页码及构建时版本状态。未新增忽略规则，也不整体忽略 `output/`。

### 当前 3.2 PDF 与预览（2026-09-29）

- [当前 PDF](main.pdf)：本轮编译生成，6 页；第 4 页为图 3 与 3.2 正文，第 5 页为完整跨站 F1 表与图 4。
- [第 3 页](output/sec32_p-3.png)、[第 4 页正文](output/sec32_p-4.png)、[第 5 页表与图](output/sec32_p-5.png)：均从该 PDF 以 150 dpi 导出。
- `output/table_page_preview.png`、`output/figure4_page_preview.png` 同步为当前第 5 页的副本；`results_layout-*`、`results_spacing-*` 保留为历史预览，不作为当前版面依据。
- 编译：`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`。渲染：`pdftoppm -png -r 150 -f 3 -l 5 main.pdf output/sec32_p`。每次重建后按实际分页更新预览入口和 [预览清单](output/preview-manifest.json)，不得只更新 PDF 而继续使用旧 PNG。

提交后以 `git status --porcelain=v1 --untracked-files=all` 输出为空核对工作区干净。未经作者指示不 push。

## 核心原则

- 证据优于声称
- 真实数据优于旧正文
- 验证优于"看起来完成"
- 论文正文和项目管理信息严格分离
- 旧 Word 仅参考写作风格和最终格式，不迁移论点、数据或正文；`plan/migration-map.md` 仅保留已停用的历史安排

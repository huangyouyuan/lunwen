# 时空深度学习模型在玉米—大豆分类中的空间泛化能力分析

科研论文工程化写作仓库。

本仓库仅维护美国四站点空间泛化论文，主线为“站内基准 → 美国站间退化 → 空间解释”。

## 目录结构

```
├── AGENTS.md              # AI 辅助写作最高级规则
├── main.tex               # LaTeX 主文件（XeLaTeX + ctex）
├── sections/              # 论文各章节 .tex 文件
├── plan/                  # 论文规划（大纲、术语、迁移地图等）
├── legacy/manuscript/     # 旧 Word 论文（写作模式 + 格式基准 + 内容来源）
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
旧 Word → plan → evidence → results → tables/figures
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

`main.pdf`、LaTeX 辅助文件和 `output/` 下的页面预览不入库。页面预览由已跟踪的 LaTeX 与正式图件重新生成；只忽略指定预览文件名，不整体忽略 `output/`。编译命令为 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`，页面预览可用 `pdftoppm -f 页码 -singlefile -png -r 160 main.pdf output/名称_page_preview` 导出。

提交后以 `git status --porcelain=v1 --untracked-files=all` 输出为空核对工作区干净。未经作者指示不 push。

## 核心原则

- 证据优于声称
- 真实数据优于旧正文
- 验证优于"看起来完成"
- 论文正文和项目管理信息严格分离
- 旧 Word 决定写作模式和最终格式

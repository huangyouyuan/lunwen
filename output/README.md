# 当前稿件

唯一当前整稿：[main.pdf](main.pdf)。根目录`main.pdf`和原`previews/`已归档，后续不再创建这两处副本。

从仓库根目录执行：

```powershell
latexmk -xelatex -synctex=1 -interaction=nonstopmode -halt-on-error main.tex
```

[.latexmkrc](../.latexmkrc)与[VS Code配置](../.vscode/settings.json)统一设置：

| 位置 | 用途 |
|---|---|
| `output/main.pdf` | 当前整稿，直接打开这一份 |
| `output/main.synctex.gz` | 源码与PDF跳转信息 |
| `output/build/main/` | 主稿辅助文件及日志 |
| `output/build/<图件任务>/` | 独立图件编译文件；正式图在`figures/` |
| `verification/layout/<任务>/` | 页面检查图片 |
| `archive/manuscript/<日期>/<任务>/` | 旧稿、试排和必要备份 |

保存正文不会自动编译，自动清理关闭。替换已有版本前按[写作流程](../plan/writing-workflow.md)核对并保留必要历史文件；不重新建立预览目录或为同一版本重复备份。

本次默认输出、归档和页面一致性核查见[记录](../verification/default-output-2026-10-15.json)，控制台输出在[编译日志](build/main/compile-output.txt)。[原previews](../archive/manuscript/2026-10-15/default-output/previews/)与[旧清单](../archive/manuscript/2026-10-15/default-output/preview-manifest.json)仅作历史保存。各文档职责集中见[写作流程](../plan/writing-workflow.md)，不在本入口重复维护正文状态。

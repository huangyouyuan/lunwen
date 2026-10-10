# 玉米—大豆分类空间泛化论文

当前主线：四站空间背景 → 本站错误基准 → 跨站F1差距 → 空间条件与错分变化的对应关系。

总体计划见 [plan/outline.md](plan/outline.md)，最新交接见 [HANDOVER.md](HANDOVER.md)，规则见 [AGENTS.md](AGENTS.md)。

## 活动目录

| 目录 | 用途 |
|---|---|
| `plan/` | 当前结构、口径、证据路由与具体任务 |
| `sections/`、`main.tex` | 当前正文；保存不自动编译 |
| `results/raw/` | 原始整数矩阵及FRAGSTATS结果表 |
| `results/processed/` | F1处理链、完整参考斑块和计数、可复用的逐次分析底表 |
| `results/summary/` | 科学数值权威入口，见其README |
| `figures/`、`tables/` | 正式图表及保留的定向混淆探索图 |
| `scripts/`、`scripts/test/` | 当前数据与图表脚本、相关测试 |
| `bibliography/`、`evidence/` | 文献元数据与证据映射 |
| `verification/` | 当前整理核查及B站身份说明 |
| `archive/` | 停用文件、原字节快照与迁移清单 |
| `legacy/`、`output/`、`word/` | 实验和写作参考、既有编译产物及投稿稿件 |

下一项是 [1.3与3.1基础材料整理](plan/tasks/2026-10-10-sec13-sec31-foundations.md)，不默认执行分级、聚类或联合建模。

## 保留脚本

| 脚本 | 职责 |
|---|---|
| `calculate_f1_raw_scale.py` | 两份raw矩阵→有效F1链，阅读前先校验已有产物 |
| `generate_core_tables.py` | 仅生成现行12路径正文表，不生成旧口径和检验表 |
| `plot_within_site_f1.py`、`plot_within_site_map_D.py`、`plot_degradation_heatmap.py` | 正式图件，共享 `figstyle.py` |
| `sec33_metrics.py` | 只读指标和五次完整统计函数 |
| `explore_sec33_directional_confusion_closeout.py` | 从保留整数表计算收尾结果，已有结果本次不重跑 |
| `plot_sec33_directional_confusion_closeout.py` | 保留探索图来源，不自动写入正文 |

从仓库根目录执行必要的只读检查：

```powershell
python -B -m unittest scripts/test/test_sec33_directional_confusion_closeout.py scripts/test/test_sec33_directional_confusion.py scripts/test/test_f1_raw_scale.py scripts/test/test_f1_presentation.py -v
```

手动编译为 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`，只在授权任务中运行；既有PDF与预览来源见 `output/preview-manifest.json`，本次未重建。

## 历史入口

[2026-10-10归档](archive/2026-10-10-mainline/README.md)保存旧口径、图块/聚类候选、任务和源码，源码以 `.source` 停用。复核后27份可复用的整站、距离和逐次底表已移回结果目录，旧报告与不适用方案仍归档；具体见[恢复清单](archive/2026-10-10-mainline/restored-reusable.csv)。历史清单中的原路径按迁移与恢复两份清单解析。

不得删除文件或新增忽略规则制造干净状态。本次未改变Git跟踪规则，不自动提交或推送。

# results/summary 文件索引

论文正文数字的唯一来源。类别顺序：所有 `cm_ij` 按 corn=0, other=1, soybean=2（训练标签减 1）。

## 主线（玉米、大豆 F1 体系）

| 文件 | 内容 | 脚本 | 上游 |
|------|------|------|------|
| `within_site_crop_f1.csv` | 12 组站内 OOF pooled 玉米 F1 / 大豆 F1 / 其它 F1 / OA | `calculate_crop_f1.py` | `results/raw/within_site_confusion_matrices.csv` ← `D:/20{site}/…/metrics_summary.csv` |
| `within_site_crop_f1_fold_stats.csv` | 12 组五折 mean±std | 同上 | 同上 |
| `cross_site_crop_f1_per_fold.csv` | 180 行 checkpoint 级 F1 | `extract_cross_site_cm.py` | `results/raw/cross_site_confusion_matrices.csv` ← `legacy/experiment-results/cross_site_all_20260916/` |
| `cross_site_crop_f1_summary.csv` | 12 条有向迁移路径、36 个模型—路径组合的 mean±std（每组合 5 次预测，ddof=1） | 同上 | 同上 |
| `crop_f1_degradation_36paths.csv` | 36 个模型—路径组合的 ΔF1（pp）及站内、跨站 F1；仅供追溯，正文不用 | `calculate_crop_f1_degradation.py` | 上两者 |
| `crop_f1_relative_degradation_36paths.csv` | derived：36 个模型—路径组合的泛化退化比例 DR（%）及站内、跨站 F1；正文与图 4 数据 | 同上 | `within_site_crop_f1.csv` + `cross_site_crop_f1_summary.csv` |

正文采用跨站绝对 F1 + 泛化退化比例 DR；上述跨站数据覆盖 12 条有向迁移路径、36 个模型—路径组合，原文件名中的 `36paths` 为历史命名，不表示 36 条独立迁移路径。百分点差值文件保留，数据和处理脚本不因文字口径同步而改动。

相对退化比例为 `100 × (within_F1 - cross_mean_F1) / within_F1`，`within_F1` 取同一模型在目标站的站内汇总值。列 `corn_relative_loss_pct`、`soybean_relative_loss_pct` 分别对应玉米、大豆，单位 %；原 `*_loss_pp` 仍为百分点差值。模型平均比例为 12 条路径比例的算术平均。

## 补充（Crop-mIoU 体系，不控制正文结构）

来自 `legacy/experiment-results/paper_tables/`，类别顺序与主线一致。

| 文件 | 内容 |
|------|------|
| `generalization_degradation_36paths.csv` | Crop-mIoU / 三类 mIoU 退化 |
| `within_site_oof_baseline.csv` | Crop-mIoU 站内基准（含 pooled CM） |
| `model_significance_analysis.csv` | Crop-mIoU Friedman（12 路径） |
| `../processed/generalization_analysis.csv` | Crop-mIoU 按源站/目标站汇总、不对称性 |

## 结论与验证

发现记录在 `plan/claims.md`（含 S1–S5 数据处理链说明），验证记录在 `verification/verification-report.md`。本目录不放分析结论文档。

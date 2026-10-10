# results/summary 文件索引

论文正文数字的唯一来源。类别顺序：所有 `cm_ij` 按 corn=0, other=1, soybean=2（训练标签减 1）。

## 当前正文数据（原尺度 F1，`f1_raw_scale/`）

由 `scripts/calculate_f1_raw_scale.py` 从 `results/raw/` 的整数混淆矩阵经 `results/processed/f1_raw_scale/` 生成，保存 17 位有效数字；正文、表格和图件显示两位小数，比较和均值均用未舍入值。

| 文件 | 内容 |
|------|------|
| `f1_raw_scale/within_site_crop_f1.csv` | 12 组站内汇总玉米 F1 / 大豆 F1 / 其它 F1 / OA |
| `f1_raw_scale/within_site_crop_f1_fold_stats.csv` | 12 组五折 mean±std（ddof=1），仅说明稳定性 |
| `f1_raw_scale/cross_site_crop_f1_per_fold.csv` | 180 次完整目标站预测的逐次 F1 |
| `f1_raw_scale/cross_site_crop_f1_summary.csv` | 36 个模型—路径组合的五次 mean±std（ddof=1） |
| `f1_raw_scale/crop_f1_difference_36paths.csv` | 36 个模型—路径组合的 ΔF1 及站内、跨站 F1；正文与图 4 数据 |
| `f1_raw_scale/run_manifest.json` | 输入、脚本与产物的 SHA-256 和运行口径 |

ΔF1 = 同模型目标站站内汇总 F1 − 跨站 F1 五次均值，列为 `corn_f1_difference`、`soybean_f1_difference`；不乘 100、不除基准，与 F1 同为原始刻度。模型平均差值为 12 条路径差值的算术平均。显示 0.00 不表示真实值为零。

## 历史口径（旧 DR 体系，仅供追溯）

下列文件及其脚本保留，不再作为正文数据入口；不得改列名充当 ΔF1。

| 文件 | 内容 | 脚本 | 上游 |
|------|------|------|------|
| `within_site_crop_f1.csv` | 12 组站内 OOF pooled 玉米 F1 / 大豆 F1 / 其它 F1 / OA | `calculate_crop_f1.py` | `results/raw/within_site_confusion_matrices.csv` ← `D:/20{site}/…/metrics_summary.csv` |
| `within_site_crop_f1_fold_stats.csv` | 12 组五折 mean±std | 同上 | 同上 |
| `cross_site_crop_f1_per_fold.csv` | 180 行 checkpoint 级 F1 | `extract_cross_site_cm.py` | `results/raw/cross_site_confusion_matrices.csv` ← `legacy/experiment-results/cross_site_all_20260916/` |
| `cross_site_crop_f1_summary.csv` | 36 个模型—路径组合的 mean±std（每组合 5 次预测，ddof=1） | 同上 | 同上 |
| `crop_f1_degradation_36paths.csv` | 36 个模型—路径组合的百分点差值及站内、跨站 F1 | `calculate_crop_f1_degradation.py` | 上两者 |
| `crop_f1_relative_degradation_36paths.csv` | 36 个模型—路径组合的泛化退化比例 DR（%），历史正文与图 4 数据 | 同上 | `within_site_crop_f1.csv` + `cross_site_crop_f1_summary.csv` |

历史 DR 为 `100 × (within_F1 − cross_mean_F1) / within_F1`，列 `corn_relative_loss_pct`、`soybean_relative_loss_pct`；`*_loss_pp` 为百分点差值。跨站数据覆盖 12 条有向迁移路径、36 个模型—路径组合，文件名中的 `36paths` 为历史命名，不表示 36 条独立迁移路径。数据和处理脚本不因文字口径同步而改动。

`sec33_exploration/` 为 3.3 第一轮探索结果，标为 derived / exploratory，采用冻结协议中的 DR 口径，不自动进入正文。

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

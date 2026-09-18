# Capability Audit

记录大型任务实际使用的能力，防止跳过必要步骤。

## 已执行

| 能力 | 日期 | 说明 |
|------|------|------|
| Legacy manuscript analysis | 09-16 | 结构、样式、格式、作者信息（含数学域上标）提取 |
| Project scaffolding | 09-16 | 目录与核心文件 |
| Style / format extraction | 09-16/17 | 旧 Word + 测绘通报模板；模板为准，未覆盖处以旧稿为准 |
| Terminology standardization | 09-16 | 术语表；站点映射 A=iw, B=iw2, C=ida, D=il |
| Code audit | 09-17 | 从 HLS-Crop 训练代码核对超参、折划分、增强、距离带定义，修正方法章节 |
| Result extraction | 09-18 | 站内五折 CM（D:/20{site}）、跨站 180 组 CM（legacy/experiment-results） |
| Statistical analysis | 09-18 | F1/OA、ΔF1、Friedman + Wilcoxon–Holm（n=12 路径） |
| Result verification | 09-18 | 见 verification/verification-report.md，7 项 Verified |
| Table generation | 09-18 | table1、table1b、table2、table3 |
| Figure generation | 09-18 | 6 子图退化热力图 |
| LaTeX validation | 09-18 | 方法章节公式 + caption 字体修正后编译通过 |

## 待执行

| 能力 | 触发条件 |
|------|----------|
| Evidence mapping | 引言重写时 |
| Chapter blueprint | 引言、3.3.2 论证段落 |
| Structure review | 第 3 章正文完成后 |
| Quality review | 同上 |
| Peer review simulation | 全文完成后 |

## 本轮教训

- 修脚本时没有同步 `plan/` 与 `verification/`，导致系统文件与数据脱节两天
- 临时说明文档（README_UPDATES.md、crop_f1_analysis_summary.md）游离于系统之外，且后者在 results/summary 中保留了已证伪的结论——今后发现写入 plan/claims.md 与 verification-report.md，不另建文件

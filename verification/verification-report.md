# Verification Report

结果只允许：Verified / Partially verified / Not verified。

| 验证对象 | 验证方式 | 结果 | 日期 | 备注 |
|----------|----------|------|------|------|
| 工程目录结构 | 文件系统检查 | Verified | 2026-09-16 | — |
| main.tex 编译 | latexmk -xelatex，exit 0，PDF 生成 | Verified | 2026-09-18 | 方法章节新增 F1/OA/ΔF1 三个 equation；caption 字体改为 \DeclareCaptionFont 声明（原 font={songti,zihao=-5} 写法在 2026-09-17 编译时被 caption 包忽略并只发 warning，本次报错后修正） |
| 类别顺序 | 站内、跨站脚本统一 corn=0, other=1, soybean=2；修正后大豆 F1 与用户独立按 CM 复算一致 | Verified | 2026-09-18 | 修正前大豆列实为其它类，导致虚假"负退化" |
| 站内 pooled CM = Σ 五折 CM | `calculate_crop_f1.py` 逐组断言 | Verified | 2026-09-18 | 12/12 通过 |
| 站内 OA | 对角线/总像元；与用户独立复算范围 89.10%–94.82% 对照 | Verified | 2026-09-18 | 修正前误用全矩阵和，12 值全为 100% |
| 跨站记录完整性 | 180 行 = 36 路径 × 5 fold | Verified | 2026-09-18 | — |
| 泛化退化符号 | 72 个 ΔF1 全 > 0，min 0.4414 pp | Verified | 2026-09-18 | — |
| 表3 配对单位 | `data_matrix.shape == (12, 3)` | Verified | 2026-09-18 | 修正前误用 60 个 checkpoint 样本 |
| 表3 Holm 校正 | step-down（累积最大 + 首次不显著后停止）；用户独立复核判断一致 | Verified | 2026-09-18 | 修正前逐个比阈值；p_holm：玉米 0.0137/0.0029/0.5693，大豆 0.0015/0.0015/0.9097 |
| 旧结论残留 | grep `3.25|5.35|负退化|Crop-mIoU 作为主` | Verified | 2026-09-18 | 正文、plan 无残留；仅 verification/capability-audit/HANDOVER 保留事故记录 |
| 热力图与数据一致 | 脚本打印六组 mean/std/min/max 与 `crop_f1_degradation_36paths.csv` 对照 | Verified | 2026-09-18 | 图生成于类别修正后 |
| citation key | 与 references.bib 核对 | Not verified | — | bib 尚未导入 |
| 正文数字可追溯 | 与 results/summary 核对 | Not verified | — | 第 3 章正文尚未撰写 |

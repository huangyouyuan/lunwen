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
| 3.1 正文数字 | 与 `within_site_crop_f1.csv`、`within_site_crop_f1_fold_stats.csv` 逐一核对：F1 范围、折间 std 范围、C/D 站最大差值、U-TAE 与 3D U-Net 差值 < 1 pp、各站最优模型 | Verified | 2026-09-19 | 用户草稿，AI 核对 |
| 站内柱状图与数据一致 | 脚本打印 12 组值与 csv 对照；柱顶标注与 csv 两位小数一致 | Verified | 2026-09-19 | 已按用户要求改为上下排、子图题图例在下 |
| D 站分类结果图数据来源 | 三模型 `reference.tif` sha256 一致；`oof_prediction.tif` 为五折拼接；窗口 (13,8) 2×2 内作物像元错误率 12.1/5.8/4.8%、边界带 32.0/15.3/13.4%，与全站排序一致 | Verified | 2026-09-20 | 09-19 窗口 (5,7) 按总错误率极差选，三模型差异不明显；09-20 改为只看玉米/大豆像元与边界带 |
| main.tex 编译（含 3.1 图文） | latexmk -xelatex，exit 0 | Verified | 2026-09-19 | — |
| citation key | 与 references.bib 核对 | Not verified | — | bib 已导入 71 条，正文尚无 \cite |
| 正文数字可追溯 | 与 results/summary 核对 | Partially verified | 2026-09-19 | 3.1 已核；3.2、3.3 未写 |

## 3.2 收尾验证（2026-09-29）

本轮状态：**Verified（限本轮 3.2 收尾范围）**。以上表格保留为历史记录，其中“3.2 未写”“36 路径”和旧 ΔF1 图口径不作为当前状态。当前跨站实验为 12 条有向迁移路径、36 个模型—路径组合，每组合五次完整目标站预测；正文采用跨站绝对 F1 + 泛化退化比例 DR。

### 本轮实际执行

| 验证对象 | 验证方式与范围 | 结果 |
|---|---|---|
| 三段正文数字与比较 | 从当前 summary 只读复算，逐段匹配全部 22 处百分数；核对 12 条路径、36 个组合、每组合五次预测、全部 72 个跨站 F1 低于同一模型目标站基准、A 站最高值及 C 站玉米最低值 | Verified |
| 模型均值与方向 | 分别计算每模型 12 条路径平均 F1、平均 DR；核对固定目标站 D 的 ConvGRU 大豆 C→D/B→D，以及 ConvGRU、3D U-Net 玉米和大豆的 B↔D 方向 | Verified |
| 五次均值口径与 DR 公式 | 180 行 `cross_site_crop_f1_per_fold.csv` 按 36 个组合核对每组五个折，重算均值和样本标准差，与 summary 的最大差异分别为 6.0×10⁻⁷、6.71×10⁻⁷；72 个 DR 与目标站基准公式的最大差异 4.94×10⁻⁷（百分数单位），均在六位小数导出舍入容差内 | Verified |
| 完整跨站 F1 表 | 72 个路径精度值及 6 个模型均值逐格对照 summary、CSV 和 LaTeX 表体，同时核对源—目标路径标签 | Verified |
| 六子图热力图 | 直接读取现有六个子图 PDF：72 个数值及其源站行、目标站列坐标与 DR summary 一致；图件未重新绘制 | Verified |
| 正文边界与相关规则 | 三段保留；不作分类难度归因、不称 DR 消除站点差异、不以 DR 小判断泛化更强、不推广方向规律；相关计划与风格条目已同步，旧稿迁移安排已标为停用历史 | Verified |
| 修改范围 | 与基线 `92b58a2` 对照：3.1、3.3、方法、实验数据、处理脚本、表体、正式图件、主文件和 `.gitignore` 未变；未改变早停或实验设计 | Verified |
| 编译与交叉引用 | `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`，exit 0，6 页；日志无 Overfull/Underfull、未定义引用或 LaTeX 错误；辅助文件确认图 3/3.2 在第 4 页、表 1/图 4 在第 5 页、3.3 标题在第 6 页 | Verified |
| 当前版面与预览 | 从本轮 `main.pdf` 渲染第 3—5 页并逐页查看：标题归属和图表顺序正确，无文字截断或溢出；通栏表图延后，未调整间距强行塞页。另独立逐页渲染，PNG 的 SHA-256 与保存预览逐一一致 | Verified |

正文数值复算结果（模型顺序 ConvGRU / 3D U-Net / U-TAE）：跨站玉米 F1 范围 85.68%～92.92%，大豆 83.08%～92.15%；路径平均玉米 F1 为 88.73% / 90.18% / 90.39%，大豆为 87.64% / 89.69% / 89.77%；平均玉米 DR 为 3.05% / 4.18% / 4.21%，大豆为 3.32% / 4.01% / 4.22%。ConvGRU 大豆 C→D 为 0.99%，B→D 为 8.17%，D→B 为 3.75%；3D U-Net 大豆 B→D 为 4.26%，D→B 为 6.65%。

执行说明：两次内联核查先后因正文行定位未匹配、正则转义而报 `StopIteration`、`re.error: bad escape \\l`，均未作为通过依据；随后在系统临时目录运行明确定位正文和图表结构的两份只读核查脚本，以上断言全部通过。`git diff --check` 首次发现本报告末尾多余空行，修正后复查通过。临时核查脚本不属于实验数据处理链。

### 编译产物与预览绑定

- PDF：`main.pdf`，2026-09-29 01:25:21 +08:00 生成，815240 字节，6 页；SHA-256 为 `408267f28272c5fb11b9fc3c952550813905c578a5ea58682b4f9e90d7e0df48`。
- 当前预览：`output/sec32_p-{3,4,5}.png`，2026-09-29 01:36:08—09 +08:00 由上述 PDF 以 150 dpi 渲染。第 4 页为图 3 与 3.2 三段正文，第 5 页为完整跨站 F1 表和图 4。
- `output/table_page_preview.png`、`output/figure4_page_preview.png` 同步为当前第 5 页的逐字节副本。`results_layout-*`、`results_spacing-*` 仅为保留的历史预览。
- `output/preview-manifest.json` 记录 PDF、源码锚点、所有当前预览的哈希和生成时间。构建基线为 `92b58a2` 加本轮工作区修改；构建时未提交，不把基线提交本身误称为这次 PDF 对应的完整版本。
- 现有告警仍为 xeCJK 字体族重定义、SimSun/SimHei 字形替代和空参考文献。它们不影响本轮 3.2 的数字及版面核对，但本轮没有消除这些全文层面问题。

### 既有验证与未验证项

- 既有 raw→summary 全链验证：引用 `plan/progress.md` 中“3.2 起草与接手核查（2026-09-26—27）”及 `plan/claims.md` C4 的记录；原记录包含上游与 raw 逐项一致、站内汇总矩阵等于五折之和、由混淆矩阵重算 F1/OA/DR。**本轮未重跑该全链**，只核对数据与处理脚本未变，并执行以上 summary→正文/图表的检查。
- **Not verified（本轮未执行）**：重新训练、外部原始实验复跑、文献元数据与全文引用验证、研究区图和其它章节的全面审查、3.3 空间分析与分组处理链。未把这些项目列为本轮完成。
- 历史核查记录不覆盖或删除；3.2 本轮技术验证完成不等于整篇论文定稿。

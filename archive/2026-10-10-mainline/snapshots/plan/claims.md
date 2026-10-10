# 论文核心论点

每条论点必须有数据支撑。数字来源一律为 `results/summary/`，口径见 `plan/experiment-protocol.md`。每条 claim 标注它经过数据处理链的哪几步（S1–S5），便于回溯。

## 当前 3.1—3.2 证据更新（2026-10-01）

按最新口径，F1、标准差及差值以原始刻度显示两位小数；下方 S1—S5 与 C1—C7 中的旧 F1 显示、DR 数字及图表入口仅作历史追溯，当前采用本表及 `experiment-protocol.md`。C8 的研究问题和非指标约束不在本轮改写。新链为两份 raw CM → `scripts/calculate_f1_raw_scale.py` → `results/processed/f1_raw_scale/` → `results/summary/f1_raw_scale/`；计算保存 17 位有效数字，不从旧舍入表换算。

| 论点 | 当前证据（两位显示，比较使用未舍入值） | 新 summary 文件 |
|---|---|---|
| C1 | 站内玉米 F1 为 0.91～0.96，大豆为 0.90～0.96；同站同模型玉米均较高，差值小于 0.02；U-TAE 与 3D U-Net 差值绝对值均小于 0.01 | within_site_crop_f1.csv |
| C2 | 12 组实验的两作物 F1 折间样本标准差均小于 0.01；显示 0.00 不表示没有波动 | within_site_crop_f1_fold_stats.csv |
| C3 | 两作物模型间最大差值在 C 站约为 0.02、D 站约为 0.04；D 站跨度最大，不扩大为所有指标的难度排序 | within_site_crop_f1.csv |
| C4 | 36 个模型—路径组合的两作物 F1 均低于目标站基准；跨站玉米 0.86～0.93、大豆 0.83～0.92；两作物最大值目标均 A，玉米最小值目标均 C | cross_site_crop_f1_summary.csv、crop_f1_difference_36paths.csv |
| C5 | ConvGRU 路径平均玉米/大豆 F1 为 0.89/0.88，低于另两模型（两作物均约 0.90）；不因两位显示相同断言另两模型完全相等 | cross_site_crop_f1_summary.csv |
| C6 | 两作物平均差值 ConvGRU 均约 0.03，另两模型均约 0.04；差值较小不代表跨站绝对 F1 更高 | crop_f1_difference_36paths.csv |
| C7 | 固定 D 目标站，ConvGRU 大豆 C→D 差值 0.01、B→D 0.07；大豆 B→D/D→B：ConvGRU 0.07/0.03，3D U-Net 0.04/0.06；玉米方向亦相反，仅描述该站点对均值 | crop_f1_difference_36paths.csv |

上述文件均位于 `results/summary/f1_raw_scale/`。Verified：主干迁移时从新链核对；具体测试及未编译边界见 `plan/tasks/f1-scale-migration-checklist.md` 的执行记录。旧比例相关、逐次范围等未迁入本轮差值论点。

## 历史数据处理链（旧口径，不作为当前运行入口）

以下保留截至 2026-09-29 的旧数据链说明；正文、图 4 和一键入口仅指当时版本。当前入口与论点见文件开头的更新表，不按本节恢复旧 DR 正文。

### S1 站内混淆矩阵 → F1 / OA / 折间稳定性

**脚本**：`scripts/calculate_crop_f1.py`

**输入**：`D:/20{site}/2023{model}{site}results/summary/metrics_summary.csv`（iw、iw2 站目录为 `2023{site}{model}results`），共 12 个文件，每个含 5 行 `fold`（各测试折 CM）和 1 行 `oof_pooled`（五折 CM 之和）。CM 列名为 `cm_gt_{X}_pred_{Y}`，X、Y ∈ {corn, other, soybean}。

**处理**：
1. 把 `cm_gt_X_pred_Y` 九列按 `CLASS_ORDER = ['corn', 'other', 'soybean']` 排成 3×3 矩阵，索引 0/1/2 对应训练时减 1 后的标签。类别顺序在这一步固定，下游全部沿用。
2. 断言每组 `oof_pooled` CM 等于其 5 个 fold CM 逐元素之和；不等则报错终止。
3. 从 pooled CM 计算各类 F1（Precision = C_ii / Σ_j C_ji，Recall = C_ii / Σ_j C_ij）和 OA = trace / 总像元。
4. 从每个 fold CM 单独计算同样指标，按 (model, target) 求均值和样本标准差（ddof=1）。

**输出**：
- `results/raw/within_site_confusion_matrices.csv`——12 组 × (5 fold + 1 pooled) 的标准顺序 CM
- `results/summary/within_site_crop_f1.csv`——pooled 口径的 corn_f1 / soybean_f1 / other_f1 / oa，站内基准
- `results/summary/within_site_crop_f1_fold_stats.csv`——折间 mean / std，只用于稳定性

### S2 跨站混淆矩阵 → 路径级 F1

**脚本**：`scripts/extract_cross_site_cm.py`

**输入**：`legacy/experiment-results/cross_site_all_20260916/{model}__{source}_2023__{digest}/{target}_2023/metrics_summary.csv`，36 个 (model, source, target) 组合，每个取 5 行 `fold`（源站第 k 折 checkpoint 对目标站全部 400 图块的 CM）。

**处理**：
1. 与 S1 同一 `CLASS_ORDER` 重排 CM。
2. 每行 CM 单独计算 corn_f1 / soybean_f1 / other_f1。
3. 按 (model, source, target) 对 5 行求均值和样本标准差（ddof=1）。不拼跨站 OOF，不做集成。

**输出**：
- `results/raw/cross_site_confusion_matrices.csv`——180 行标准顺序 CM
- `results/summary/cross_site_crop_f1_per_fold.csv`——180 行 checkpoint 级 F1，供 S4 检验和追溯
- `results/summary/cross_site_crop_f1_summary.csv`——36 行路径级 mean ± std

### S3 泛化退化

**脚本**：`scripts/calculate_crop_f1_degradation.py`

**输入**：S1 的 `within_site_crop_f1.csv`（按目标站取基准）+ S2 的 `cross_site_crop_f1_summary.csv`。

**处理**：对每条 (model, source, target)，ΔF1_c = 100 × (F1_c^{pooled}(model, target) − F1_c^{cross mean}(model, source, target))，c ∈ {corn, soybean}。基准是同一模型在目标站的 OOF pooled 值，不是源站。

**输出**：`results/summary/crop_f1_degradation_36paths.csv`——36 行，含站内基准、跨站 mean ± std、ΔF1（pp）。

**相对比例（2026-09-23 新增，图 4 采用）**：同一脚本从上述站内与跨站 F1 计算 DR_c = 100 × (站内 F1 − 跨站 F1 五次均值) / 站内 F1，单位 %，输出 `results/summary/crop_f1_relative_degradation_36paths.csv`。两种退化计算中的 F1 均取 0～1，DR 与召回率 R 区分。分母为同一模型在目标站的站内汇总 F1，必须为正；模型平均比例为 12 条路径比例的算术平均。原 ΔF1 文件与已有表格口径不变。

### S4 表格与显著性检验

**脚本**：`scripts/generate_core_tables.py`

**输入**：S1、S2、S3 输出。

**处理**：
- 表1：S1 pooled 值按模型 × {玉米 F1, 大豆 F1, OA} 排成 A/B/C/D + Mean。
- 表1b：S1 折间 mean ± std，同布局。
- 正文表2：从 S2 的路径级汇总表提取 12 条迁移路径，按 ConvGRU、3D U-Net、U-TAE 分别列出玉米和大豆 F1；每格为 5 次预测的 F1 均值，末行对 12 条路径取平均，不重复列退化值。
- 分析备查表：S3 按模型 × 作物汇总，跨站 F1 取该模型 12 条路径的路径均值再求 mean ± std，ΔF1 同理。
- 表3：从 S2 的 180 行按 (source, target, model) 先求 5 次均值，得 12 × 3 矩阵；对每种作物做 Friedman；三对 Wilcoxon 符号秩；Holm step-down（p 升序，第 k 个校正 p = (m−k)·p 取累积最大，首次不显著后其余不再拒绝）。检验对象是跨站 F1，不是 ΔF1。**2026-09-27 作者决定：本篇正文不使用该检验作显著性结论**。12 条路径共享 4 个站点，不是独立样本；脚本与结果文件保留，仅供追溯。

**输出**：`tables/table1_within_site_baseline.csv`、`table1b_within_site_fold_stability.csv`、`table2_cross_site_f1_12paths.csv`、`table2_cross_site_f1_12paths_rows.tex`、`table2_cross_site_summary.csv`、`table3_significance_tests.csv`。正文通过 `\input` 读取脚本生成的表体，不重复维护数字。

### S5 图

**热力图**：`scripts/plot_degradation_heatmap.py 1`，输入 S3 的 `crop_f1_relative_degradation_36paths.csv`。每个 (model, crop) 把 12 条路径的相对退化比例 pivot 成 4×4（行源站、列目标站，A–D），对角线置 NaN；6 子图按两行三列排列，上玉米、下大豆，图框各 3.8 cm，共用下方横向色标 0–9%，LaTeX 标签“泛化退化比例/%”。每子图一个 PDF + 色标 PDF，输出 `figures/results/fig_degradation_heatmap_{a..f,cbar}.pdf`。

**站内条形图**：`scripts/plot_within_site_f1.py`，输入 S1 的 `within_site_crop_f1.csv`。玉米、大豆各一子图上下排，横向条形：纵轴站点 A–D、每站三模型条，横轴 F1 换算为百分数、条末端标两位小数。每子图一个 PDF，输出 `figures/results/fig_within_site_f1_{a,b}.pdf`。

**D 站分类结果图**：`scripts/plot_within_site_map_D.py`，输入 `D:/20il/2023{model}ilresults/summary/maps/` 的 `reference.tif` 与 `oof_prediction.tif`（五折拼接，每图块预测来自未训练过它的模型；断言三模型 reference sha256 一致）。上行全站标红框，下行红框放大；窗口取图块网格 (13,8) 起 2×2，按"真实玉米/大豆像元错误率差 + 类别边界带错误率差（ConvGRU 相对另两模型均值）"最大选出。每子图一个 PDF，输出 `figures/results/fig_within_site_map_D_{a..h}.pdf`。

图题、子图题、图例均为 LaTeX 文本（subcaption、\modellegend / \classlegend），图片里只有图框、刻度、数值、轴标签。

### 分析备查体系（不进正文）

`results/summary/generalization_degradation_36paths.csv`、`within_site_oof_baseline.csv`、`model_significance_analysis.csv` 直接复制自 `legacy/experiment-results/paper_tables/`，是实验侧生成的 Crop-mIoU 表；`results/processed/generalization_analysis.csv` 由 `scripts/analyze_generalization_36paths.py` 从前者派生。类别顺序与主线一致，仅供分析核对；本文不设补充材料。

---

## 历史 Claim 1（旧口径）：站内三模型排序为 U-TAE ≈ 3D U-Net > ConvGRU，玉米略易于大豆

**内容**：站内 OOF pooled 玉米 F1 为 0.915 / 0.941 / 0.944（ConvGRU / 3D U-Net / U-TAE），大豆 F1 为 0.906 / 0.934 / 0.937，OA 为 0.896 / 0.928 / 0.931。3D U-Net 与 U-TAE 差距 < 0.3 pp，二者高于 ConvGRU 约 2.6–3.5 pp。同一模型玉米 F1 高于大豆 0.6–0.9 pp。

**数据来源**：`results/summary/within_site_crop_f1.csv`（S1 步骤 1–3；模型均值为四站汇总值的算术平均，见 S4 表1 Mean 列）；图 `figures/results/fig_within_site_f1_{a,b}.pdf`（S5）

**状态**：已验证（2026-09-18）；正文 3.1 已写（2026-09-19），范围 90.98–96.23 / 89.55–95.89、C 站最大差 1.61/1.50、D 站 3.58/3.98 均核对

## 历史 Claim 2（旧口径）：站内训练稳定，折间波动不超过 1 pp

**内容**：12 组站内实验五折标准差：玉米 F1 0.12–0.73 pp，大豆 F1 0.06–0.96 pp，OA 0.13–0.86 pp。最大值均出现在 3D U-Net 的 B 站。

**数据来源**：`results/summary/within_site_crop_f1_fold_stats.csv`（S1 步骤 4）

**状态**：已验证（2026-09-18）

## 历史 Claim 3（旧口径）：站点难度差异稳定，C 站最难、A 站最易

**内容**：三模型在 C 站 OA 均最低（0.891 / 0.910 / 0.912），在 A 站均最高（0.901 / 0.937 / 0.948）。A 与 C 的 OA 差距为 1.0 / 2.7 / 3.7 pp，与 ConvGRU 相对另两模型的差距量级相当，大于 3D U-Net 与 U-TAE 之间的差距。

**数据来源**：`results/summary/within_site_crop_f1.csv`（S1 步骤 1–3）

**状态**：已验证（2026-09-18）；与景观特征的对应关系待 3.3

**口径限定**（2026-09-26 核）：“C 站最难”只对 OA 成立。玉米 F1 三模型均以 C 站最低，但 ConvGRU 的 C、D 两站只差 0.01 个百分点；大豆 F1 ConvGRU 最低在 B 站（89.55%），不在 C 站。正文引用站点难度时须注明指标。

## 历史 Claim 4（旧口径）：跨站后全部模型—路径组合低于目标站当地训练基准，跨站 F1 高低与目标站有关

**内容**：36 个模型—路径组合（3 模型 × 12 条有向路径）的玉米、大豆跨站 F1 均低于同一模型在目标站的站内汇总 F1，72 个泛化退化比例 DR 全部为正，范围 0.48%～8.17%。跨站 F1：玉米 85.68%～92.92%，大豆 83.08%～92.15%。三模型玉米、大豆跨站 F1 最高值均在以 A 为目标站的路径上（玉米均为 B→A；大豆 B→A、B→A、D→A），与站内 A 站点最高对应；三模型玉米跨站 F1 最低值均在以 C 为目标站的路径上（B→C、A→C、B→C）；大豆最低值无此一致性。

**口径与边界**：差距是相对目标站当地训练基准的差距，不是同一个已训练模型离开源站前后的变化；站内基准不是理论精度上限。

**数据来源**：`tables/table2_cross_site_f1_12paths.csv` ← `results/summary/cross_site_crop_f1_summary.csv`（S2→S4）；`results/summary/crop_f1_relative_degradation_36paths.csv`（S3）。百分点差值文件 `crop_f1_degradation_36paths.csv` 保留备查（0.44～7.39 个百分点），正文不用。

**状态**：Verified（2026-09-27，从 raw 混淆矩阵经 summary 重算，表 72 格一致）

## 历史 Claim 5（旧口径）：按路径平均，跨站 F1 排序与站内一致，ConvGRU 最低；U-TAE 与 3D U-Net 互有高低

**内容**：12 条路径平均跨站 F1，玉米 88.73% / 90.18% / 90.39%，大豆 87.64% / 89.69% / 89.77%（ConvGRU / 3D U-Net / U-TAE）。逐路径计数：ConvGRU 玉米 10/12、大豆 12/12 条路径为三模型最低；U-TAE 高于 3D U-Net 的路径玉米 7/12、大豆 5/12。

**口径与边界**：“排序一致”只指路径平均，不指每条路径。路径计数只作描述，不解释为独立重复试验。**本篇不作显著性结论**：Friedman、Wilcoxon–Holm 结果（`tables/table3_significance_tests.csv`）保留仅供追溯，因 12 条路径共享 4 个站点，不是独立样本（作者 2026-09-27 决定）。

**数据来源**：`results/summary/cross_site_crop_f1_summary.csv`（S2）；表末行“平均”（S4）

**状态**：Verified（2026-09-27）

## 历史 Claim 6（旧口径）：ConvGRU 平均 DR 最小，但 DR 较小不代表跨站绝对精度更高

**内容**：12 条路径 DR 的算术平均，玉米 3.05% / 4.18% / 4.21%，大豆 3.32% / 4.01% / 4.22%（ConvGRU / 3D U-Net / U-TAE），ConvGRU 最小；而其跨站 F1 路径平均最低（C5）。两种排序的参照不同：跨站 F1 直接比较实际精度，DR 以各模型自身在目标站的站内汇总 F1 为参照。U-TAE 与 ConvGRU 的差距：四站点站内汇总 F1 平均 2.84 / 3.09 个百分点，跨站 F1 路径平均 1.66 / 2.13 个百分点（玉米 / 大豆），缩小但未反转。

**口径与边界**：正文写“DR 较小不代表跨站绝对精度更高”，不写“DR 小是因为基准低”，也不写“ConvGRU 泛化能力更强”。每个目标站在 12 条路径中各出现 3 次，故路径平均的基准等于四站点站内平均，两者可比。

**数据来源**：`crop_f1_relative_degradation_36paths.csv`（S3）；`within_site_crop_f1.csv`（S1）；`cross_site_crop_f1_summary.csv`（S2）

**状态**：Verified（2026-09-27）

## 历史 Claim 7（旧口径）：DR 随源—目标组合变化，同一组合与迁移方向对不同模型的影响不一致

**内容**：
- 路径间跨度：ConvGRU 0.48%～8.17%（全部 72 个比例的最小、最大值均来自它），3D U-Net 2.54%～6.65%，U-TAE 2.30%～6.09%。
- 目标站一侧：按目标站对 3 条路径取平均，三模型玉米 DR 均以 C 最高（4.56% / 5.03% / 5.06%）；大豆无此一致性。
- 源站一侧：同一目标站的 DR 随源站变化，如 ConvGRU 大豆目标站 D：C→D 0.99%（5 次 0.86%～1.09%），B→D 8.17%（5 次 3.63%～11.95%）。
- 方向：B、D 之间，ConvGRU 玉米和大豆均 B→D 较大（大豆 8.17% / 3.75%），3D U-Net 均 D→B 较大（大豆 4.26% / 6.65%）。玉米两模型 5 次预测完全分开，大豆各有 1 次重叠。U-TAE 的方向差异主要由单次预测拉动，不作为方向证据。

**口径与边界**：描述性结果；不判断区域组合与模型的影响主次，不写“困难路径一致”。三模型之间 12 条路径的 DR 等级相关仅 −0.04～0.66（跨站 F1 为 0.73～0.84），困难路径在绝对 F1 上较一致，在 DR 上不一致。DR 较大的方向往往 5 次预测也最不稳定（大豆 F1 标准差最大三组：ConvGRU B→D 2.70、U-TAE B→D 2.20、3D U-Net D→B 1.91 个百分点），正文只写方向，不细排名次。U-TAE 以 A 为目标站时玉米 DR 偏高（A 站基准 96.23%），比例化不能代替绝对 F1。

**数据来源**：同 C4、C6；逐次核对用 `results/summary/cross_site_crop_f1_per_fold.csv`

**状态**：Verified（2026-09-27）

**正文位置**：C4—C7 归入 3.2 三段：第一段 C4（引表），第二段 C5、C6，第三段 C7（引图 4），用一句话衔接空间分析。

### 历史 3.2 取舍（2026-09-29，已由当前证据表替代）

- C4：只保留跨站 F1 范围、全部组合低于同一模型目标站当地训练基准，以及 A、C 站的表现差异；不从精度排序直接推断目标站分类难度，不声称 DR 消除了目标站差异。
- C5、C6：正文仅用 12 条路径的平均跨站 F1 与平均 DR 支撑“ConvGRU 跨站 F1 最低、平均 DR 最小；DR 较小不代表跨站绝对精度更高”。上列历史路径计数、站内外差距数字仅备查，不恢复到正文。D→B 大豆的 ConvGRU 与 3D U-Net 未舍入 F1 为 86.1899%、86.1929%，仅差 0.003 个百分点，表中均为 86.19%。
- C7：保留固定目标站 D、更换源站 C/B 的 ConvGRU 大豆例子，以及 B↔D 两模型方向不同的证据；均以各路径五次预测的 F1 均值计算 DR，仅描述该站点对，不推广为普遍规律或因果解释。上列玉米、大豆合并的 DR 范围及按目标站平均的 DR 数字仅备查。
- 三段不设三级标题，不改变完整表与六子图；3.3 正文与处理链不在本轮范围内。历史核查记录保留，本轮验证范围见 `verification/verification-report.md` 的 2026-09-29 记录。

## Claim 8：退化与目标站空间条件及源—目标站点差异的对应关系

**问题**（作者 2026-09-27 确定，覆盖全部站点与 12 条路径，不只围绕 C 站和 B、D 组合挑证据）：
1. 目标站在哪些空间条件下退化较大；
2. 同一目标站的退化为什么随源站变化——以对应关系表述，不写因果机制。美国站间迁移除空间格局外，物候、管理和影像条件也可能不同。

**当前证据**（2026-10-09）：逐条对照、数字来源与限制见 `results/summary/sec33_evidence_overview.md`，以该文件为 3.3 证据入口，本处只列要点。均为 derived / exploratory，正文未引用。

- C8a 碎片化与跨站新增（斑块尺度）：微小斑块（T1）本站漏分率高，但跨站漏分率增量 T2 高于 T1 65/72。碎片化对应“本来就难”，不对应跨站新增。
- C8b 位置与去向：主体斑块（T2）新增漏分率边界高于内部 62/72；只接触单一异类的边界像元上，错向对侧类别的跨站率更高（T2 143/144）。
- C8c 例外：B→D 大豆→玉米的新增延续到完整斑块内部，幅度随模型与来源改变。
- C8d 模型构成：按 12 路径等权，ConvGRU 大豆以 Recall 下降为主，3D U-Net、U-TAE 两作物以 Precision 下降为主。
- C8e 图块尺度的目标站条件：高 AREA_MN 组 F1 更高、ΔF1 多数更小（67/72），但 8/8 个站点—作物组合与类别组成共变。
- 问题 2（源站依赖）：现有空间特征不能解释。源站组成排序与定向增量多为反向（其他→玉米 10/12）；代表性检验和路径差值分解只有 2026-10-06 预检，未落盘，不得引用。

**数据**：
- 单斑块：`legacy/experiment-results/label/` 下四份 FRAGSTATS `.patch` 与 `*_id8.tif`，已转存 `results/raw/sec33_reference_patch_types/`。主指标 AREA、SHAPE、ENN；GYRATE、CONTIG 只作描述；本批无 FRAC、PROX、CAI 输出。
- 图块级与站点级：沿用下方历史记录所列外部底表。
- 预测：12 份本站 OOF 与 180 次跨站保存预测，均未重新推理。

**状态**：各轮派生计数、身份连接与闭合 Verified（以各轮核查记录为准）；历史距离数组生成、FRAGSTATS 原工程配置 Partially verified。正文未写，结构待作者按总览第 5 节的待定事项确定。

**正文位置**：3.3，不设第三级标题。

### C8 历史记录（2026-09-26—29，旧口径）

**数据**（当时记为已生成、未入库）：
- 图块级：`D:/cross_site_all_20260916/paper_tables/Patch级空间误差底表/` 下 `patch_spatial_features.csv`（1600）、`within_patch_oof.csv`（4800）、`cross_patch_fold.csv`（72000）、`cross_patch_summary.csv`（14400）；QC 报告 `patch_spatial_qc.md`（2026-09-18 passed）。
- 站点级：`D:/label/fragstats_results/完整标签景观级指标.csv`、`完整标签类别级指标.csv`（2023 年完整标签，ED、PD、AREA_MN、AI 已从 GeoTIFF 复算）。

**已核**（2026-09-26）：行数与键唯一；站内图块混淆矩阵之和 = 12 组汇总混淆矩阵；跨站图块混淆矩阵之和 = 180 个原始混淆矩阵；NA 未补零。**未核**：未从标签 GeoTIFF 重算 ED、AREA_MN、AI。

**口径**：ED 为图块景观级，AREA_MN、AI 为类别级，均以单个 128×128 图块为独立景观计算，不能称为整站景观指标；真实缺类与不可计算值保留 NA。按空间特征分组时先汇总组内混淆矩阵再算类别 F1；跨站逐次计算后汇总 5 次结果，站内以同组图块为参照；不平均图块 F1。`cross_patch_summary.csv` 的 `delta_error_rate` 是三分类错误率之差，不是 F1 退化；其 QC 中的 Crop-mIoU 分组口径不沿用。

**当时状态**：Partially verified；分组 F1/DR 与边界探索已入库，见 `results/summary/sec33_exploration/`。旧 DR 不直接作为当前差值结果。

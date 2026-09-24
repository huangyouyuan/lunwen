# 论文核心论点

每条论点必须有数据支撑。数字来源一律为 `results/summary/`，口径见 `plan/experiment-protocol.md`。每条 claim 标注它经过数据处理链的哪几步（S1–S5），便于回溯。

## 数据处理链

原始实验输出不入库；下列脚本按顺序运行即可从原始输出完整重建 `results/` 与 `tables/`。一键：`scripts/run_all_updates.ps1`。

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
- 表3：从 S2 的 180 行按 (source, target, model) 先求 5 次均值，得 12 × 3 矩阵；对每种作物做 Friedman；三对 Wilcoxon 符号秩；Holm step-down（p 升序，第 k 个校正 p = (m−k)·p 取累积最大，首次不显著后其余不再拒绝）。检验对象是跨站 F1，不是 ΔF1。

**输出**：`tables/table1_within_site_baseline.csv`、`table1b_within_site_fold_stability.csv`、`table2_cross_site_f1_12paths.csv`、`table2_cross_site_f1_12paths_rows.tex`、`table2_cross_site_summary.csv`、`table3_significance_tests.csv`。正文通过 `\input` 读取脚本生成的表体，不重复维护数字。

### S5 图

**热力图**：`scripts/plot_degradation_heatmap.py 1`，输入 S3 的 `crop_f1_relative_degradation_36paths.csv`。每个 (model, crop) 把 12 条路径的相对退化比例 pivot 成 4×4（行源站、列目标站，A–D），对角线置 NaN；6 子图按两行三列排列，上玉米、下大豆，图框各 3.8 cm，共用下方横向色标 0–9%，LaTeX 标签“泛化退化比例/%”。每子图一个 PDF + 色标 PDF，输出 `figures/results/fig_degradation_heatmap_{a..f,cbar}.pdf`。

**站内条形图**：`scripts/plot_within_site_f1.py`，输入 S1 的 `within_site_crop_f1.csv`。玉米、大豆各一子图上下排，横向条形：纵轴站点 A–D、每站三模型条，横轴 F1 换算为百分数、条末端标两位小数。每子图一个 PDF，输出 `figures/results/fig_within_site_f1_{a,b}.pdf`。

**D 站分类结果图**：`scripts/plot_within_site_map_D.py`，输入 `D:/20il/2023{model}ilresults/summary/maps/` 的 `reference.tif` 与 `oof_prediction.tif`（五折拼接，每图块预测来自未训练过它的模型；断言三模型 reference sha256 一致）。上行全站标红框，下行红框放大；窗口取图块网格 (13,8) 起 2×2，按"真实玉米/大豆像元错误率差 + 类别边界带错误率差（ConvGRU 相对另两模型均值）"最大选出。每子图一个 PDF，输出 `figures/results/fig_within_site_map_D_{a..h}.pdf`。

图题、子图题、图例均为 LaTeX 文本（subcaption、\modellegend / \classlegend），图片里只有图框、刻度、数值、轴标签。

### 补充体系（不进正文）

`results/summary/generalization_degradation_36paths.csv`、`within_site_oof_baseline.csv`、`model_significance_analysis.csv` 直接复制自 `legacy/experiment-results/paper_tables/`，是实验侧生成的 Crop-mIoU 表；`results/processed/generalization_analysis.csv` 由 `scripts/analyze_generalization_36paths.py` 从前者派生。类别顺序与主线一致，可作补充材料核对。

---

## Claim 1：站内三模型排序为 U-TAE ≈ 3D U-Net > ConvGRU，玉米略易于大豆

**内容**：站内 OOF pooled 玉米 F1 为 0.915 / 0.941 / 0.944（ConvGRU / 3D U-Net / U-TAE），大豆 F1 为 0.906 / 0.934 / 0.937，OA 为 0.896 / 0.928 / 0.931。3D U-Net 与 U-TAE 差距 < 0.3 pp，二者高于 ConvGRU 约 2.6–3.5 pp。同一模型玉米 F1 高于大豆 0.6–0.9 pp。

**数据来源**：`results/summary/within_site_crop_f1.csv`（S1 步骤 1–3；模型均值为四站汇总值的算术平均，见 S4 表1 Mean 列）；图 `figures/results/fig_within_site_f1_{a,b}.pdf`（S5）

**状态**：已验证（2026-09-18）；正文 3.1 已写（2026-09-19），范围 90.98–96.23 / 89.55–95.89、C 站最大差 1.61/1.50、D 站 3.58/3.98 均核对

## Claim 2：站内训练稳定，折间波动不超过 1 pp

**内容**：12 组站内实验五折标准差：玉米 F1 0.12–0.73 pp，大豆 F1 0.06–0.96 pp，OA 0.13–0.86 pp。最大值均出现在 3D U-Net 的 B 站。

**数据来源**：`results/summary/within_site_crop_f1_fold_stats.csv`（S1 步骤 4）

**状态**：已验证（2026-09-18）

## Claim 3：站点难度差异稳定，C 站最难、A 站最易

**内容**：三模型在 C 站 OA 均最低（0.891 / 0.910 / 0.912），在 A 站均最高（0.901 / 0.937 / 0.948）。A 与 C 的 OA 差距为 1.0 / 2.7 / 3.7 pp，与 ConvGRU 相对另两模型的差距量级相当，大于 3D U-Net 与 U-TAE 之间的差距。

**数据来源**：`results/summary/within_site_crop_f1.csv`（S1 步骤 1–3）

**状态**：已验证（2026-09-18）；与景观特征的对应关系待 3.3

## Claim 4：跨站应用后全部路径均出现退化，模型排序不变

**内容**：36 条路径 × 2 作物共 72 个 ΔF1 全部为正，范围 0.44–7.39 pp。跨站玉米 F1 均值 0.887 / 0.902 / 0.904，大豆 0.876 / 0.897 / 0.898，排序与站内一致。

**图 4 相对比例**：72 个值全部为正，范围 0.48%～8.17%，由 `crop_f1_relative_degradation_36paths.csv` 核对（Verified，2026-09-23）。

**数据来源**：`results/summary/crop_f1_degradation_36paths.csv`（S3）；跨站均值为 S4 表2 口径（12 条路径均值的平均）

**状态**：已验证（2026-09-18）

## Claim 5：ConvGRU 显著弱于 3D U-Net 和 U-TAE，后两者无显著差异，两作物一致

**内容**：以 12 条路径的五折均值为配对单位，跨站玉米 F1 Friedman χ² = 12.67（p = 1.8×10⁻³），大豆 χ² = 18.17（p = 1.1×10⁻⁴）。Holm 校正后 p：玉米 ConvGRU–3D U-Net 0.0137、ConvGRU–U-TAE 0.0029、3D U-Net–U-TAE 0.5693；大豆 0.0015、0.0015、0.9097。

**数据来源**：`tables/table3_significance_tests.csv`（S4，从 S2 的 per-fold 文件出发）

**状态**：已验证（2026-09-18）；12 条路径共享 4 个站点，结论限定在本文四站范围

## Claim 6：ConvGRU 退化幅度最小，但不代表泛化更好

**内容**：平均退化玉米 2.79 / 3.93 / 3.97 pp，大豆 3.00 / 3.74 / 3.96 pp，ConvGRU 最小；但其站内基准最低（Claim 1），跨站绝对 F1 仍最低（Claim 4）。退化幅度必须与基准一起解读。

**图 4 相对比例**：12 条路径比例的算术平均，玉米 3.05% / 4.18% / 4.21%，大豆 3.32% / 4.01% / 4.22%（ConvGRU / 3D U-Net / U-TAE），ConvGRU 仍最小。来源 `crop_f1_relative_degradation_36paths.csv`（Verified，2026-09-23）。

**数据来源**：`tables/table2_cross_site_summary.csv`（S4，由 S3 汇总）

**状态**：已验证（2026-09-18）

## Claim 7：退化随源—目标组合变化，不同模型对迁移方向的响应存在差异

**内容**：在本文四站点、不微调的跨站实验中，泛化退化比例随源—目标组合变化，迁移方向改变时，不同模型的退化比例不一定同向变化。以大豆 B↔D 为例，ConvGRU 在 B→D、D→B 上的退化比例分别为 8.17%、3.75%，前者更大；3D U-Net 分别为 4.26%、6.65%，后者更大。这组对照支持不同模型对迁移方向的响应存在差异。

**口径与边界**：每条路径以同一模型在目标站的站内汇总 F1 为基准，跨站 F1 为 5 次完整目标站预测的算术平均；退化比例为二者之差除以该基准，再乘 100%。反向迁移时目标站与基准随之改变。上述比较是描述性结果，不能据此确定区域组合与模型的影响主次，也不预设三模型的困难路径排序一致；图 4 的路径排序须按比例核对，不沿用百分点差值排序。

**数据来源**：`results/summary/within_site_crop_f1.csv` 与 `results/summary/cross_site_crop_f1_summary.csv`，经 `scripts/calculate_crop_f1_degradation.py` 的 `calculate_degradation()`、`calculate_relative_degradation()` 现算，并与 `results/summary/crop_f1_relative_degradation_36paths.csv` 核对；图 `figures/results/fig_degradation_heatmap_{a..f}.pdf` 使用同一比例文件（S1、S2→S3→S5）。

**状态**：Verified（2026-09-24）；72 个比例和 72 个百分点差值均与上述脚本现算结果一致（CSV 保留 6 位小数）；本条结论限定于描述性路径差异。

**正文位置**：C4—C7 均归入 3.2；连续论述跨站绝对 F1、平均退化和不同模型对源—目标组合及迁移方向的响应差异，六子图热力图作为路径层证据。

## Claim 8：区域与路径差异可由地物组成和景观配置解释

**内容**：待站点级与 Patch 级空间特征数据。

**数据来源**：待补；处理链尚未建立

**状态**：未验证

**正文位置**：3.3；以地物占比、景观指标和分组分类结果解释空间条件，不再设置第三级标题。

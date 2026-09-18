# 论文核心论点

每条论点必须有数据支撑。数字来源一律为 `results/summary/`，口径见 `plan/experiment-protocol.md`。

## Claim 1：站内三模型排序为 U-TAE ≈ 3D U-Net > ConvGRU，玉米略易于大豆

**内容**：站内 OOF pooled 玉米 F1 为 0.915 / 0.941 / 0.944（ConvGRU / 3D U-Net / U-TAE），大豆 F1 为 0.906 / 0.934 / 0.937，OA 为 0.896 / 0.928 / 0.931。3D U-Net 与 U-TAE 差距 < 0.3 pp，二者高于 ConvGRU 约 2.6–3.5 pp。同一模型玉米 F1 高于大豆 0.6–0.9 pp。

**数据来源**：`results/summary/within_site_crop_f1.csv`

**状态**：已验证（2026-09-18）

## Claim 2：站内训练稳定，折间波动不超过 1 pp

**内容**：12 组站内实验五折标准差：玉米 F1 0.12–0.73 pp，大豆 F1 0.06–0.96 pp，OA 0.13–0.86 pp。最大值均出现在 3D U-Net 的 B 站。

**数据来源**：`results/summary/within_site_crop_f1_fold_stats.csv`

**状态**：已验证（2026-09-18）

## Claim 3：站点难度差异稳定，C 站最难、A 站最易

**内容**：三模型在 C 站 OA 均最低（0.891 / 0.910 / 0.912），在 A 站均最高（0.901 / 0.937 / 0.948）。A 与 C 的 OA 差距为 1.0 / 2.7 / 3.7 pp，与 ConvGRU 相对另两模型的差距量级相当，大于 3D U-Net 与 U-TAE 之间的差距。

**数据来源**：`results/summary/within_site_crop_f1.csv`

**状态**：已验证（2026-09-18）；与景观特征的对应关系待 3.3.2

## Claim 4：跨站应用后全部路径均出现退化，模型排序不变

**内容**：36 条路径 × 2 作物共 72 个 ΔF1 全部为正，范围 0.44–7.39 pp。跨站玉米 F1 均值 0.887 / 0.902 / 0.904，大豆 0.876 / 0.897 / 0.898，排序与站内一致。

**数据来源**：`results/summary/crop_f1_degradation_36paths.csv`、`cross_site_crop_f1_summary.csv`

**状态**：已验证（2026-09-18）

## Claim 5：ConvGRU 显著弱于 3D U-Net 和 U-TAE，后两者无显著差异，两作物一致

**内容**：以 12 条路径的五折均值为配对单位，玉米 F1 Friedman χ² = 12.67（p = 1.8×10⁻³），大豆 χ² = 18.17（p = 1.1×10⁻⁴）。Holm 校正后 ConvGRU 与另两模型的差异均显著，3D U-Net 与 U-TAE 不显著。

**数据来源**：`tables/table3_significance_tests.csv`

**状态**：已验证（2026-09-18）

## Claim 6：ConvGRU 退化幅度最小，但不代表泛化更好

**内容**：平均退化玉米 2.79 / 3.93 / 3.97 pp，大豆 3.00 / 3.74 / 3.96 pp，ConvGRU 最小；但其站内基准最低，跨站绝对 F1 仍最低。退化幅度必须与基准一起解读。

**数据来源**：`tables/table2_cross_site_summary.csv`

**状态**：已验证（2026-09-18）

## Claim 7：路径难度主要由区域组合决定，涉及 B 站的路径最难且存在方向不对称

**内容**：玉米退化前 5 条路径为 D→B（3D U-Net，5.85）、B→C（ConvGRU，5.30）、B→D（ConvGRU，5.26）、B→C（U-TAE，4.89）、A→C（3D U-Net，4.84）；大豆前 5 条为 B→D（ConvGRU，7.39）、D→B（3D U-Net，6.14）、B→C（ConvGRU，6.00）、B→D（U-TAE，5.74）、C→A（U-TAE，4.79）。ConvGRU 大豆 B→D 为 7.39 pp，D→B 仅 3.36 pp。三模型的困难路径高度重合。

**数据来源**：`results/summary/crop_f1_degradation_36paths.csv`；图 `figures/results/fig_degradation_heatmap.png`

**状态**：已验证（2026-09-18）

## Claim 8：区域与路径差异可由地物组成和景观配置解释

**内容**：待站点级与 Patch 级空间特征数据。

**数据来源**：待补

**状态**：未验证

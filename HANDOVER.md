# 论文工程交接文档

## 一、论文方向

### 研究问题

**时空深度学习模型在跨区域作物遥感分类中的空间泛化能力差异**

核心问题：
- 不同时空建模范式（时序注意力 vs 3D卷积 vs 循环网络）的跨站点泛化性能是否存在显著差异？
- 为什么同一模型在玉米和大豆上的泛化退化幅度不同？
- 空间景观特征（地块破碎度、边界复杂度、作物占比）如何影响模型的泛化能力？

### 技术路线

**模型**：
- U-TAE（时序自注意力 + U-Net）
- 3D U-Net（3D卷积时空联合建模）
- ConvGRU（卷积循环单元）

**数据**：
- HLS（Harmonized Landsat Sentinel-2）30 m 多时相遥感
- 4 个站点（A/B/C/D；A=iw，B=iw2，C=ida，D=il）× 玉米、大豆、其他地类
- 2023 年生长季 DOY 116–266，5 天间隔 31 个时间步

**实验设计**：
1. **站内基准**：各站点 5-fold cross-validation（OOF pooled 混淆矩阵）
2. **跨站泛化**：12 条迁移路径（源站 → 目标站，排除自身），每条 5 个 checkpoint
3. **泛化退化**：ΔF1 = F1_站内 - F1_跨站
4. **显著性检验**：Friedman + Wilcoxon 配对 + Holm 校正（12 条路径为配对单位）

**主要指标**：
- **主指标**：玉米 F1、大豆 F1（分别报告）
- **辅助指标**：Overall Accuracy（站内表使用）
- **泛化评价**：ΔF1（百分点）、5 个 checkpoint 的稳定性（std）

---

## 二、代码体系历史变化

### 阶段 1：原始实验输出（数据年份 2023，实验运行 2026-09）

**原始结果目录**：
- 站内：`D:/20{site}/2023…results/summary/metrics_summary.csv`（Windows 本地，未入库）
- 跨站：`legacy/experiment-results/cross_site_all_20260916/*/metrics_summary.csv`（git 排除）

**混淆矩阵格式**：
- 列名：`cm_gt_X_pred_Y`（X, Y ∈ {corn, other, soybean}）
- 站内：5 行 `fold` + 1 行 `oof_pooled`
- 跨站：5 行 `fold`（每个 checkpoint 一行）

**问题**：
- 站内、跨站导出脚本曾采用不同类别顺序
- 缺少标准化的 F1 计算流程

---

### 阶段 2：数据标准化（2026-09）

**目标**：建立可复现的数据处理流水线

#### 2.1 类别顺序统一

**约定**：corn=0, other=1, soybean=2

**原因**：
- 站内实验最早采用此顺序
- 跨站实验初期采用不同顺序（corn=0, soybean=1, other=2）
- 2026-09-18 统一为站内顺序

**影响脚本**：
- `scripts/calculate_crop_f1.py`（站内）
- `scripts/extract_cross_site_cm.py`（跨站，已修正）

#### 2.2 站内数据处理

**脚本**：`scripts/calculate_crop_f1.py`

**输入**（Windows 本地，12 个目录）：
```
D:/20{site}/2023{model}{site}results/summary/metrics_summary.csv
D:/20{site}/2023{site}{model}results/summary/metrics_summary.csv   # iw/iw2 站的目录命名不同
```
每个文件含 5 行 `fold`（各测试折 CM）+ 1 行 `oof_pooled`（五折汇总 CM）。脚本校验 pooled CM 等于五折 CM 之和。

**输出**：
- `results/raw/within_site_confusion_matrices.csv`（12 组 × 5 折 + pooled）
- `results/summary/within_site_crop_f1.csv`（OOF pooled 玉米F1 / 大豆F1 / OA）
- `results/summary/within_site_crop_f1_fold_stats.csv`（五折 mean ± std，用于表1b 稳定性）

**关键修正**（2026-09-18）：
- OA 计算从"全矩阵和÷有效像元"修正为"对角线和÷有效像元"
- 修正前所有 OA = 100%，修正后范围 89.10%–94.82%
- 不再依赖 `legacy/.../within_site_oof_baseline.csv` 中转，直接从原始五折 CM 计算

#### 2.3 跨站数据处理

**脚本**：`scripts/extract_cross_site_cm.py`

**输入**：
```
legacy/experiment-results/cross_site_all_20260916/
└── {model}__{source}_2023__{digest}/
    └── {target}_2023/metrics_summary.csv     # 5 行 fold + cv_mean + cv_std
```
36 个 (model, source, target) 组合，各 5 行 fold。

**输出**：
- `results/raw/cross_site_confusion_matrices.csv`（36 条路径 × 5 fold = 180 行原始 CM）
- `results/summary/cross_site_crop_f1_per_fold.csv`（180 行各折 F1）
- `results/summary/cross_site_crop_f1_summary.csv`（36 条路径 mean ± std）

**关键修正**（2026-09-18）：
- 类别映射从 `corn=0, soybean=1, other=2` 改为 `corn=0, other=1, soybean=2`
- 修正前"大豆"列实为其它类，产生虚假的负退化；修正后 72 个退化值全为正

#### 2.4 泛化退化计算

**脚本**：`scripts/calculate_crop_f1_degradation.py`

**输入**：
- `results/summary/within_site_crop_f1.csv`
- `results/summary/cross_site_crop_f1_summary.csv`

**输出**：
- `results/summary/crop_f1_degradation_36paths.csv`

**计算逻辑**：
```python
ΔF1_corn = 100 × (F1_corn_站内OOF - F1_corn_跨站平均)
ΔF1_soybean = 100 × (F1_soybean_站内OOF - F1_soybean_跨站平均)
```

**关键修正**（2026-09-18）：
- 修正类别对应后，所有退化值变为正值（0.44–7.39 pp）

---

### 阶段 3：表格生成自动化（2026-09）

**脚本**：`scripts/generate_core_tables.py`

#### 表1：站内分类性能

**表1（OOF pooled）**：
```
行                     A       B       C       D     Mean
ConvGRU (Corn F1)      ...
ConvGRU (Soybean F1)   ...
ConvGRU (OA)           ...
3D U-Net (...)         ...
U-TAE (...)            ...
```

**表1b（五折稳定性，mean±std）**：同样布局，单元格为各测试折指标的均值±标准差，用于正文中"折间稳定性"论述。OOF pooled 与五折均值口径不同，不可混用。

#### 表2：跨站分类性能汇总

**布局**：模型 × 作物 6 行；列为跨站 F1 mean±std（该模型 12 条路径的路径均值统计）、ΔF1 mean±std（pp）。

#### 表3：显著性检验

**检验对象**：跨站玉米 F1、跨站大豆 F1（不是 ΔF1），分别检验。

**配对单位**：12 条有向迁移路径，每条取 5 个 checkpoint 的均值 → `data_matrix.shape == (12, 3)`。

**修正记录**（2026-09-18）：
- 修正前把 12 路径 × 5 checkpoint 当成 60 个配对样本；同一路径的 5 次结果来自同一训练过程的不同折，不构成独立配对
- Holm 由"逐个比阈值"改为标准 step-down：p 升序，校正 p = (m−k)·p 取累积最大，首次不显著后其余不再拒绝；表中报告 p_holm
- 12 条路径共享 4 个站点，作为配对单位可用，但不解释为完全独立的区域样本

---

## 三、当前代码体系架构

### 数据流

```
原始实验结果（legacy/）
    ↓
提取与标准化（scripts/extract_*.py, calculate_*.py）
    ↓
标准数据（results/summary/）
    ↓
表格生成（scripts/generate_core_tables.py）
    ↓
LaTeX 表格（tables/*.csv）
    ↓
论文正文引用（sections/04_results.tex）
```

### 核心约定

#### Source of Truth 分层

1. **科学数字**：`results/summary/`（最高优先级）
2. **实验协议**：`plan/experiment-protocol.md`
3. **写作模式**：`plan/style-guide.md`
4. **格式规范**：`plan/format-spec.md`（旧 Word 为最终裁决）
5. **文献元数据**：`bibliography/references.bib`
6. **当前正文**：`sections/*.tex`

#### 类别顺序

**全局约定**：corn=0, other=1, soybean=2

**验证方法**：
```python
# 正确的 F1 计算
class_names = ['corn', 'other', 'soybean']
for i, name in enumerate(class_names):
    tp = cm[i, i]
    ...
```

#### 指标约定

**主指标**：
- 玉米 F1
- 大豆 F1

**辅助指标**：
- Overall Accuracy（仅站内表）

**不再使用**：
- Crop-mIoU（方法章节已删除）
- mIoU（全局指标，不区分作物）

---

## 四、已知问题与待办

### 已修正（2026-09-18）

- ✅ 站内 OA 计算错误（全矩阵和 → 对角线和）
- ✅ 跨站类别顺序不一致（已统一为 corn/other/soybean）
- ✅ 显著性检验配对单位错误（60 → 12）；Holm 改为标准 step-down
- ✅ 方法章节主指标过时（Crop-mIoU → 分别报告玉米/大豆 F1）
- ✅ 结果章节、results-map、claims 中基于错误类别的结论已清除；`crop_f1_analysis_summary.md` 已删除

### 待补充

1. **方法章节待添加**
   - 空间景观特征提取方法（3.3 用）

2. **Results 章节待填充**
   - 3.1 站内分类结果（表1 + 表1b 已就绪）
   - 3.2 跨站分类结果（表2 已就绪）
   - 3.2.3 显著性检验（表3 已按 12 路径重算）
   - 3.3.1 源—目标热力图（图已生成）
   - 3.3.2 空间特征关联（暂无数据）

---

## 五、执行脚本流程

### 完整更新流程

```powershell
# 方法1：使用自动化脚本
.\scripts\run_all_updates.ps1

# 方法2：手动逐步执行
python scripts/calculate_crop_f1.py
python scripts/extract_cross_site_cm.py
python scripts/calculate_crop_f1_degradation.py
python scripts/generate_core_tables.py
```

### 验证检查点

执行后检查：
1. **表1 OA 列**：范围应为 89%–95%，不应全为 100%
2. **表2 大豆列**：值应合理（不应异常高或异常低）
3. **退化表**：36 条路径 × 2 作物 = 72 个退化值，全部应为正值（0.44–7.39 pp）
4. **表3显著性**：检验应基于 12 个路径均值，不是 180 个样本

---

## 六、关键设计决策记录

### 为什么分别报告玉米和大豆F1？

**原因**：
1. 论文的分类对象是玉米和大豆，制图应用关心各作物精度而非平均值
2. 单一合成指标（mIoU / Crop-mIoU）掩盖类别间差异，且会把"其它"类混入
3. 类别顺序事故表明：只有分类别报告才能在数据层面暴露错误

### 为什么不使用 mIoU？

**原因**：
1. mIoU 包含"其它"类，而本研究不关注其它类的识别
2. "其它"在各站点的地类构成不一致
3. F1 更符合作物识别的评价习惯

### 为什么显著性检验用 12 个配对样本而非 60 个？

**原因**：
1. 检验对象是模型在一条迁移路径上的跨站 F1；路径是设计单元
2. 同一路径的 5 个 checkpoint 来自同一站点的 5 个训练折，是重复测量而非新的路径
3. 先对 5 次求均值消除 checkpoint 随机性，再以 12 条路径配对比较模型
4. 12 条路径共享 4 个站点，并非完全独立的区域样本；结论限定在本文四站范围内

### 为什么类别顺序统一为 corn/other/soybean？

**技术原因**：
- 站内实验最早采用此顺序，已有大量依赖代码
- 混淆矩阵索引 `cm[i, j]` 必须全局一致，否则 F1 计算错误

**科学原因**：
- 类别顺序本身不影响模型性能
- 但不一致的顺序会导致后处理指标错误（本次事故：大豆列实为其它类）

---

## 七、后续工作建议

### 短期（第 3 章正文）

1. 写 3.1、3.2 正文（表1、1b、2、3 已就绪）
2. 定位 3.3.2 的站点级景观指标与 Patch 级四张表
3. 重编译 main.tex，更新 verification-report

### 中期

1. 重写 2.1 三模型描述
2. 引言 evidence-map 与 blueprint
3. 3.3.2 空间特征与退化关联分析（按特征分组汇总 CM）

### 长期（投稿阶段）

1. 内容冻结后 LaTeX → Word
2. 中英文摘要
3. 全文一致性检查（术语、引用、图表编号）

---

## 八、紧急联系信息

### 数据问题

- **站内原始数据**：`D:/20{ida,il,iw,iw2}/2023…results/summary/metrics_summary.csv`
- **跨站原始数据**：`legacy/experiment-results/cross_site_all_20260916/`
- **系统文档**：状态看 `plan/progress.md`，结论看 `plan/claims.md`，验证看 `verification/verification-report.md`——本文件只是入口，不重复维护数字
- **类别映射错误**：检查 `cm_gt_X_pred_Y` 列是否对应正确的 `cm[i, j]`

### 脚本问题

- **OA 计算**：必须使用 `np.trace(cm) / cm.sum()`，不是 `cm.sum()`
- **显著性检验**：先对每条路径 5 次求均值，`data_matrix.shape` 必须是 `(12, 3)`
- **Holm**：step-down，首次不显著后停止拒绝
- **类别顺序**：全局检查 `CLASS_ORDER = ['corn', 'other', 'soybean']`

### 表格问题

- **表1**：OA 范围 89–95%
- **表2**：ΔF1 全为正
- **表3**：n = 12，报告 p_holm

---

**最后更新**：2026-09-18
**更新内容**：类别顺序统一、OA 修正、Holm step-down、检验对象明确为跨站 F1、清除旧结论文档

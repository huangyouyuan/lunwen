# Table Schema

正式表格定义，制作前必须在此定义。

## 表 1 四个研究站点景观格局指数

**Purpose**：展示 4 站点空间异质性梯度，为泛化结果分析提供依据。

**Source**：CDL 2021–2024 + FRAGSTATS 4.3

**Columns**：站点 | 地物类型 | PD | AREA_MN | AI | ED

**行结构**：每站点含玉米、大豆、其它 3 行 + 景观级别指标

**Primary metric**：ED（边界密度）

**Status**：旧稿已有（Table 0, 14×6），需数据验证

---

## 表 2 模型在四个研究站点的总体分类精度

**Purpose**：展示三种模型各站点站内分类性能。

**Source**：results/summary/ — 待建立

**Columns**：站点 | 模型(3D U-Net: mIoU/UA/PA) | 模型(U-TAE: mIoU/UA/PA) | 模型(ConvGRU: mIoU/UA/PA)

**行结构**：每站点 1 行 + 平均行

**Primary metric**：mIoU

**Supporting metrics**：Macro UA, Macro PA

**Status**：旧稿已有（Table 9, 7×12），需数据验证

---

## 表 3 三种模型在空间泛化中的精度退化

**Purpose**：比较模型跨站点后相对于站内性能的退化程度。

**Source**：results/summary/ — 待建立

**Columns**：迁移路径(X→Y) | 3D U-Net(ΔmIoU/ΔUA/ΔPA) | U-TAE(ΔmIoU/ΔUA/ΔPA) | ConvGRU(ΔmIoU/ΔUA/ΔPA)

**行结构**：12 条迁移路径 + 各源站点平均 + 总平均

**Primary metric**：ΔmIoU

**Derived fields**：ΔmIoU = within-site mIoU − cross-site mIoU

**Status**：旧稿已有（Table 11, 15×10），需数据验证

---

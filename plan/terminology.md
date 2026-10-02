# 术语表

统一全文用语，避免同一概念出现多种表述。

## 站点 ID 映射

| 论文代号 | 数据集 ID | 州 |
|----------|-----------|-----|
| A | iw_2023 | 爱荷华州 |
| B | iw2_2023 | 爱荷华州 |
| C | ida_2023 | 印第安纳州 |
| D | il_2023 | 伊利诺伊州 |

州别依据研究区 SHP 与标签 GeoTIFF（EPSG:5070）叠加美国人口普查局 2023 州界核实，四站均不跨州（2026-09-27，见 `plan/experiment-protocol.md`）。

论文正文使用 A/B/C/D，代码和数据目录使用 iw2/iw/ida/il。

## 模型名称

| 规范写法 | 禁止写法 | 说明 |
|----------|----------|------|
| U-TAE | UTAE, U_TAE | 保持连字符 |
| 3D U-Net | 3D-UNet, 3DUNet, 3D Unet | 统一大小写 |
| ConvGRU | Conv-GRU, CGRU | 不拆分 |
| L-TAE | LTAE | Lightweight Temporal Attention Encoder |

## 模型范式描述

| 中文术语 | 英文 | 说明 |
|----------|------|------|
| 时间注意力 | temporal attention | U-TAE 的核心机制 |
| 三维卷积 | 3D convolution | 3D U-Net 的核心机制 |
| 递归门控 | recurrent gating | ConvGRU 的核心机制 |
| 时空深度学习模型 | spatiotemporal deep learning model | 三种模型的统称 |

## 实验术语

| 中文术语 | 英文 | 说明 |
|----------|------|------|
| 站内分类 | within-site classification | 在同一站点训练和测试 |
| 跨站点空间泛化 | cross-site spatial generalization | 在源站点训练，直接迁移至目标站点；正文可简称"跨站" |
| 泛化退化 / 精度退化 | generalization degradation | 跨站精度相对站内精度的降幅 |
| 迁移路径 | transfer path | 从源站点到目标站点的方向，记为 A→B；四站共 12 条有向路径，与三模型组合为 36 个模型—路径组合，不称“36 条路径” |
| 源站点 / 源站 | source site | 模型训练所在站点 |
| 目标站点 / 目标站 | target site | 模型直接应用的站点 |
| 汇总精度 | oof_pooled | 5 个测试折混淆矩阵逐元素相加后计算的指标；站内基准与退化的口径；正文不用 OOF 缩写 |
| 五折均值 / 折间标准差 | cv_mean / cv_std | 各测试折指标的算术均值与标准差；只用于说明训练稳定性 |
| 5 折交叉验证 | 5-fold cross-validation | 3 训练 + 1 验证 + 1 测试 |
| 折 | fold | 正文不用 fold |
| 模型（某折的） | checkpoint | 正文写"每折一个模型"或"5 个模型"，不用 checkpoint |

## 数据术语

| 中文术语 | 英文 | 说明 |
|----------|------|------|
| 多时相遥感影像 | multi-temporal remote sensing imagery | — |
| HLS | Harmonized Landsat and Sentinel-2 | 全文首次出现需全称 |
| CDL | Cropland Data Layer | 全文首次出现需全称 |
| 时间步 | time step | 时间序列中的单个观测 |
| 生育阶段 | growth stage / phenological stage | — |
| 图块 | patch | 128×128 像素的样本单元 |

## 分类类别

| 中文 | 英文 | 模型标签值 | CDL 源标签值 |
|------|------|-----------|-------------|
| 玉米 | Corn | 0 | 1 |
| 其它 | Others | 1 | 2 |
| 大豆 | Soybean | 2 | 3 |

## 指标

| 缩写 | 全称 | 中文 | 地位 | 公式角标 |
|------|------|------|------|----------|
| F1_corn / F1_soybean | 玉米 F1 / 大豆 F1 | 玉米 F1 分数、大豆 F1 分数 | 主指标，分别报告 | $F1_{\text{玉米}}$、$F1_{\text{大豆}}$ |
| OA | Overall Accuracy | 总体精度 | 辅助 | OA |
| ΔF1 | F1 difference | F1 差值 | 正文及图 4 | 同模型目标站站内汇总 F1 减跨站五次均值；原尺度、两位显示；不乘 100、不除基准 |
| DR | relative generalization degradation | 泛化退化比例（%） | 仅历史追溯，不作当前正文指标 | 历史定义为 F1 差值除以目标站站内基准再乘 100%；旧文件及冻结探索协议保留，不改名充当 ΔF1 |
| P / R | Precision / Recall | 精确率 / 召回率 | 定义 F1 用 | $P_i$、$R_i$ |
| Crop-mIoU | (IoU_corn + IoU_soybean)/2 | 作物平均交并比 | 补充 | — |
| mIoU | mean Intersection over Union | 平均交并比（三类） | 补充 | — |
| UA / PA | User's / Producer's Accuracy | 用户精度 / 制图精度 | 补充 | — |
| Kappa | Kappa coefficient | Kappa 系数 | 补充 | — |

公式角标一律中文，不用 corn / within / cross。

## 景观指标

| 缩写 | 英文 | 中文 | 说明 |
|------|------|------|------|
| ED | Edge Density | 边界密度 | — |
| PD | Patch Density | 斑块密度 | — |
| AREA_MN | Mean Patch Area | 平均斑块面积 | **不写"平均田块面积""平均地块面积"**——FRAGSTATS 斑块是标签上的同类连通区，不等于实际农业地块 |
| AI | Aggregation Index | 聚集度指数 | — |

"斑块"（patch，景观生态）与"图块"（patch，128×128 样本单元）是两个概念，正文分别用这两个词，不混用。

## 标点与数字规范

- 中文语境使用中文标点（，。；：""）
- 数字与单位之间空半角空格（30 m、5 天）
- 百分号前不空格（89.53%）
- 区间使用短横线（DOY 116–266）

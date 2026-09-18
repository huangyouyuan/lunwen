# 术语表

统一全文用语，避免同一概念出现多种表述。

## 站点 ID 映射

| 论文代号 | 数据集 ID | 州 |
|----------|-----------|-----|
| A | iw_2023 | — |
| B | iw2_2023 | — |
| C | ida_2023 | — |
| D | il_2023 | — |

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
| 跨站点空间泛化 | cross-site spatial generalization | 在源站点训练，直接迁移至目标站点 |
| 泛化退化 / 精度退化 | generalization degradation | 跨站点精度相对站内精度的降幅 |
| 迁移路径 | transfer path | 从源站点到目标站点的方向，记为 X→Y |
| 源站点 / 基准站点 | source site | 模型训练所在站点 |
| 目标站点 | target site | 模型直接应用的站点 |
| OOF | Out-of-Fold | 5 折交叉验证的汇总预测 |
| 距离带 | distance band | 按像素到边界距离划分的区域 |
| 5 折交叉验证 | 5-fold cross-validation | 3 训练 + 1 验证 + 1 测试 |

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

| 缩写 | 全称 | 中文 |
|------|------|------|
| mIoU | mean Intersection over Union | 平均交并比（三类） |
| UA | User's Accuracy | 用户精度 |
| PA | Producer's Accuracy | 制图精度 |
| F1 | F1-score | F1 分数 |
| OA | Overall Accuracy | 总体精度 |
| Kappa | Kappa coefficient | Kappa 系数 |
| ER | Error Rate | 误差率（1 − OA） |

## 景观指标

| 缩写 | 英文 | 中文 |
|------|------|------|
| ED | Edge Density | 边界密度 |
| PD | Patch Density | 斑块密度 |
| AREA_MN | Mean Patch Area | 平均斑块面积 |
| AI | Aggregation Index | 聚集度指数 |

## 标点与数字规范

- 中文语境使用中文标点（，。；：""）
- 数字与单位之间空半角空格（30 m、5 天）
- 百分号前不空格（89.53%）
- 区间使用短横线（DOY 116–266）

# 数据资产与口径清单

本轮性质：derived / exploratory。起始HEAD为`2c4a1c3`，2026-10-05开始，2026-10-06完成。全域为A=`iw_2023`、B=`iw2_2023`、C=`ida_2023`、D=`il_2023`；模型为ConvGRU、3D U-Net、U-TAE。每站400个128×128非重叠图块，共2560×2560像元，30 m；三类内部顺序为玉米0、其他1、大豆2。

## 实际读取的资产

| 资产 | 位置与身份 | 本轮用途 |
|---|---|---|
| 已有标签、边界、类型 | `G:/2560图像/20{iw,iw2,ida,il}/2023{站名}shuju/`下`ANNOTATIONS/TARGET_{patch_id}.npy`、`BOUNDARIES/BOUNDARY_{patch_id}.npy`、`BOUNDARY_PAIRS/BOUNDARY_PAIR_{patch_id}.npy`及`metadata.csv` | 读取全部1600图块，核对标签/网格/类型和图块身份；未重新定义类型 |
| 本站保存预测 | `calculate_crop_f1.within_site_file(model,site).parent`定位的D盘12个结果目录；各目录`details/fold_1`至`fold_5` | 读取已有NPZ预测及metrics CSV、run JSON；每折80图块、每图块一次独立测试 |
| 跨站保存预测 | `D:/cross_site_all_20260916/{model}__{source}__.../{target}/details/fold_{1..5}/` | 36个模型—路径组合，各五次完整目标站预测；未调用推理 |
| 现有距离与导出标签 | 各结果目录`maps/reference.tif`及`details/reference_assets/{distance_band_index.npy,reference_contract.json}`；四个参考目录的`class_boundary_distance_pixels.npy` | 核对48个结果目录标签、分带数组相同；直接复用七带 |
| 图块空间特征及CM底表 | 第一轮`sec33_exploration/run_manifest.json`定位的`D:/cross_site_all_20260916/paper_tables/Patch级空间误差底表/` | `patch_spatial_features.csv`、`within_patch_oof.csv`、`cross_patch_fold.csv`；逐图块CM与新计数相等 |
| 冻结AREA_MN组及已有结果 | `results/processed/sec33_exploration/patch_groups.csv`、`results/processed/sec33_f1_raw_scale/*group*cm.csv`；第一轮`group_features.csv` | 保留原分组、缺类组、阈值及特征，不重新分组 |
| 全站与七带整数CM | `results/raw/{within_site_confusion_matrices,cross_site_confusion_matrices}.csv`；`results/processed/sec33_round3_distance/boundary_*_cm_reused.csv` | 完整整数闭合；本站12个矩阵、跨站180个矩阵 |
| 当前F1 | `results/summary/f1_raw_scale/` | 本站汇总F1、跨站五次均值及样本标准差核对，绝对容差1e-12 |

确切绝对路径、大小及SHA-256见`prepare_manifest.json`、`count_manifest.json`、`analyze_manifest.json`、`diagnose_manifest.json`。`joint_counts_index.csv`将每份新计数连接到模型、源站、目标站、预测编号。本站`fold=0`表示五个不重叠测试集合汇总，不是额外训练模型。

## 已有边界类型的实际含义

定义来源为旧工程`docs/PROJECT_CONTEXT.md`第5节、`src/dataset.py`及`src/learning/boundary_analysis.py`。标签NPY为三个相同通道、原码1/2/3，转为0/1/2；类型NPY为uint8位掩膜。位1=玉米—其他，位2=玉米—大豆，位4=其他—大豆。每条参考标签四邻域共享边的两个相邻像元被标记。它表示**直接类别交界的两侧像元邻域**，不是边界线栅格，也不是给所有像元赋予最近边界类型；没有边段ID。

三类交汇可出现3、5、6、7多位值。同一像元在相应按位并集中重复出现；分析时保留两种视图：

- 位组合0—7是互斥完备分区，用于闭合；0是“无直接类型标记”，不是丢失数据。未知非法位为0个。
- 原三种类型按位并集用于同类边界的两侧比较，允许重叠，不能将三种类型贡献直接相加。第三类错误在同一侧参考支持量上计算；它不是第三种参考边界侧。

本轮用完整标签的四邻域邻接直接核对已有位掩膜，逐像元一致；仅作语义验证，未替换原掩膜。图块通过patch_id、patch_uid、tile_row/col、x/y_offset和fold_id关联，完整网格再切回400图块，未把裁剪框或外框当成边界。四站标签没有NoData类别；类型也没有“等距最近类型”选择过程，因而不存在人为打破最近类型平局。多类型交汇已经原样保留。

| 站点 | 有类型像元 | 多类型像元 | 最近带中无直接类型标记 | 最近带以外有类型像元 |
|---|---:|---:|---:|---:|
| A | 1,543,403 | 159,050 | 251,126 | 0 |
| B | 1,495,444 | 114,714 | 307,718 | 0 |
| C | 1,683,273 | 220,807 | 335,734 | 0 |
| D | 1,414,412 | 149,769 | 247,495 | 0 |

因此类型×距离表保留全部七带，但有类型的参考支持只在`(0,1]`。其余六带类型率为NA，零支持计数为0，不能解释为没有错误。内部分析只能用原七带的全部参考像元；本轮不能回答“离某种最近边界越来越远”的问题，也不能称“同一段边界两侧”。两种作物的共同权重只扩展到距离带，未将重叠类型强行变成互斥环境权重。

## 七距离带与沿用限制

原算法见`legacy/manuscript/HLS-Crop/src/learning/distance_band_analysis.py`：在加倍网格标记有效参考类别四邻域共享边线段，欧氏距离变换后取像元中心并除以2。直线相邻像元距边0.5像元；不是距边界像元中心的距离。研究区外框、裁剪框、NoData边不参与。沿用`(0,1]`至`(5,6]`和`>6`七带；本轮读取保存距离，验证有限正值、分带阈值和旧数组身份，**未重新执行距离变换**。

历史`boundary_identity_checks.csv`中的2处复合参考指纹不一致分别为B站本站3D U-Net、U-TAE；其中U-TAE另缺完整GeoTIFF CRS标签。它们不是标签数组缺失。本轮实际核对这些目录与目标参考标签、分带数组一致；没有修补指纹或GeoKey，没有重新证明历史地理来源。原距离生成及地理来源仍为**Partially verified**，当前数组连接与计数为**Verified**。景观指数沿用图块底表，未从标签重算FRAGSTATS。

## 复现入口

从仓库根目录运行：`python -B scripts/explore_sec33_crop_spatial_context.py analyze`、`diagnose`，再运行`python -B scripts/plot_sec33_crop_spatial_context.py`。这三步只读已有新计数并写本轮目录。`prepare`、`count`已完成，检测到既有底表时会停止，避免覆盖缓存；它们不是每次复查需要重跑的步骤。最后`seal`记录交付哈希。不要运行历史生产脚本更新本轮结果。

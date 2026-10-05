# 3.3 第三轮边界距离带探索核查

核查日期：2026-10-05
HEAD：`db026b4`；本轮未提交
结果性质：`derived / exploratory`
总体处理链状态：**Verified**
空间指标状态：**Partially verified**

## 本轮实际核查

- 复用 `results/processed/sec33_exploration/boundary_within_cm.csv` 和 `boundary_cross_fold_cm.csv`，未调用会写回历史目录的生产流程，未重训、重新推理、重跑 FRAGSTATS 或重新执行 EDT。
- 站内分带矩阵 84 条，跨站逐次分带矩阵 1260 条；键、距离带名称、模型、来源、目标站和五次预测覆盖均通过核查。
- 七带整数混淆矩阵逐组合相加，恢复 12 个站内总体矩阵和 180 个跨站逐次总体矩阵；目标站同一参考支持量在站内、跨站各次预测间一致。
- 站内先汇总矩阵计算漏分率，跨站逐次计算后取五次均值和样本标准差；未用合并五次矩阵替代逐次指标，也未用带内指标平均验证矩阵闭合。
- 336 条站内分带指标、5040 条跨站逐次分带指标和 1008 条分源汇总已生成。七带带内贡献之和恢复全站漏分率差；D 站大豆“大豆→玉米”和“大豆→其它”两项差值逐带相加恢复大豆 `Δe`。
- 最近带与 `d>6` 的配对比较保留五次方向、范围和负值；图件已实际查看，图例、单位、距离区间、副坐标及开放区间标识清楚，未发现裁切或明显重叠。
- 新增内存测试 6 项全部通过：

```text
python -B -m unittest scripts/test/test_sec33_round3_distance.py -v
```

## 沿用记录与限制

距离定义为完整标签图中有效类别四邻域共享边到像元中心的欧氏距离，原七带为 `(0,1]`、`(1,2]`、`(2,3]`、`(3,4]`、`(4,5]`、`(5,6]`、`>6` 像元。本轮仅核对已有数组、契约和分带矩阵的一致性，未重新生成距离栅格。

历史边界清单记录两处参考指纹不一致和一处 GeoTIFF 缺完整 CRS GeoKey。本轮没有修改元数据、重建数组或把这些历史记录解释成新的异常；因此空间指标标为 **Partially verified**。在当前数组一致性和矩阵闭合范围内，结果可支持距离带内漏分率、净增错误数和带内贡献的描述性比较，但不能单独证明边界是错误的因果来源，也不能区分类别组成与空间结构的独立作用。

## 产物位置

- 计算脚本：`scripts/explore_sec33_round3_distance.py`
- 测试：`scripts/test/test_sec33_round3_distance.py`
- 处理底表：`results/processed/sec33_round3_distance/`
- 汇总、数据字典和报告：`results/summary/sec33_round3_distance/`
- 探索图：`figures/exploratory/sec33_round3_distance/`
- 输入、脚本和主要产物哈希：`results/summary/sec33_round3_distance/run_manifest.json`

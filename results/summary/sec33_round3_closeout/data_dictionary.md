# 第三轮收尾数据字典

数据性质：`derived / exploratory`。由第三轮已保存的七带整数混淆矩阵和逐次漏分率表派生，不是新预测。A=`iw_2023`，B=`iw2_2023`，C=`ida_2023`，D=`il_2023`；类别顺序玉米0、其他1、大豆2。全部CSV以17位有效数字保存，空数值表示NA，不表示零。

## 配对与汇总

`results/processed/sec33_round3_closeout/nearest_vs_gt6_delta_e_per_fold.csv`：720行，完整键 `model/source/target/fold/population`。`fold`为源站模型预测编号1—5；不是按表的行位置配对。`population`取corn、soybean、other、all，前两种共360行。all表示总体错误率，不能称作某一类别漏分率。

| 字段 | 含义 |
|---|---|
| `near_pixels / gt6_pixels` | 最近带 `(0,1]` / 内部带 `>6` 的同一真实类参考支持量；all为三类合计 |
| `near_within_e / gt6_within_e` | 同模型本站分带汇总矩阵的漏分率 |
| `near_cross_e / gt6_cross_e` | 同次跨站预测的分带漏分率 |
| `near_delta_e / gt6_delta_e` | 逐次跨站率减同带本站率 |
| `d_gt6_minus_near` | 内部逐次Δe减最近带逐次Δe，即D_k |
| `near/gt6_within/cross_status` | 对应输入率的defined或undefined_zero_support |
| `direction` | D>0为gt6_higher；D<0为near_higher；D=0为equal；NA为not_calculable |
| `status` | defined或not_calculable，不可计算不记为equal |

`nearest_vs_gt6_delta_e_summary.csv`：144行，键 `model/source/target/population`，其中作物72行。

- `near_delta_e_mean / gt6_delta_e_mean`：五次同带Δe均值。
- `d_mean / d_std / d_min / d_max`：完整五次D的均值、样本标准差（ddof=1）、最小值、最大值。
- `n_predictions / n_defined`：实际记录数和可计算D次数。五次编号必须完整，否则停止；五次存在NA则上述D统计均为NA，不缩小分母。
- `n_gt6_higher / n_near_higher / n_equal / n_not_calculable`：正、负、严格零及NA次数。
- `mean_direction`：五次平均D的方向；`five_direction`：all_gt6_higher、all_near_higher、all_equal、mixed或not_calculable。mixed表示可计算方向不完全相同，不等于平均为零；有NA时不称为mixed或相等。
- `status`：defined或undefined_one_or_more_predictions。

以上是**相对本站的额外漏分比较**。原 `sec33_round3_distance/nearest_vs_gt6_*.csv` 为**跨站绝对漏分率比较**，原位保留。所有方向使用未舍入值，不以1e−12容差把小差值改成零；容差仅用于浮点闭合。

## D站大豆五次诊断

`results/processed/sec33_round3_closeout/d_soybean_gt6_delta_e_components_per_fold.csv`：45行，键同配对逐次表，`target=il_2023`、`population=soybean`、`band=d>6`。

- `soybean_pixels`：该带真实大豆像元数。
- `within/cross_to_corn/other_errors`：本站/同次跨站的大豆→玉米/其他类整数错误数。
- `within/cross_to_corn/other_rate`：上述错误数除以同带真实大豆像元数。
- `delta_to_corn_rate / delta_to_other_rate`：两种逐次跨站率减本站率；允许负值。
- `component_sum`：两去向差之和；`gt6_delta_e`为同次内部总Δe；`component_closure_error`为两者相减，容差1e−12。
- `d_gt6_minus_near / direction`：关联该次两端比较，含义同上；`status`为defined或undefined_zero_support。

这里每项分母是N(真实大豆,内部带)，不同于第二轮F1误差分量的Z=2TP+FP+FN；两项恢复Δe，不能用来恢复全部ΔF1。零支持时率和闭合差均为NA。

`d_soybean_five_prediction_diagnostic.csv`：九行，键 `model/source/target/population`。

- 保留两带平均Δe、内部五次Δe及标准差/最小/最大：`gt6_delta_e_fold_1...5`按明确预测编号排列。
- `d_fold_1...5 / d_direction_fold_1...5`：同次两端D值及方向；D均值、方向计数及标签含义同配对汇总表。
- `delta_to_corn_fold_1...5 / delta_to_other_fold_1...5`：内部两种漏分去向的逐次差，按预测编号与内部Δe逐次对应；计数和本站/跨站率保留在45行底表中。
- `delta_to_corn_mean / delta_to_other_mean`：五次去向差均值；有NA不改用较少次数。
- `n_gt6_positive/negative/zero/defined`：内部Δe自身的正/负/零/有效次数，不能与D的方向计数混用。两端可能始终最近带更高而内部Δe始终为正。

## 图、核查与运行

`figures/exploratory/sec33_round3_closeout/delta_e_distance_overview.png`读取原 `sec33_round3_distance/three_source_overview.csv` 的 `delta_error_rate_three_source_mean`。每点严格为三个来源各自五次Δe均值的等权平均，不把15次预测作为独立重复；没有误差线。四站A—D为行、玉米/大豆为列，三个模型统一颜色、同一纵轴尺度，168个点逐项对照分源结果。七带为类别位置；>6为开放区间，用空隙、分隔线和断开连线表示。

`checks.csv`保存本次实际计算核查；`run_manifest.json`保存6个输入、收尾脚本、复用脚本和6个输出的SHA-256。文档和测试等最终交付哈希另见 `delivery_manifest.json`，不改旧运行清单。

运行：`python -B scripts/close_sec33_round3_distance.py`。仅重建本收尾目录内的派生表与图，不调用旧生产入口。测试：`python -B -m unittest discover -s scripts/test -p "test_sec33_round3*.py" -v`，内存用例不写正式结果。

距离数组和历史身份依据仍沿用原记录，未重新生成或重新检查外部空间数组，因此空间来源为Partially verified；本次从既有整数矩阵到逐次率、配对、去向分解和图表数据的核查为Verified。

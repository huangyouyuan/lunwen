# 3.3 第三轮距离带结果数据字典

本目录保存第三轮边界距离带探索的 `derived / exploratory` 结果，不直接进入论文正文。站点 A、B、C、D 分别对应 `iw_2023`、`iw2_2023`、`ida_2023`、`il_2023`；模型类别顺序为玉米 `0`、其它 `1`、大豆 `2`。

## 距离与计算口径

- `band`：原七带，`0<d<=1`、`1<d<=2`、`2<d<=3`、`3<d<=4`、`4<d<=5`、`5<d<=6`、`d>6`，单位为像元；最后一带为开放区间。
- 距离沿用完整参考标签图中有效类别四邻域共享边到像元中心的欧氏距离定义。相邻边界像元的距离为 `0.5` 像元。本轮未重新执行距离变换，也未把裁剪框、研究区外框或 NoData 边缘当作类别边界。
- `population`：`corn`、`soybean`、`other` 为真实类别，`all` 为全部真实类别。
- `pixels`：该距离带中相应真实类别的参考像元数 `N(c,b)`。
- `errors`：该带真实类别被预测为其它类别的像元数。
- `error_rate`：类内漏分率 `errors / pixels`，即 `1 - Recall`，不是 F1 或按全体像元归一化的错误率。
- 站内指标先汇总同一距离带的 OOF 混淆矩阵后计算；跨站指标对五次预测分别计算，再取五次均值和样本标准差（`ddof=1`）。
- `delta_error_rate`：跨站五次平均漏分率减站内漏分率。负值保留；零支持量或五次中存在不可计算值按现有 NA 规则记录，不静默减少预测次数。
- `pixel_share`：`N(c,b)` 除以该站该作物全站参考像元数。
- `net_added_errors_mean`：跨站五次错误数均值减站内错误数，是净错误数差，不表示逐像元由正确变错的数量。
- `net_overall_contribution`：`pixel_share × delta_error_rate`，七带之和恢复全站该作物漏分率差；它不用于分解全部 F1 变化。

## 文件和字段

### `band_metrics_within.csv`

站内每个模型、目标站、距离带和类别的汇总指标。字段为：`model`、`target`、`band`、`population`、`pixels`、`errors`、`error_rate`、`status`、`pixel_share`、`source`、`fold`。`source` 和 `fold` 对站内汇总为空。

### `band_metrics_cross_fold.csv`

跨站每个模型、来源、目标站、预测折、距离带和类别的逐次指标。字段为：`model`、`source`、`target`、`fold`、`band`、`population`、`pixels`、`errors`、`error_rate`、`status`、`pixel_share`。五次记录必须完整，逐次结果不能合并后代替五次指标均值。

### `band_metrics_summary.csv`

分源汇总表，键为模型—来源—目标站—距离带—类别。字段为：`model`、`source`、`target`、`band`、`population`、`pixels`、`pixel_share`、`within_errors`、`within_error_rate`、`cross_errors_mean`、`cross_errors_std`、`cross_error_rate_mean`、`cross_error_rate_std`、`delta_error_rate`、`net_added_errors_mean`、`net_added_errors_std`、`net_overall_contribution`、`n_predictions`、`n_defined_error_rate`、`status`。

### `three_source_overview.csv`

三个来源等权平均的概览表，不把 15 次预测作为独立重复。字段为：`model`、`target`、`band`、`population`、`within_error_rate`、`pixel_share`、`cross_error_rate_three_source_mean`、`delta_error_rate_three_source_mean`、`net_overall_contribution_three_source_mean`、`source_count`、`aggregation`。

### `band_contribution_closure.csv`

全站漏分率差闭合核查。字段为：`model`、`source`、`target`、`population`、`whole_within_error_rate`、`whole_cross_error_rate_mean`、`whole_delta_error_rate`、`sum_band_contributions`、`absolute_error`、`status`。

### `nearest_vs_gt6_summary.csv` 和 `nearest_vs_gt6_per_fold.csv`

按同一来源模型预测配对比较最近带与 `d>6` 带。`per_fold` 保留每次预测的两带漏分率和方向；`summary` 汇总配对次数、方向计数及差值范围。该比较不把 `d>6` 画作等宽连续距离点。

### `d_soybean_error_decomposition.csv`

D 站大豆的两类漏分方向分解。`soybean_to_corn` 和 `soybean_to_other` 的站内率、跨站五次均值和标准差、各自差值相加恢复 `delta_soybean_error_rate`。这些是漏分率差分量，不是因果贡献，也不同于按真实类别像元数归一化的全体误分类率。

### `checks.csv`

本轮脚本实际执行的身份、覆盖、矩阵闭合、贡献闭合和 D 站大豆分解核查；`status` 仅使用 `Verified`、`Partially verified` 或 `Not verified`。

### `run_manifest.json`

记录本轮输入、脚本、主要产物的 SHA-256、计算口径及历史限制。空间指标的总体验证状态为 `Partially verified`，因为本轮沿用既有距离数组，未重新执行原始 EDT；历史记录中的两处参考指纹不一致和一处 GeoTIFF 缺完整 CRS GeoKey 均未被自动修补。

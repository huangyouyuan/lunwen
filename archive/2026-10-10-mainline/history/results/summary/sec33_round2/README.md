# 3.3 第二轮探索结果

本目录保存 AREA_MN 原尺度结果的探索图数据及 D 站大豆四类混淆去向分解，均为 `derived / exploratory`。

- `d_soybean_error_components_summary.csv`：固定 D 站、三模型、三来源、低中高组；跨站五次分别计算分量后取均值，四项分量差值之和恢复 ΔF1。
- `d_soybean_key_contrasts.csv`：各模型—来源组合的高低组 ΔF1 和误差分量对照。
- `../processed/sec33_round2/d_soybean_components_per_prediction.csv`：本站组汇总和跨站逐次底表，含支持量、Precision、Recall、按真实类分母的误分类率。
- `overall_relation_plot_data.csv`、`composition_plot_data.csv`、`d_soybean_source_plot_data.csv`：图件对应数据。
- `exploration-report.md`：本轮证据判断，不是论文正文。

F1 分量的分母为 `Z=2TP+FP+FN`；它们与按真实类别像元数归一化的误分类率分开保存。误差线是五次预测的样本标准差，不是置信区间。

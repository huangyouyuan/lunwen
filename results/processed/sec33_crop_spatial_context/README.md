# 保留的整站矩阵与可复用逐次表

`whole_cm.csv`供当前定向混淆收尾和1.3、3.1基础核对读取，包含12个本站与180次跨站的完整整数混淆矩阵，类别顺序corn、other、soybean。另从归档恢复完整F1四项错分分量、六向最近带—远内部对照、距离类内错误率和共同权重的逐次底表；对应汇总见[结果阅读入口](../../summary/README.md)。这些是原有数据，未重新统计。

2026-10-11已恢复`joint_*.npz`192份、身份索引、参考数组、metadata以及整站七带×位组合矩阵与方向统计。`cm[400,7,8,3,3]`中的400仅是无重叠存储分区；本次逐运行核对，沿该轴求和与完整参考斑块计数中的`type_band_bit_cm`沿类型轴求和逐元素相等。可直接复用这些整数底表，不重新读取预测；不能以`patch_id`连接整图参考斑块的`PID`。

`reference_*.npz`和metadata用于旧存储身份/像元定位追溯，完整斑块空间对象仍使用`sec33_reference_patch_types/reference_full_*.npz`。`reference_type_band_support.csv`中的`patches`是涉及存储图块数，不能称完整参考斑块数。按位并集的`type_direction_*`仍有重叠，只可作补充；主要比较用收尾互斥分组，闭合用0—7互斥位码。

旧图块AREA_MN、匹配和相关条件结论仍在[历史目录](../../../archive/2026-10-10-mainline/history/results/processed/sec33_crop_spatial_context/)。恢复路径逐项见[第二次清单](../../../archive/2026-10-10-mainline/restored-second-pass.csv)。原脚本停用，不运行旧生产流程重建此目录。完整F1分量的分母为`2TP+FP+FN`，不能与真实类别归一化的定向错分率相加；共同距离权重只是描述性标准化，不是调整后F1。

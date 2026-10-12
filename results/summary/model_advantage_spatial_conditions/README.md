# 模型优势在空间条件中的分布

2026-10-13；起点HEAD `b812fb1`。性质：derived / exploratory。执行[任务计划](../../../plan/tasks/2026-10-13-model-advantage-spatial-conditions.md)，直接复用已有计数、统一分档和条件权重；没有训练、推理、修改论文或制图。

先看[精简主表](main_reading_table.md)和[短报告](analysis-report.md)。主表覆盖四站两作物、U-TAE/3D U-Net相对ConvGRU的16个本站比较；全部跨站路径在[48行路径表](cross_path_overview.csv)。优势均定义为ConvGRU漏分率减相应模型漏分率，正值表示相应模型漏分更少。

| 内容 | 文件 |
|---|---|
| 本站完整分解：全作物、七带、三段、24个联合格 | [within_group_advantages.csv](within_group_advantages.csv)，560行 |
| 跨站同分组五次统计、绝对错误率、自身增量与优势变化 | [cross_group_advantages.csv](cross_group_advantages.csv)，1680行；[路径概览](cross_path_overview.csv)，48行 |
| 本站联合格净贡献前列 | [within_top_joint_cells.csv](within_top_joint_cells.csv)，49行，第三名并列全保留 |
| 同一支持范围下，保留自身距离比例与统一距离比例 | [本站组优势](within_conditional_advantages.csv)、[本站高低组差](within_conditional_contrasts.csv)、[跨站组优势](cross_conditional_advantages.csv)、[跨站高低组差](cross_conditional_contrasts.csv) |
| 条件对照参考权重、纳入像元和被排除范围 | [same_support_weights.csv](same_support_weights.csv)、[conditional_coverage.csv](conditional_coverage.csv) |
| 复用C/D大豆十二档面积×七带结果，转成模型差额 | [refined_CD_bridge.csv](refined_CD_bridge.csv)，12行；沿用上一轮四组共同权重 |
| 完整F1及其本站差值，避免漏分排序替代F1排序 | [complete_F1_comparisons.csv](complete_F1_comparisons.csv)，48行 |
| 逐次预测身份能否配对 | [prediction_identity_audit.csv](prediction_identity_audit.csv)，240份运行记录 |
| 机器可读主表、固定口径、核查 | [main_reading_table.csv](main_reading_table.csv)、[analysis_config.json](analysis_config.json)、[verification.md](verification.md) |

逐次数据在[processed目录](../../processed/model_advantage_spatial_conditions/)，包括8960行组优势、13440行单模型组错误率、条件对照和完整三类指标。两种较优模型可通过共同ConvGRU基准相减读取，但本轮没有另扩成第三套比较。

## 复现

```powershell
python -B scripts/analyze_model_advantage_spatial_conditions.py
python -B scripts/test/check_model_advantage_spatial_conditions.py
```

默认复用仓库中的计数与身份快照，不依赖外部预测影像，不重复推理或空间指标计算。生产脚本只更新本批生成表、主表Markdown、配置和manifest；人工报告和字典不由脚本重写。测试只读，包含原距离函数的小数组语义测试；这些数组仅为测试夹具，不进入科研结果。

本轮首次用`--capture-provenance`从实际外部运行JSON与图块清单提取240份身份记录到[`prediction_identity_snapshot.json`](../../processed/model_advantage_spatial_conditions/prediction_identity_snapshot.json)。快照保留原路径、原文件SHA-256、分折、图块集合指纹和完整矩阵，可随Git传递。已有快照时该选项停止，正常复现无需再次使用；它也不读取或运行模型权重。

统计定义与NA见[字典](data_dictionary.md)。[manifest.json](manifest.json)覆盖本轮输入、生成表、生成主表和生产脚本哈希，不包括人工报告。原分布继续以[联合气泡表](../area_shape_joint_bubbles_v3/area_shape_joint_bins.csv)为入口，本轮没有重新定义形态类型。

# 1.3.2景观格局：现行展示入口

2026-10-14，结果性质为 **derived**。本目录只选取已有统计、汇总已保存联合格用于文字核对，并生成论文展示；未重训、推理、计算新景观指数或重新分档。原始数据、旧表及气泡图v3保持原位。

- [表1数据](table1_landscape_context.csv)：8个站点—作物组，斑块数、AI及整站ED来自[基础表](../sec13_sec31_foundations/README.md)的`scope=full`结果；ENN P90直接复用[已有分布表](../sec33_indicator_grading_preparation/indicator_distribution_reading.csv)的`domain=site_crop, metric=ENN, weighting=patch_equal, q90`。CSV中的整站ED为方便连接而重复附列，LaTeX按站点合并，不能当作两种作物各自的ED。
- [联合分布阅读表](joint_distribution_reading.csv)：对[气泡图v3原汇总](../area_shape_joint_bubbles_v3/area_shape_joint_bins.csv)作必要的行筛选与加总；只服务本节文字核对。最大单格、前三格总份额、小于10 ha的数量/面积份额和大型复杂组合分别保留，不能将最大单格称为绝对多数。
- [闭合检查](closure_checks.csv)：149,234个作物斑块、192个联合格；八组分档面积占比各自为100%。169个非零格绘制，23个零格留空。
- [生成与几何清单](manifest.json)：输入输出SHA-256、旧版缩放参数及最小圆间净距。

ENN每个完整参考斑块计一次。P90沿用pandas线性顺序统计量：升序后在从0开始的位置`(n−1)×0.9`按相邻值线性插值；独立核查从完整参考表手工排序验证，未重算ENN距离。八组没有缺失/无效ENN，单像元及外缘斑块均保留。ENN是窗口内最近同类斑块边界像元中心距离，不是田块间净空距离；历史FRAGSTATS工程参数的核查范围没有升级。

联合图沿用六档AREA（ha）：<10、10–<50、50–<100、100–<200、200–<500、≥500；四档SHAPE：1–<1.5、1.5–<2、2–<3、≥3。面积份额分母为本站该作物的完整参考面积。图中的面积份额、正文辅助引用的AREA面积加权中位数、表中ENN斑块等权P90是三种不同口径；展示分档不定义形态类型。

## 活动文件与复现

- 脚本：`scripts/generate_sec13_landscape_display.py`，只读取保存的summary，不调用原探索脚本的聚合入口。
- 表体：`tables/sec13_landscape_context_rows.tex`。
- 联合图：`figures/study_area/fig_sec13_area_shape_joint.pdf`及600 dpi PNG；两份面板PDF均按原尺寸进入LaTeX，图框各7.6×7.6 cm；`.tex`与`_legend.tex`在主文排子图题和共享图例。
- 正文标签：`tab:sec13_spatial_metrics`、`fig:sec13_area_shape_joint`。当前为表1与图3，数字编号由LaTeX生成。

```powershell
python -B scripts/generate_sec13_landscape_display.py --check
python -B scripts/test/check_sec13_landscape_display.py
```

首次生成去掉`--check`；若已有输出，脚本会停止，需先按仓库规则保留旧版本，不自动覆盖。旧表`tables/sec13_spatial_metrics_enn_equal_rows.tex`和旧生成器`generate_sec13_spatial_tables.py`继续作为历史展示/可复用分布核查入口，不能再当作现行表1。旧联合图v3及其汇总、检查、脚本全部保留。

本轮核查与文字判断追溯见[核查记录](../../../verification/sec132-landscape-2026-10-14.md)，实际PDF及页面见[预览入口](../../../output/README.md)。

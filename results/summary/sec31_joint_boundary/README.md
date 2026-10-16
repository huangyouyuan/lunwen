# 3.1完整斑块面积—形状×边界／内部

2026-10-17，**derived**，只复用真实参考与站内预测。当前正文证据及全站图4入口；没有训练、推理或重算景观指数。原局部差异案例继续保留在`../sec31_spatial_examples/`，不作为全站判断依据。

## 入口与数据链

- `scripts/analyze_sec31_joint_boundary.py`：复用`spatial_error_conditions/within_group_metrics.csv`的1,728行组合×距离整数计数，汇总边界／内部；独立以12份`processed/sec33_reference_patch_types/counts_within_*.npz`核查。参考支持与图2的`area_shape_joint_bubbles_v3/area_shape_joint_bins.csv`一致。
- `scripts/plot_within_site_full_errors.py`：读取`prediction_count_index.csv`所指12份原参考、站内交叉验证预测，逐像元生成全站图；复用旧局部脚本的只读网格与身份核查，不运行旧生产阶段。
- `scripts/summarize_sec31_joint_boundary.py`：从上述完整精度表生成[分析报告](analysis.md)、[正文证据索引](prose_evidence.csv)及`tables/sec31_spatial_text_values.tex`。
- `scripts/test/check_sec31_joint_boundary.py`：端点、零分母和带符号贡献测试；`--artifacts`用原始栅格及完整PID属性重新直接聚合，并核查原生PDF像元；加`--compiled`核对整稿内嵌12幅图的像元和5.2 cm尺寸。

以上为仓库根目录下的入口。生成器遇到现有同名输出会停止；重新生成前先按AGENTS规则核查用途、原字节归档及SHA-256，不删除或覆盖历史输出。图件拼版为`figures/results/fig_within_site_full_errors.tex`，由3.1当前图4引用。

## 分组与分母

AREA六档为[0,10)、[10,50)、[50,100)、[100,200)、[200,500)、[500,+∞) ha；SHAPE四档为[1,1.5)、[1.5,2)、[2,3)、[3,+∞)。属性来自完整八邻域参考斑块，以`target,PID`连接，不在图块或窗口重算。零支持组合仍保留。

类别交界按完整标签有效四邻域共享边确定，像元中心距交界≤30 m为边界，其余全部作物像元为内部；外框、存储图块切线、窗口边缘和无效数据边缘不产生交界。内部合并保存距离数组的1—6号分组，边界为0号。独立重算完整边界掩膜后逐像元核对，未重新验证其它距离分带的具体距离值。

| 文件 | 行数与用途 |
|---|---|
| `reference_support.csv` | 192行=四站×两作物×24组合；完整斑块数、参考数、边界／内部支持及面积占比 |
| `within_position_metrics.csv` | 1,152行=192组合×三模型×两位置；主要定位底表 |
| `within_joint_metrics.csv` | 576行；两位置合并，与原组合表闭合 |
| `within_site_position_metrics.csv` | 48行；24组合汇总的全站位置指标 |
| `small_area_by_shape.csv` | 192行；仅将AREA<50 ha的两档按SHAPE合并，保留两位置与三模型 |
| `model_comparisons.csv` | 1,152行；ConvGRU→3D U-Net、ConvGRU→U-TAE、3D U-Net→U-TAE三个带符号比较，各384行 |
| `prose_evidence.csv` | 正文数值、来源文件、行筛选、计算式、完整精度和两位小数展示；对应LaTeX宏 |
| `analysis.md` | 四个待核查问题的读数、主要支持组合、负向结果及解释限制 |
| `full_site_pixel_checks.csv` | 颜色计数与原始参考数、漏分数核查 |
| `full_site_grid_checks.csv` | 网格、类别身份、分辨率、CRS依据；B站U-TAE缺CRS标签的原情况保留 |
| `verification_checks.csv` | 汇总阶段151项核验 |
| 三份`*manifest.json` | 汇总、绘图、读数各阶段输入、脚本与输出SHA-256 |

字段中`target/crop/group/model/position`分别为站点、作物、完整斑块组合、模型、位置。机器码`corn/soybean`为玉米／大豆，`boundary/interior`为边界／内部。`site`为A—D。

- `reference_support.reference_pixels`是组合全部作物参考数；`patch_count`为归属该组合的完整斑块数，不能跨位置累加；`area_share=reference_pixels/whole_crop_pixels`；`boundary_share=boundary_reference_pixels/reference_pixels`。
- 位置表`reference_pixels`是该位置支持，`group_reference_pixels`为完整组合支持，`fn`为该位置漏分数；`position_area_share=reference_pixels/whole_crop_pixels`，`position_share_in_group=reference_pixels/group_reference_pixels`，`omission_rate=fn/reference_pixels`，`error_share=fn/whole_fn`。`whole_fn`始终为同站、同作物、同模型全站漏分总数。
- 比较表`rate_reduction_pp=100×(基准漏分率−比较模型漏分率)`，单位百分点；`net_fewer_pixels=基准FN−比较模型FN`；`net_reduction_share=net_fewer_pixels/whole_net_fewer_pixels`；`whole_rate_contribution_pp=100×net_fewer_pixels/whole_crop_pixels`。最后一项可跨组、位置相加，单位百分点。负数表示比较模型漏分更多；净贡献可负、可超过100%，净差分母为0则NA。
- 率和比例存储为0—1（字段名含`pp`的为百分点），计数为整数，展示时才保留两位小数；零参考数不写为零错误率。

全站图蓝色`#377EB8`、红色`#D73027`、灰色`#BDBDBD`，每幅原生2560×2560像元、5.2×5.2 cm，无平滑、膨胀、透明度或细密边界。红色包含作物互混及作物判为其它地类；参考其它始终灰色，不显示其中误分入作物的像元。纸面只用于观察聚集，细小边界差异由整数统计支撑。漏分净差不是完整F1分解，描述性对应不作为独立因果作用。

本次最终核验范围、编译和页面检查见`verification/sec31-joint-boundary-2026-10-17.json`；历史核验与本次范围分开记录。

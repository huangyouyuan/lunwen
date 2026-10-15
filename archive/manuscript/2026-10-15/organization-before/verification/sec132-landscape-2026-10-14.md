# 1.3.2景观格局正文、表1及联合图核查

2026-10-14，基于HEAD `1d7d025`及已有未提交的“跨站表只显示平均F1”修改。本轮保留这些既有改动，只更新1.3.2、相关表图、生成入口和必要引用说明；未提交或推送。

**Verified**：本轮的保存统计复用、正文数字、分位数权重、联合格闭合、图例比例及受影响页面。**Partially verified**：沿用的ENN距离及历史FRAGSTATS工程参数仍受原验证范围限制，本轮没有重新生成距离或景观指数。本次不代表整篇论文定稿。

## 实际修改

- `sections/02_data.tex`只改1.3.2及其表图。正文依次交代指标用途与选择、统计对象和分母、共性、联合差异和四站特点。没有引入模型、分类错误或泛化原因。
- 表1为站点、作物、斑块数、AI（%）、ENN P90（m）、整站ED（m/ha）六列；ED同站两行合并。AREA/SHAPE中位数、极值及PD退出展示，原文件保留。
- 联合图接入`fig:sec13_area_shape_joint`，自动成为图3；原本站F1图顺延为图4，D站示例为图5，差值热力图为图6。没有按旧图号覆盖图件。
- 新生成脚本`generate_sec13_landscape_display.py`直接读取已有summary；原探索脚本只复用绘制函数，不调用分档统计入口。新表体、分面矢量PDF、主文子图题/图例LaTeX、独立PDF与600 dpi PNG已生成。
- 表图在第4页通栏排列，图框各7.6×7.6 cm。为解决首轮`strip`的栏位及1.70 pt高度警告，改为本节末通栏顶端排版；未改动方法和结果内容。

## 数据与正文追溯

表1选取[新展示数据](../results/summary/sec13_landscape_display/table1_landscape_context.csv)，来源为基础表中的全图类别/景观背景及已有分布表。ENN P90使用`domain=site_crop, metric=ENN, weighting=patch_equal, q90`；排序后按从0开始的位置`(n−1)×0.9`线性插值，每个完整参考斑块计一次。八组无缺失值，保留单像元和外缘斑块。

| 站点 | 玉米ENN P90/m | 大豆ENN P90/m |
|---|---:|---:|
| A | 161.55 | 180.00 |
| B | 180.00 | 240.00 |
| C | 152.97 | 180.00 |
| D | 180.00 | 189.74 |

独立核查从完整参考特征表手工排序及插值，八组均与复用值一致；NP、AI、ED另与`sec33_reference_patch_types/background_{class,landscape}.csv`的`scope=full`对照。D站大豆斑块数为14407、AI为93.43%，使用实际表值，不沿用交接提示中的误记。

联合图直接复用[原192格汇总](../results/summary/area_shape_joint_bubbles_v3/area_shape_joint_bins.csv)；本轮只筛选或加总已有格，见[文字阅读表](../results/summary/sec13_landscape_display/joint_distribution_reading.csv)。所有面积份额均以本站该作物总面积为分母。

| 正文判断 | 核对依据 |
|---|---|
| 四站共性 | AI 91.22%～93.92%；八组ENN等权中位数均67.08 m；玉米AREA面积加权中位数116.91～130.95 ha。三者不是同一统计口径，也不证明完整分布一致。 |
| A较规则、面积相对集中 | SHAPE<2占玉米78.27%、大豆80.82%；两作物前三联合格合计44.74%、47.51%，均为四站最高。最大单格分别22.42%、19.45%，均为100≤AREA<200 ha且1.5≤SHAPE<2，不称绝对多数。 |
| B两作物分布差异突出 | 玉米最大格200≤AREA<500 ha且2≤SHAPE<3，占16.06%；大豆最大格10≤AREA<50 ha且1≤SHAPE<1.5，占19.92%；大豆ENN P90为四站最高240.00 m。 |
| C分散、复杂且大小并存 | 前三联合格合计30.38%、33.05%，均为四站最低；小于10 ha斑块占数量90.24%、89.94%，占作物面积4.51%、5.46%；AREA≥200 ha且SHAPE≥3的份额分别16.78%、10.09%。NP及整站ED最高，不将数量多等同主要面积都小。 |
| D两作物主要组合接近 | 两作物前三格集合相同：100–<200 ha×1.5–<2、200–<500 ha×2–<3、10–<50 ha×1–<1.5（排序略有不同）；ED为四站最低51.76 m/ha。 |

## 实际执行与版面检查

以下命令均已完成：

```powershell
python -B scripts/generate_sec13_landscape_display.py
python -B scripts/generate_sec13_landscape_display.py --check
python -B scripts/test/check_sec13_landscape_display.py
python -B scripts/test/check_area_shape_joint_bubbles.py --tag area_shape_joint_bubbles_v3
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
```

- **Verified**：149234个作物斑块、八组各24格；斑块数和参考像元数闭合，八组面积占比各100%。原汇总CSV及探索版v3字节保持。
- **Verified**：169个非零格全部绘制，23个零格留空；不设最小气泡、不画描边放大小值。圆面积与面积份额严格正比，两面板四站同一尺度；图例1%、5%、20%与气泡的物理直径一致。
- **Verified**：新矢量图圆间最小净距约0.219 mm，至格边最小净距约0.164 mm；无圆重叠或越格。独立图全部文字9 pt、宋体/Times New Roman，未栅格化。实际查看了独立PNG和论文第3—5页；第4页表宽17.4 cm，数值、表注、图注、共享图例和标签无裁切。
- **Verified**：最终9页编译完成，无Overfull/Underfull、未定义引用或缺字。此前已有的宋体/黑体粗体替代、`caption hypcap`及`unsrtnat`不识别软件条目/年份的警告仍保留，未借本次修改文献样式。
- **Verified**：1.3.2之前的研究区与数据正文保持；其余章节、正式F1统计和图件未因本次修改而变化，仅自动图号及分页顺延。跨站主表继续保留上一轮的仅均值百分数格式。

最终[9页PDF](../output/previews/2026-10-14-sec132-landscape/manuscript.pdf)、[第3页](../output/previews/2026-10-14-sec132-landscape/page-3.png)、[第4页](../output/previews/2026-10-14-sec132-landscape/page-4.png)及[第5页](../output/previews/2026-10-14-sec132-landscape/page-5.png)保存供审阅；哈希及范围见[机器记录](sec132-landscape-2026-10-14.json)。首轮排版在预览目录`pass1/`原位保留，不作为当前PDF。

原活动源码及入口修改前备份在[保留目录](../output/archive/2026-10-14/sec132-landscape-before/)，原路径、备份路径、原因及SHA-256见其中两份manifest；未删除或移动旧统计、脚本和预览。

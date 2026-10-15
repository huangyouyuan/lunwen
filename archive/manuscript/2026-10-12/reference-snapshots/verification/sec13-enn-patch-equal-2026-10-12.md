# 1.3.2 ENN斑块等权及小五字体核查（2026-10-12）

版面用途说明：前部记录首次14.84 cm紧缩表的核查；当前表已按作者后续意见铺满17.4 cm双栏宽，行列间距重新安排，详见文末“后续通栏排版修订”。统计口径与数据不变。

作者最新决定：ENN按完整参考斑块等权统计，每个斑块计一次，报告中位数（全体最小值～最大值），单位m；AREA、SHAPE保持参考像元面积加权中位数。图表中文为小五宋体，字母和数字为小五Times New Roman。此前“编译提交”的授权仍适用于本轮修订；未推送。

## 数据及统计口径

**Verified**：复用`results/summary/sec33_indicator_grading_preparation/indicator_distribution_reading.csv`中`domain=site_crop`、`metric=ENN`、`weighting=patch_equal`、`algorithm=linear_order_statistics`的8条已核验记录。按数据字典，等权中位数采用常规顺序统计量：奇数个斑块取中间值，偶数个取中间两值的均值，不使用参考像元面积权重。

**Verified**：从`reference_patch_features.csv`的149234条作物记录重新复核，每个完整参考斑块只计一次；生产脚本用pandas中位数，独立检查用Python标准库`statistics.median`。八组ENN中位数原值均为67.082 m，显示67.08 m，不是舍入后才相同。8组的中间两个位置取值均相同，最小值均为60 m；最大值与旧表逐组一致。未剔除单像元或外框接触斑块，无填值或重跑FRAGSTATS。

**Verified**：AREA、SHAPE继续使用`weighting=reference_pixel_area`及加权ECDF左逆，像元累计权重首次达到50%时取值。新旧表逐单元格比较，只有ENN中位数由60.00改为67.08，AREA、SHAPE、全体极值、斑块数、PD、AI、ED均未变化。PD/AI/ED仍追溯到`scope=full`的整站结果。1.3.2之前正文、组成图、方法及结果章节未改。

运行`python -B scripts/test/check_sec13_spatial_enn.py --report verification/sec13-enn-patch-equal-2026-10-12.json`通过，含149234条作物指标与原CSV的身份和值核对、输入哈希、分母及统计口径检查。初次预览发现一行正文单独跨至右栏，随后仅删除第二段一个冗余“也”字，再运行同一检查（不写报告）通过。首份[数据核查JSON](sec13-enn-patch-equal-2026-10-12.json)原位保留，最终源码与PDF哈希见[版面核查JSON](sec13-enn-patch-equal-layout-2026-10-12.json)。

## 正文、表格与编译

正文和表注分别说明AREA/SHAPE面积加权、ENN斑块等权。第二段共性改为八组ENN等权中位数均为67.08 m，仍保留“中位数相同不表示完整距离分布相同”和ENN不同于AI的说明。ENN表示窗口内最近同类异斑块的边界像元中心距离，不是实际田块净空距离。单表、斑块级中的斑块数、类别级PD/AI及三类景观ED的分组不变。

**Verified**：`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`成功，全文8页，表1位于第4页，仍在1.3.2与第2节之间。实际PDF字体核查：表头、单元格和组成图为SimSun/TimesNewRomanPSMT、9 pt；表题和表注保持小五。表宽420.552 bp（14.84 cm），小于17.4 cm版心，固定窄列距不伸展。渲染查看最终第3、4页，整表完整、无文字重叠或裁切，正文无单行跨栏；日志无Overfull/Underfull、缺字或未定义引用。沿用既有SimSun/SimHei粗体替代、xeCJK、caption hypcap及Perl区域设置警告。

最终预览为`output/sec13-enn-equal-final-20261012-{3,4}.png`。初次预览`output/sec13-enn-equal-20261012-{3,4}.png`原位保留。

## 历史保留与边界

新活动表为`tables/sec13_spatial_metrics_enn_equal_rows.tex`；原`tables/sec13_spatial_metrics_enn_rows.tex`及其核查记录原位保留，不再由当前正文引用或生成脚本写入。更换的是作者指定的统计口径，不是否定已有面积加权结果。

**Partially verified**：本轮核对既有ENN值及其等权汇总，没有重算空间距离或恢复全部FRAGSTATS工程参数。C站玉米ENN最大值对应外框接触斑块`ida_2023, PID=69765`的既有限制不变；完整窗口外的同类斑块未参与距离计算，不能将表内距离直接解释为实际农业田块间距。

## 后续通栏排版修订

按作者意见，整表改用`tabular*{\textwidth}`铺满双栏17.4 cm，保留三条主横线及分组表头辅助线。撤去半角标点间距压缩，恢复正常括号留白；`tabcolsep=2pt`并将剩余空间分配至列间，行距系数由1.08调至1.2。PD/(个/100 ha)与ED/(m/ha)分别同行显示，表内字体仍为9 pt宋体和Times New Roman。已将满栏宽、合理间距及指标单位同行要求写入`plan/format-spec.md`。

**Verified**：1.3.2三段正文与逐行底表相对`e90c614`均未变化；149234条作物记录的复核通过。检查期间1.1有独立并行修改进入暂存区，首次默认HEAD前缀比较因此失败，不能据此判定本轮越界。未覆盖该修改；为核对当前工作区，现有检查增加显式`--scope-baseline`选项，运行`python -B scripts/test/check_sec13_spatial_enn.py --scope-baseline INDEX`通过，比较基准在报告中保留。

**Verified**：正常编译完成。当前稿件包含同时进行的1.1修订，共7页；表1在第3页，仍位于1.3.2之后、第2节之前。实测三条主横线宽均为493.228 bp（17.4 cm）；字体仍为9 pt的SimSun与TimesNewRomanPSMT；PD/ED单位没有换行。相邻两作物行基线距约16.848 bp、站点组间约18.84 bp。日志无Overfull/Underfull、缺字或未定义引用；渲染查看整页及表格，列、行、表头和表注无重叠、裁切。既有字体替代及caption警告不变。

源码与PDF哈希及实测记录见[通栏版面核查](sec13-fullwidth-layout-2026-10-12.json)。新预览为`output/sec13-fullwidth-20261012-v1-3.png`，表格局部为`output/sec13-fullwidth-20261012-v1-table.png`；旧预览原位保留。本轮未操作Git暂存或提交，已有暂存内容保持。

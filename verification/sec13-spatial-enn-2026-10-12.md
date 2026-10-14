# 1.3.2共性与差异、斑块数量及ENN核查（2026-10-12）

用途更新：以下记录保留ENN面积加权版本及先前字号调整的核查，不再代表现行口径。作者随后明确ENN按完整参考斑块等权、AREA/SHAPE保持面积加权、图表统一小五字号；现行表和核查见[ENN斑块等权记录](sec13-enn-patch-equal-2026-10-12.md)。旧表和报告原位保留，数据有效性未被否定。

版本说明：本文前部保留首次数据与源码核查过程，文末记录后续授权编译、放大字号及调整表头。初稿按作者决定重组1.3.2，新增斑块数量与ENN，保留PD、AI、ED，并合为8行9列通栏三线表。初稿采用小五号、可伸展列距，斑块数暂列类别级；初稿数据核查时没有编译、提交或推送。现行表内字为五号10.5 pt、固定窄列距，斑块数已移入斑块级表头；同站ED仍跨两作物行合并。

正文为三个连续段落：单像元斑块的数量/面积占比与面积加权理由；同类聚集、玉米斑块大小和近邻距离的四站共性；大豆大小变化及C站形状、数量密度和边缘密度的差别。面积占比仍由1.3.1承担，本节不提前解释精度差异或迁移退化。

## 数据与表格

- **Verified**：完整参考表187372条三类记录，唯一键为`target,PID`；表格仅使用其中149234个玉米、大豆斑块。A/iw_2023、B/iw2_2023、C/ida_2023、D/il_2023，原标签1/2/3对应玉米/其它地类/大豆。各站总像元数6553600、整站面积589824 ha；逐组数量、像元和、AREA=像元数×0.09 ha与基础汇总一致。
- **Verified**：AREA、SHAPE沿用`crop_patch_distribution_reading.csv`中参考像元面积权重的记录；ENN沿用`indicator_distribution_reading.csv`的`domain=site_crop`、`weighting=reference_pixel_area`、`algorithm=inverse_weighted_ecdf`八条记录。24组“站点×作物×指标”全部由逐斑块记录复核，无缺失或剔除。加权中位数满足“小于该值的累计像元数<50%，小于等于该值的累计像元数≥50%”，不是均值，也不是AREA_AM；括号为全部斑块极值。
- **Verified**：单像元斑块占相应作物斑块数44.308437…%～54.640212…%，占相应作物面积0.232305…%～0.712544…%。面积分母不是整站面积。逐组单像元数、斑块数、像元数与`crop_patch_support_and_limitations.csv`一致；单像元及外框接触斑块全保留。
- **Verified**：PD、AI、ED与上游`background_class.csv`和`background_landscape.csv`中`scope=full`、`verified=True`结果一致。PD=作物斑块数/整站589824 ha×100，AI为类别聚集指数，ED为整站三类边缘密度。未混入128×128图块尺度结果。
- **Verified**：独立检查以标准CSV读取、按未舍入同值汇总像元权重后求中位数，与生产脚本逐行排序法一致；149234条作物记录的AREA、SHAPE、ENN、类别及LID/PID又与四份原始结果CSV逐条一致，原CSV的哈希与转换清单吻合。详细输入哈希、极值PID及本次结果见[JSON](sec13-spatial-enn-2026-10-12.json)。未重新运行FRAGSTATS或生成距离。

## 正文比较与解释边界

**Verified**：以未舍入值比较，八组AI范围91.217658…%～93.923026…%，玉米AREA加权中位数116.91～130.95 ha，大豆63.27～114.39 ha。两作物中位数差为A 24.48、B 67.68、C 24.12、D 7.47 ha（仅此处显示时舍入）；B最大、D最小。C站两作物的SHAPE加权中位数及PD最高、AI最低，整站ED最高65.529734… m/ha；两作物AREA加权中位数均非最低。正文没有把斑块数和PD当作独立证据。

**Verified**：八组ENN的原始加权中位数均为60，不是舍入后恰好相同。最近同类异斑块的像元中心距离定义依据既有数据字典、`feature-selection-and-freeze.md`及64例历史核查。30 m栅格按8邻域合并同类像元后，不同同类斑块最近边界像元中心的最小可能距离为2个像元即60 m；它不是田块边缘的净空距离，也不能替代AI或说明完整距离分布相同。

**Verified**：八组AREA、SHAPE最大值均未接触外框。ENN最大值中，C站玉米对应`ida_2023, PID=69765`，780.5767 m，接触外框；其它七组ENN最大值斑块未接触外框。三指标各组最小值均包含外框接触斑块。全部指标描述研究窗口内参考斑块，外框及窗口外同类斑块仍限制解释；未据极值推论实际农业田块。

**Partially verified**：本轮重新核查已有结果间的一致性，没有恢复全部FRAGSTATS工程参数，也没有重新执行ENN的空间距离计算。历史64例核查不等同于本轮全量重算。

## 源码、历史保留与版面

运行`python -B scripts/generate_sec13_spatial_tables.py`写入新的`tables/sec13_spatial_metrics_enn_rows.tex`；现行脚本的`--check`只读回算并逐字核对新表。旧`tables/sec13_spatial_metrics_rows.tex`、更早双表及分布表保留原字节，不再由本节引用或当前脚本写入。现有PD、AI、ED有效性没有改变。

运行`python -B scripts/test/check_sec13_spatial_enn.py --report verification/sec13-spatial-enn-2026-10-12.json`，完成上述独立数据检查、九列表格8行及ED合并单元格核对、正文三段与未舍入排序检查、引用键及LaTeX环境/花括号配对检查。1.3.2之前正文与HEAD逐字一致，旧表、组成图、方法、结果及正式精度数据不变；`git diff --check`通过。**Verified**。

初稿采用本机宋体和Times New Roman的9 pt字体度量，估算表格含列距约440.64 bp（15.54 cm），小于17.4 cm版心493.23 bp。该值仅用于初稿单表设计。初稿核查时的实际版面状态为 **Not verified**；后续实际编译结果见下节，旧JSON中的`layout_status`仍表示当时状态。

## 后续授权编译、放大字号及表头调整

作者随后要求“编译提交”，并在首次编译后指定斑块数放入斑块级、缩小列间距、放大字。现行表头为斑块级AREA/SHAPE/ENN/斑块数、类别级PD/AI、景观级ED；这一展示分组不改变斑块数的含义，它仍是该站该作物全部参考斑块的总数。八行数值保持不变。

表内字体由9 pt增至五号10.5 pt；改用不伸展的`tabular`，`tabcolsep=1.5pt`，相邻列固定空白约3 pt，中文括号采用半角标点间距以收紧空白。括号字符及“中位数（最小值～最大值）”表达不变，表题和表注仍用小五号。字号依据作者最新决定调整，未改其它图表字号。

**Verified**：运行`python -B scripts/test/check_sec13_spatial_enn.py --report verification/sec13-spatial-enn-large-2026-10-12.json`，重新核对149234个作物斑块、加权中位数、全体极值、斑块数量、PD/AI/ED来源及表格源码。该脚本本身不编译，其JSON中版面仍记为`Not verified`；独立编译与视觉结果见[版面核查JSON](sec13-spatial-enn-layout-2026-10-12.json)。首次核查JSON原位保留。

**Verified**：执行`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`成功，全文8页。PDF第4页表1保持完整单表，表头及数值的实际字号均为10.5 pt，三条主横线宽486.659 bp（17.17 cm），小于493.228 bp（17.4 cm）版心。8个斑块数按原顺序完整显示；表格与第2节之间顺序正确。渲染并查看第4页，未见文字重叠、裁切或缺失，表注为3行。编译日志无Overfull、Underfull、缺字或未定义引用；仍有既有SimSun/SimHei粗体替代、xeCJK字体族重设、随文caption的hypcap及Perl区域设置警告。

放大前源码、整表和两个脚本的字节快照保存在`output/archive/2026-10-12/source-backups/sec13-enn-20261012-before-large/`，`manifest.json`记录原路径、快照路径、原因和SHA-256；未删除或覆盖历史预览。第一次编译的第3、4页预览为`output/archive/2026-10-12/sec13-layout/sec13-enn-20261012-compile-v1-{3,4}.png`，放大后的表格预览为`output/archive/2026-10-12/sec13-layout/sec13-enn-20261012-large-v1-4.png`。源码、数据及版面验证分别记录，不将旧报告的哈希当作新排版的哈希。

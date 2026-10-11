# 1.3 空间特征表格核查（2026-10-11）

**版本说明**：下文至“后续授权编译与视觉检查”记录此前两张通栏表的生成和检查，作为历史版本保留。当前正文已按作者后续决定改为一张分斑块级、类别级和景观级的整表；现行结果见文末“整表修订与复核”。

作者最新决定将1.3景观格局改为两张表：完整参考斑块AREA、SHAPE的斑块等权最小值／中位数／最大值；整站作物类别PD、AI和整站三类景观ED。组成图与2023年整站面积占比沿用。旧双权重表、旧PD／AREA_MN／AI／ED表和核查记录原位保留为历史成果；此前撤回的是旧表作为主表的选择，并非判定PD、AI、ED数据无效。本次未重跑FRAGSTATS，未改动正式F1。

修改入口为`sections/02_data.tex`的1.3、新增`tables/sec13_patch_extrema_rows.tex`及`tables/sec13_landscape_metrics_rows.tex`和对应脚本`scripts/generate_sec13_spatial_tables.py`。同步更新`figures/data-manifest.md`、`plan/progress.md`和`plan/outline.md`的1.3条目，并给旧v2核查及撤回说明补充历史用途。旧表和旧核查数值保留，1.1、1.2、方法及结果正文未改。

## 数据与层级

- 逐斑块：`results/processed/sec33_reference_patch_types/reference_patch_features.csv`，四站三类共187372个完整参考斑块；玉米、大豆共149234个。每个`target+PID`唯一，所有特征有效且AREA、SHAPE非空。每组逐斑块数量与像元和分别对上`class_background_full_scope.csv`、`reference_composition.csv`及`crop_patch_support_and_limitations.csv`；AREA等于像元数乘0.09 ha。身份映射为A/iw_2023、B/iw2_2023、C/ida_2023、D/il_2023。
- AREA、SHAPE：8组逐斑块最小值／中位数／最大值分别与`crop_patch_distribution_reading.csv`中`weighting=patch_equal`的16条已核验记录一致；不是面积加权分位数。逐组作物斑块数依次为A 15146/14695、B 14460/16039、C 29837/27894、D 16756/14407（玉米/大豆）。最小值和最大值是全体斑块在研究窗口内的跨度，不表示多数斑块的范围。
- 极值与外框：8组AREA最小值均为单像元0.09 ha；8组SHAPE最小值和中位数均为1.00。两项指标每组的最小值都包含外框接触斑块，两项最大值对应的斑块均未接触外框。微小及外框接触斑块均保留；窗口边界仍限制完整农业田块的解释。
- PD、AI、ED：`class_background_full_scope.csv`的12条类别记录及`landscape_background_full_scope.csv`的4条景观记录均与上游`background_class.csv`和`background_landscape.csv`的`scope=full`、`verified=True`记录一致。PD按类别斑块数／整站589824 ha×100核对，单位为个/100 ha；AI为类别级百分数，ED为整站三类景观的m/ha，不作为某一作物的专属值。128×128图块数据未进入两表。

## 本次验证

**Verified**：运行`python -B scripts/generate_sec13_spatial_tables.py`生成两张8行数据表，随后以`--check`模式重新读取底表、回算统计并逐字核对已生成表格；站点与作物键、斑块数、像元数、单位、full范围、最小值—中位数—最大值顺序、两位小数显示和ED两行合并均检查。另以独立CSV读取和`statistics.median`复核8组逐斑块统计、两表显示值、PD整站分母及正文所述未舍入排序。`git diff --check`通过；1.1、1.2与提交版逐字一致，FRAGSTATS引用键存在，两个`table*`和`tabular*`环境各自配对。

**Partially verified**：上述校验是现有数据、源码和LaTeX结构的核查，不是FRAGSTATS原工程重算。遵照本次要求未编译；新版两张通栏表的实际版宽、分页和浮动位置尚未验证。历史7页PDF仅对应旧版双权重表。

## 后续授权编译与视觉检查

作者随后要求编译并查看效果。运行`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`成功生成8页`main.pdf`；`main.log`无Overfull/Underfull、未解析交叉引用或编译错误。渲染并查看第2至4页，组成图仍在第2页，两张通栏表均在第3页；表头、8行数据、表注和三线完整，字迹清楚，无裁切或重叠。

**Partially verified**：浮动位置尚不理想：第2页已进入方法章，第3页才出现1.3两表，且第3页下半部留白较多。全文最终排版未解决。日志保留已有宋体／黑体粗体替代警告，BibTeX仍提示FRAGSTATS软件条目类型不被`unsrtnat`识别及年份为空；本次未修改文献元数据。页面预览为`output/sec13-current-20261011-2.png`至`-4.png`。

## 整表修订与复核

作者随后将1.3景观格局改为一张整表，列头按斑块级（AREA、SHAPE）、类别级（PD、AI）、景观级（整站ED）分组。AREA和SHAPE每格采用“中位数（最小值～最大值）”，例如A站玉米AREA为`0.18（0.09～455.40）`；括号内不是四分位区间。ED在同站玉米和大豆两行之间合并。`sections/02_data.tex`现在仅引用`tables/sec13_spatial_metrics_rows.tex`，原`tables/sec13_patch_extrema_rows.tex`与`tables/sec13_landscape_metrics_rows.tex`原位保留为历史双表数据行；双表版页面预览亦保留。

**Verified**：运行`python -B scripts/generate_sec13_spatial_tables.py`生成整表数据行，`--check`重新从逐斑块、类别和景观底表核对8组数值、统计顺序、站点与作物身份、`scope=full`、整站PD分母及ED合并。逐斑块总数仍为149234；未筛除单像元或外框接触斑块，未重跑FRAGSTATS。运行`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`成功生成7页`main.pdf`；日志无Overfull/Underfull或未解析引用。查看`output/sec13-combined-20261011-2.png`和`-3.png`，新表列宽、数字、表注和三线完整，无裁切或重叠。

**Partially verified**：浮动表仍位于第3页页顶，第2页已进入研究方法，尚未解决图表相对于方法章的阅读顺序。新表下方接排方法正文，双表版第3页大块留白已消失。字体粗体替代及FRAGSTATS BibTeX元数据警告属于既存问题，本轮未修改。`git diff --check`通过。

## 三类地物整表增补与复核

作者进一步决定将“其它”纳入同一张表。当前表为四站×三类共12行，站点和整站ED各跨三行；玉米、大豆8行的原数值保留。“其它”AREA、SHAPE直接从`results/processed/sec33_reference_patch_types/reference_patch_features.csv`按站点、类别逐斑块等权派生，不冒称`crop_patch_distribution_reading.csv`已有该类别的分布汇总。四站斑块数依次为7451、10557、12530、7600，对应像元数1169135、2256417、1816209、1546343，均与类别级和组成底表吻合。PD、AI沿用已核验的整站`scope=full`类别记录；ED仍为各站三类景观的唯一值。

四站“其它”AREA中位数均为0.09 ha，最大值依次为101427.30、198917.46、155093.22、136116.36 ha；SHAPE中位数均为1.00，最大值依次为174.63、132.53、161.72、135.38（按两位小数显示）。四个最大AREA和最大SHAPE均来自接触研究窗口外框的斑块，不能解释为完整实际田块；最小值也各有外框接触斑块。“其它”由不同CDL类别合并，它的超大连通区尤其受重分类和窗口边界影响。

**Verified**：运行`python -B scripts/generate_sec13_spatial_tables.py --check`，脚本从187372个逐斑块记录回算12行统计、类别级PD/AI和整站ED，逐字核对当前LaTeX行文件；核查站点和类别身份、面积单位、斑块数、像元数、最小值—中位数—最大值顺序及外框标志。运行`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`成功生成7页`main.pdf`；`main.log`未见Overfull/Underfull或未解析引用。渲染并查看第3页`output/sec13-threeclass-20261011-3.png`，12行、三线、表注、ED合并单元格与版心均完整，没有裁切或重叠；`git diff --check`通过。

**Partially verified**：表仍浮于第3页页顶，第2页已经进入方法章；全文定稿时需处理阅读顺序。FRAGSTATS原工程未重算，字号替代警告仍存在；这两项均非此次数据增补造成。

## 图表顺序与类别称谓调整

作者本次确定正文、表格、图例统一称“玉米、大豆、其它地类”。图2置于1.3.1与1.3.2之间；表1改为1.3.2末段后的随文通栏表，位于第2节之前。此前使用“其它”的未提交修改已按此决定更新；旧双表、8行表及各次试排图保留作历史核查，不更改科学数值。

**Verified**：`python -B scripts/generate_sec13_spatial_tables.py --check`从187372个完整参考斑块及整站汇总回算12行，逐字核对当前行文件，斑块数、数值、类别身份及外框标志均通过。`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`成功生成7页PDF；第2页图2位于1.3.1论述之后、1.3.2标题之前，第3页表1位于1.3.2末段之后、第2节标题之前。渲染查看`output/sec13-layout-inline-2.png`和`output/sec13-layout-inline-3.png`，图例、表格、表注完整，无裁切重叠；`git diff --check`通过。原FRAGSTATS工程未重算；编译仍有既存字体替代警告，以及随文表格的`hypcap`提示，不影响本次图表正文显示。

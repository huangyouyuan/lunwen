# 当前图表字体核查（2026-10-12）

**Verified**：检查当前正文实际引用的5幅图和2张表，包括图内标注、图题、子图题、图例、表头、表体和表注。正文PDF中的实际字号均为小五9 pt，中文为SimSun，字母数字为TimesNewRomanPSMT；相关字体已嵌入PDF。字体统计与文件SHA-256见[机器核查记录](figure-table-fonts-2026-10-12.json)。

## 发现与修正

- 表2的12个迁移箭头原由`$\rightarrow$`生成，使用CMSY9数学符号字体；改为文本箭头`→`后，已在实际PDF中确认与站点字母同为Times New Roman、9 pt。同步修改`tables/table2_cross_site_f1_12paths_rows.tex`和`scripts/generate_core_tables.py`，未重算或改写F1底表。
- 其它图表未发现字体或字号偏离现行要求，无需重新绘图。图1的4张PNG和图4的8张分类面板不含图内文字，其子图题、图例和图题由LaTeX排版，均已检查。
- `plan/format-spec.md`中两处表题字体仍写模板原规定的黑体，与作者最新要求和当前实现不一致，已改为宋体小五，并保留模板原规定的来源说明。

## 实际PDF检查

| 对象 | 当前页码 | 中文 / 字母数字 | 实际字号 | 检查范围 |
|---|---|---|---|---|
| 图1 四站地物分类图 | 2 | 宋体 / Times New Roman | 9 pt | 四个子图题、图例、图题；分类面板无文字 |
| 图2 地物组成 | 3 | 宋体 / Times New Roman | 9 pt | 轴标题、刻度、数值、图例、图题 |
| 表1 景观格局 | 4 | 宋体 / Times New Roman | 9 pt | 表题、分层表头、8行数据、表注 |
| 图3 站内F1 | 5 | 宋体 / Times New Roman | 9 pt | 两个子图的坐标及数值、子图题、模型图例、图题 |
| 图4 D站分类对比 | 6 | 宋体 / Times New Roman | 9 pt | 八个子图题、图例、图题；分类面板无文字 |
| 表2 跨站F1 | 7 | 宋体 / Times New Roman | 9 pt | 表题、表头、12条路径及平均行、表注，含修正的箭头 |
| 图5 F1差值热力图 | 7 | 宋体 / Times New Roman | 9 pt | 六个子图的坐标及数值、子图题、色标刻度与标题、图题 |

图2、图3和图5的源PDF与嵌入正文后的文字均为9 pt，未因插图缩放变小。使用PyMuPDF提取实际字形字体和字号，并用Poppler渲染第2至7页逐页查看；修正后重新渲染并查看第7页。未发现图表文字重叠、截断或缺字。预览为`archive/manuscript/2026-10-12/font-audit/font-audit-20261012-before-{2..7}.png`及`archive/manuscript/2026-10-12/font-audit/font-audit-20261012-after-7.png`。

执行`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex`，返回目标已更新；实际PDF已包含12个新文本箭头。当前日志无Overfull、Underfull、Missing character、未定义引用或编译错误。既有标题粗体替代、xeCJK字体重定义、随文caption的hypcap提示及Perl locale提示不属于本次图表字体问题。

## 数据与范围保护

- 从未舍入的`results/summary/f1_raw_scale/cross_site_crop_f1_summary.csv`独立核对表2的72个路径F1和6个平均值，共78格，全部一致。表体与修改前相比仅12个箭头的LaTeX写法变化。
- 所有当前图件、F1汇总CSV、表2的CSV、表1表体、`main.tex`、方法与结果正文均与本次起始快照相同。未运行FRAGSTATS或精度生产流程。
- 起始时已有暂存与未暂存修改。本次未暂存、提交或推送；核查时Git暂存区与起始快照相同。工作期间1.1另有独立修订，原样保留；`sections/02_data.tex`从图1入口起的内容未变。第2至8页提取文本与起始PDF相同；第1页变化对应独立1.1修订，不归入本次字体修改。
- 收尾检查时，独立1.1任务已形成提交`fce1b87`，因此暂存区相对起始快照发生变化；当前暂存区为空。本次字体修订仍在工作区，PDF哈希仍与上述字体核查一致。
- 修改前PDF、日志及相关源码快照保存在`archive/manuscript/2026-10-12/source-backups/font-audit-20261012-before-sources/`，原路径、快照路径关系及哈希见该目录`manifest.json`，旧文件和预览均保留。

本次核查的PDF为8页，SHA-256为`8a0194369c716438b7536efaed92fd75214425e942fd646b033fefadb641ac05`。此前7页及表1第3页的记录属于上一轮排版预览。**Not verified**：本次未全面审查分页留白、论文科学结论或未被正文引用的历史图件；不将本次字体通过等同于整篇定稿通过。

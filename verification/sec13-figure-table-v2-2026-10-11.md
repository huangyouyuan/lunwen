# 1.3 组成与完整参考斑块分布核查（2026-10-11）

当前正文见 [02_data.tex](../sections/02_data.tex)。三类面积占比图沿用四站分组、统一配色和数值标注；分布表采用站点合并行和分组表头，报告当前完整参考斑块的 AREA、SHAPE。旧稿的指标选择、数值和景观排序不作为当前正文依据。[首次记录](sec13-figure-table-2026-10-11.md)及旧表保留，用途见[撤回说明](sec13-figure-table-2026-10-11.withdrawn.md)。

## 当前证据与口径

- 组成：[reference_composition.csv](../results/summary/sec13_sec31_foundations/reference_composition.csv)，2023 年整站三类参考像元为分母，各站 6,553,600 个像元。1 像元为 0.09 ha；A/B/C/D 对应 iw_2023/iw2_2023/ida_2023/il_2023。
- 分布：[crop_patch_distribution_reading.csv](../results/summary/sec13_sec31_foundations/crop_patch_distribution_reading.csv)，四站两作物、AREA/SHAPE、斑块等权/参考像元面积加权，共 32 组。数量分位数使用线性次序统计；面积加权分位数使用加权经验分布的逆函数。
- 表格：[sec13_patch_distribution_rows.tex](../tables/sec13_patch_distribution_rows.tex)，8 行站点—作物组合，各列显示中位数（Q25～Q75）和斑块数。
- 图件：[组成图 PDF](../figures/study_area/fig_sec13_composition.pdf)／[PNG](../figures/study_area/fig_sec13_composition.png)。生成时的图宽约 8.31 cm，图例和图题由 LaTeX 排版。

参考对象为整幅标签上的 8 邻域同类连通斑块，不等同于实际农业田块。逐斑块输入来自 [reference_patch_features.csv](../results/processed/sec33_reference_patch_types/reference_patch_features.csv)，原 FRAGSTATS 表及身份追溯沿 [数据字典](../results/summary/sec33_reference_patch_types/data_dictionary.md) 和 [基础证据清单](../results/summary/sec13_sec31_foundations/manifest.json)。

## 本次实际复核

Verified：重新读取逐斑块底表，核对 target＋PID 唯一、总斑块 187,372 个、两作物斑块 149,234 个、AREA 与参考像元数×0.09 的关系；逐站逐类别汇总恢复组成表的 12 项像元和面积。

Verified：从逐斑块 AREA、SHAPE 及像元权重独立恢复 32 组分布的 96 个四分位数；8 行 LaTeX 表格中的斑块数、作物名称和两位小数显示均与底表一致。斑块等权 AREA 中位数为 0.09～0.18 ha，面积加权为 63.27～130.95 ha；C 站玉米、大豆面积加权 SHAPE 中位数为 2.07、1.91，B 站大豆面积加权 AREA 中位数为 63.27 ha。

Verified：[v2 JSON](sec13-figure-table-v2-2026-10-11.json) 中的 6 项输入及 3 项输出 SHA-256 全部与当前文件一致；实际查看了组成图 PNG。正文引用当前表格与图件，FRAGSTATS 引用键存在，figure、table*、tabular* 环境配对；`git diff --check` 通过。

本次逐斑块底表 SHA-256：`fdfe31beefcbe9a1b0661ee76d48fe240b33cd88ae5027ac6fdcc3af81e857ab`。

本次 02_data.tex SHA-256：`edf5d7aa18019852fc8eb46549a119278c9068629c441514aeb86e6df70331b7`。

## 验证边界

整体为 Partially verified。上述数据与源文件核对为 Verified；全文编译、最终分页和通栏表排布为 Not verified。本次没有重跑 FRAGSTATS、距离或预测；原工程参数与地理元数据的历史核验范围不升级。组成和斑块分布仅描述参考空间背景，不构成分类误差或跨站差距的因果解释。

## 后续授权编译（2026-10-11）

用户要求编译后，以 `latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 生成 7 页 [main.pdf](../main.pdf)。首次编译发现表格输入后的 `bottomrule` 触发 `Misplaced noalign`，将 02_data.tex 中表格行文件的输入改为可展开的 TeX 输入后通过，表内数据未变。修订前正文、旧编译产物及日志均保留于 [本次编译目录](../output/build-20261011-190347/)，快照清单记录路径与 SHA-256；上面的正文哈希及未编译状态保留为此前核查记录。

Verified：最终编译退出码 0，无 Overfull/Underfull、缺字及未解析的引用；渲染并查看全部 7 页，组成图位于第 2 页，完整 AREA/SHAPE 表位于第 3 页，表头、8 行数据、底线及表注均完整。当前 PDF、源码与逐页预览哈希见 [预览清单](../output/preview-manifest.json)及[编译清单](../output/build-20261011-190347/build-manifest.json)。

Partially verified：全文定稿排版与参考文献格式。现有浮动体边界使第 4 页右栏留白；仍有宋体、黑体粗体替代警告，以及 FRAGSTATS 的 software 条目不被 unsrtnat 支持、年份字段为空的 BibTeX 警告。本次未改变文献元数据或扩大正文修改范围。

# 整图FRAGSTATS原始结果表格

本目录提供可直接用Excel、WPS或CSV查看器打开的UTF-8 CSV，供版本追溯。原始文件仍保留在`legacy/experiment-results/label/`，没有重算或覆盖。CSV保留原字段及数值文字精度，只去掉字段周围的排版空白。来源、逐表记录数、核查状态及输入/输出SHA-256见[转换清单](conversion_manifest.json)。

## 单斑块指标原表（real）

| 表格 | 原文件 | 数据行数 | 内部LID对应站点 |
|---|---|---:|---|
| [2023iw_patch.csv](2023iw_patch.csv) | 2023iw.patch | 76055 | A站37292行及D站38763行 |
| [2023iw2_patch.csv](2023iw2_patch.csv) | 2023iw2.patch | 41056 | B |
| [2023ida_patch.csv](2023ida_patch.csv) | 2023ida.patch | 70261 | C |
| [2023il_patch.csv](2023il_patch.csv) | 2023il.patch | 38763 | D |

每行一个软件输出的参考连通斑块。`LID`为整幅标签身份，`PID`为该LID内斑块编号，`TYPE=cls_1/cls_2/cls_3`分别是玉米、其他、大豆。`AREA`单位ha；`GYRATE`、`ENN`单位m；`SHAPE`、`CONTIG`无量纲。所有数值、行序和重复记录均按原表保留，未增加聚类标签或误差统计。

**不要直接合计四份表的行数作为唯一斑块数。** `2023iw_patch.csv`内D站38763行与`2023il_patch.csv`重复；本轮分析按LID/PID核对后去重，得到187372个三类参考斑块。本目录保留原始重复，便于追溯。这里的斑块不是128×128训练图块，也不等同于真实农业田块。

## 原邻接矩阵（real，仅整理表示）

四份`2023*_adjacency.csv`将对应`.adj`中的矩阵块展开为`LID,CLASS_FROM,CLASS_TO,ADJACENCIES`。原矩阵每个单元格均保留，包括同类、异类及`background`列；转换程序将其恢复为原矩阵逐项核对。`2023iw_adjacency.csv`同样包含D、A两个景观块。

这些数值是原FRAGSTATS邻接计数，不是模型分类混淆矩阵，不据此把研究区外框当作真实地物类别边界。

## 已有完整标签背景表（历史derived）

`完整标签类别级指标.csv`、`完整标签景观级指标.csv`和`完整标签邻接矩阵.csv`来自已有`fragstats_results/`中`scope=full`的表格，原字段、原值及原行序均保留。它们含历史`reported/recomputed/verified`列，不是本轮重新运行FRAGSTATS的结果，也不是单斑块聚类输入。表内历史路径及验证标记不表示这些原路径本轮已全部复核。

## 转换核查

执行`python -B scripts/export_sec33_reference_patch_raw_tables.py`：四份单斑块CSV共226135行，四份邻接长表共60行，三份背景CSV共64行，11份表全部逐字段回读一致，状态**Verified**。新转换没有浮点运算，没有排序、筛选或去重，没有缩减数值精度。已有分析所读取输入的SHA-256同时与其prepare清单一致；所有本地原文件转换前后哈希相同。

本目录及本轮交付文件通过仓库`.gitattributes`保留原始字节，防止Git自动改写换行后使SHA-256失效。

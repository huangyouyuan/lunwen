# 1.3 正文与图表核查（历史撤回记录，2026-10-11）

> 下文保留首次版本的原核查内容；其中 PD、AREA_MN、AI、ED 表作为 1.3 主表的选择已撤回，不再代表当前正文。底表本身未被判定无效。当前有效核查见 [v2 说明](sec13-figure-table-v2-2026-10-11.md)及 [v2 清单](sec13-figure-table-v2-2026-10-11.json)；原因见 [撤回说明](sec13-figure-table-2026-10-11.withdrawn.md)。

## 本轮范围

按作者最新要求补齐 [1.3 正文](../sections/02_data.tex)，模仿旧 Word 的三类分组柱形图、“类型级别／景观级别”表头及连续比较段落。图按现行单栏规范横排；表中站点和整站 ED 各合并三行。只使用 2023 年完整参考标签结果，未沿用旧稿的多年平均题注、C/D 错位或景观排序。

生成入口：[generate_sec13_figure_table.py](../scripts/generate_sec13_figure_table.py)。

- [组成图 PDF](../figures/study_area/fig_sec13_composition.pdf)／[PNG](../figures/study_area/fig_sec13_composition.png)
- [景观指数表数据行](../tables/sec13_landscape_rows.tex)
- [数据检查及输入、输出 SHA-256](sec13-figure-table-2026-10-11.json)

## 数据与呈现

Verified：三份输入底表与基础证据 manifest 的 SHA-256 一致；四站映射和 12 个站点—类别键一致，三类像元及面积均恢复整站总量。图中百分比以整站面积为分母；各站两作物合计占比为 A 82.1604%、B 65.5698%、C 72.2868%、D 76.4047%，显示时保留两位小数。类别面积／斑块数量恢复 AREA_MN，斑块数量／整站面积恢复 PD。

Verified：组成图共 12 个数值标注，无相互遮挡或越出图框；9 pt 字体，图框 7.6×5.7 cm，完整图宽约 8.31 cm，按原尺寸可放入 8.325 cm 单栏。已查看生成的 PNG；图例和图题在 LaTeX 中排版。景观表保留三类的 PD、AREA_MN、AI 共 36 个数值及 4 个整站 ED，显示精度为两位小数。

正文比较依据：玉米占比 39.97%～45.39%，大豆占比 23.49%～36.77%；C 站两种作物 PD 最高、AREA_MN 最低，整站 ED 最高；A 站两种作物 AI 最高；B 站玉米和大豆 AREA_MN 分别为 17.17、8.64 ha；D 站两种作物 AREA_MN 均在 14～15 ha，ED 最低。各项只描述参考空间背景。

数据追溯沿用 [基础证据目录](../results/summary/sec13_sec31_foundations/README.md)的输入链和 [既有完整参考斑块核查](sec33-reference-patch-types-2026-10-07.md)。本轮未重跑 FRAGSTATS，也未扩大原工程参数、地理元数据的核验范围。

## 验证边界

整体状态：Partially verified。数据、图件及源文件核对为 Verified；整篇 LaTeX 编译与表格的最终分页排布为 Not verified（按规则本轮不自动编译）。未改动 1.1、1.2、3.1、3.2，未重算科学结果、未删除文件、未提交或推送。此前基础证据目录保持原样。

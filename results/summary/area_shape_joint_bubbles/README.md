# 面积—形状联合气泡图：用途入口

2026-10-12。本次仅作完整参考斑块联合分布统计与探索绘图，未修改论文正文或既有科研结果。

**当前交付为v3**：两个7.6×7.6 cm正方形绘图区，气泡圆面积及占比图例统一为v2的2倍；保持严格正比，不额外设置最小气泡下限。统计CSV与v2逐字节一致。

- [统计口径与复现说明](../area_shape_joint_bubbles_v3/README.md)
- [联合分档汇总CSV](../area_shape_joint_bubbles_v3/area_shape_joint_bins.csv)
- [八组闭合检查](../area_shape_joint_bubbles_v3/closure_checks.csv)
- [高清PNG](../../../figures/exploratory/area_shape_joint_bubbles_v3/fig_area_shape_joint_bubbles.png)
- [矢量PDF](../../../figures/exploratory/area_shape_joint_bubbles_v3/fig_area_shape_joint_bubbles.pdf)
- [独立数值及PDF核查](../area_shape_joint_bubbles_v3/verification.json)
- [实际查看与交付记录](../area_shape_joint_bubbles_v3/visual-review.md)

## 保留的过程文件

| 位置 | 用途与状态 |
|---|---|
| 初次汇总的两份CSV | 已按原路径结构移入下方归档；统计内容与v3一致，保存首次汇总记录 |
| v1图件、统计和预览 | 已归档。第一轮完整导出，存在轴标签与子图题间距过小的问题；其历史Verified仅覆盖当时写明的范围 |
| v2图件、统计和预览 | 已归档。上一轮绘图区7.6×5.7 cm；统计CSV及比例清单仍作为v3只读基线，活动脚本已改读归档位置 |
| `results/summary/area_shape_joint_bubbles_v3/`及同名图件、预览目录 | 当前正方形与圆面积2倍排版，数据及口径不变；全部169个非零气泡、图例及分档边界经数值和实际导出核查 |

旧版集中放在[归档入口](../../../archive/2026-10-12-area-shape-bubbles/README.md)；[迁移清单](../../../archive/2026-10-12-area-shape-bubbles/archive-manifest.json)记录28份移动文件和4份入口更新前快照的原路径、新路径、用途及SHA-256。全部保留原字节，没有删除文件。本次归档未改变v3图件、统计CSV或论文正文。

v3修订前的绘图脚本、独立核查脚本和本入口均已按原字节保存，见[快照与SHA-256映射](../../../output/archive/2026-10-12/area-shape-square-before/manifest.json)。v2清单中的代码哈希对应这些历史快照，当前活动脚本已切换v3；历史README里的v2绘图/核查命令不能当作当前活动入口。

历史manifest和交付清单保留生成时内容，旧路径按迁移清单解析；活动核查脚本支持这种原路径及哈希映射。当前执行命令仍见v3的README，归档源码只供审阅。

# 预览与归档入口

本目录存放页面预览和核查备份。正式论文图件在[figures](../figures/)，最近核查的8页稿件已保存为[可随Git传递的PDF](previews/2026-10-12-figure23-bars/manuscript.pdf)，与本地`main.pdf`在本次交接时哈希一致。

## 最新预览

最近一次图2、图3柱形样式修订已编译并查看以下两页；这两张图对应同一份8页PDF，不代表整篇论文均已定稿。

- [第3页：图2及1.3.2正文](previews/2026-10-12-figure23-bars/figure23-bars-20261012-3.png)
- [第5页：图3及相邻正文](previews/2026-10-12-figure23-bars/figure23-bars-20261012-5.png)

对应PDF和图片哈希见[当前预览清单](preview-manifest.json)，尺寸、字体及数据检查见[图2/图3核查](../verification/figure23-bars-2026-10-12.md)。若后续修改稿件，以清单中的PDF哈希判断这些预览是否仍对应当前版本。

## 历史预览

[2026-10-12归档索引](archive/2026-10-12/README.md)按研究区、1.1润色、1.3表格、字体检查等任务收纳此前散放的图片。文件原名和内容均保留；原路径、新路径、原因及SHA-256见[迁移清单](../verification/output-preview-archive-2026-10-12.json)。

已完整纳入Git的修改前备份：

- [图表字体检查前备份](archive/2026-10-12/source-backups/font-audit-20261012-before-sources/)，12个文件，含原PDF、日志和暂存补丁。
- [图2/图3样式统一前备份](archive/2026-10-12/source-backups/figure23-bars-20261012-before/)，20个文件，含原图件、PDF、日志和源码。

两组原始清单和源码内容不变，旧路径按[收尾迁移清单](../verification/output-handoff-closeout-2026-10-12.json)解析；源码仅供历史审阅，不作为执行入口。此前已纳入版本的成组资料仍在原位置：

- [2026-10-11编译与修改前备份](build-20261011-190347/)
- [ENN表放大前备份](sec13-enn-20261012-before-large/)

后续页面预览放入`previews/<日期-任务>/`，每次更新清单和本入口；历史版本经用途与引用核对后按任务归档，不再把PNG平铺在根目录。

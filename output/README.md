# 预览与归档入口

本目录存放页面预览和核查备份。正式论文图件在[figures](../figures/)，2026-10-13统一F1展示后的8页稿件已保存为[可审阅PDF](previews/2026-10-13-f1-percent/manuscript.pdf)，与当前本地`main.pdf`哈希一致。2026-10-14按作者明确指令随本次提交保存。

## 最新预览

2026-10-13已将F1及标准差改为百分数、差值改为百分点，重新编译8页并渲染全页。重点逐页检查第4—7页，其余页结合总览核对；此次验证限于F1展示及受影响版面，不代表论文已定稿。

- [第4页：方法中的F1定义](previews/2026-10-13-f1-percent/page-4.png)
- [第5页：本站F1条形图及3.1正文](previews/2026-10-13-f1-percent/page-5.png)
- [第6页：3.2正文](previews/2026-10-13-f1-percent/page-6.png)
- [第7页：跨站均值±标准差表及六幅差值热力图](previews/2026-10-13-f1-percent/page-7.png)
- [全部8页预览目录](previews/2026-10-13-f1-percent/)

对应PDF和图片哈希见[当前预览清单](preview-manifest.json)，数值、字体及版面检查见[F1展示核查](../verification/f1-display-2026-10-13/README.md)。若后续修改稿件，以清单中的PDF哈希判断这些预览是否仍对应当前版本。

## 历史预览

- [2026-10-12图2/图3样式版PDF](previews/2026-10-12-figure23-bars/manuscript.pdf)及同目录第3、5页预览保留原位。
- [2026-10-13 F1展示修改前备份](archive/2026-10-13/f1-display-before/)保存40份原文件，包括旧正式图、表、脚本、正文、规范、PDF及预览清单；[备份清单](archive/2026-10-13/f1-display-before/manifest.json)记录原路径、备份路径、用途与SHA-256。仅为历史审阅，不作为当前生成入口。

[2026-10-12归档索引](archive/2026-10-12/README.md)按研究区、1.1润色、1.3表格、字体检查等任务收纳此前散放的图片。文件原名和内容均保留；原路径、新路径、原因及SHA-256见[迁移清单](../verification/output-preview-archive-2026-10-12.json)。

已完整纳入Git的修改前备份：

- [图表字体检查前备份](archive/2026-10-12/source-backups/font-audit-20261012-before-sources/)，12个文件，含原PDF、日志和暂存补丁。
- [图2/图3样式统一前备份](archive/2026-10-12/source-backups/figure23-bars-20261012-before/)，20个文件，含原图件、PDF、日志和源码。

两组原始清单和源码内容不变，旧路径按[收尾迁移清单](../verification/output-handoff-closeout-2026-10-12.json)解析；源码仅供历史审阅，不作为执行入口。此前已纳入版本的成组资料仍在原位置：

- [2026-10-11编译与修改前备份](build-20261011-190347/)
- [ENN表放大前备份](sec13-enn-20261012-before-large/)

后续页面预览放入`previews/<日期-任务>/`，每次更新清单和本入口；历史版本经用途与引用核对后按任务归档，不再把PNG平铺在根目录。

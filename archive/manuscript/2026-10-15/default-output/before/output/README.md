# 当前稿件与编译工作区

当前审阅稿：[8页PDF](previews/2026-10-15-sec132-joint/manuscript.pdf)；[根目录PDF](../main.pdf)为同字节副本。稿件包含第三段、分页及图3区间、纵坐标和宽度修订。当前文件与哈希见[预览清单](preview-manifest.json)。

| 内容 | 位置 |
|---|---|
| 当前整稿PDF | `output/previews/<日期-任务>/`，只保留当前稿 |
| 编译源码、中间文件与日志 | `output/build/<任务>/`，日志收在任务目录内 |
| 页面检查图片与核查记录 | `verification/layout/<任务>/`与`verification/` |
| 旧稿、试排、备份及历史检查材料 | [archive/manuscript/](../archive/manuscript/README.md) |

当前页面检查：[第3页](../verification/layout/sec132-joint-2026-10-15/page-3.png)、[第4页](../verification/layout/sec132-joint-2026-10-15/page-4.png)、[第5页](../verification/layout/sec132-joint-2026-10-15/page-5.png)。图3及版面验证见[核查记录](../verification/sec132-joint-2026-10-15.md)，最后一次[编译记录](../verification/compile-2026-10-15-102000.json)保留当时的验证范围。

本次整稿[编译目录](build/compile-2026-10-15-102000/)与[输出日志](build/compile-2026-10-15-102000/compile-output.txt)；当前图3[编译目录](build/sec132-joint-2026-10-15/figure/)。已有其它编译任务原位保留，生产脚本仍写入各自的`build/`任务目录。

2026-10-15目录调整见[迁移及核查清单](../verification/artifact-locations-2026-10-15.json)。历史清单中的旧路径按该清单解析，不能把历史验证状态视为当前全面重验。修改前只保存一份所需版本；已有匹配SHA-256的备份直接引用。旧文件不删除，归档须核用途、引用、目标不存在及移动前后哈希。编译仍遵守[项目规则](../AGENTS.md)，不因整理目录重新生成论文或科学结果。

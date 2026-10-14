# 2026-10-12页面预览归档

本次整理从`output`根目录迁移58张图片，其中56张归入本目录，最近一次核查的2张放入当时的最新预览目录（现见[条形版历史预览](figure23-bars-preview/)）。随研究区预览保存1份文本提取文件；旧预览清单完整迁至`preview-index/`。归档日期表示本次整理时间，不重新推断各文件的生成时间或科学有效性。

| 目录 | 内容 | 文件数 |
|---|---|---:|
| [study-area](study-area/) | 研究区图位置和尺寸的页面预览，含配套文本提取 | 6 |
| [sec11-polish](sec11-polish/) | 1.1多轮润色的页面比较 | 4 |
| [sec13-layout](sec13-layout/) | 1.3双表、整表、统计口径及字号调整的历史预览 | 32 |
| [font-audit](font-audit/) | 图表字体核查前后页面 | 7 |
| [figure-size-comparison](figure-size-comparison/) | 图2、图3调整条形前的尺寸比较 | 2 |
| [sec32-layout](sec32-layout/) | 原3.2页面预览及两个同内容副本，均完整保留 | 6 |
| [preview-index](preview-index/) | 2026-10-11七页版本的原始预览清单 | 1 |
| [reference-snapshots](reference-snapshots/) | 修改引用路径前的14份清单、核查记录及进度快照 | 14 |
| [source-backups](source-backups/) | 后续补齐的字体检查前与条形样式修改前备份，含PDF、日志、源码和原始清单 | 32 |

当前入口为[output/README.md](../../README.md)。迁移明细与核验结果见[归档清单](../../../verification/output-preview-archive-2026-10-12.json)。全部移动前核对用途、引用和目标路径；移动后逐文件核对哈希，没有删除或覆盖同名文件。

`preview-index/`和`reference-snapshots/`保留历史内容，其中的旧路径是当时记录，不继续作为活动入口；查找迁移后的文件时使用上述清单的`original_path`与`archive_path`映射。

后续收尾将两组原未跟踪源码备份完整迁入`source-backups/`并纳入Git，包括原先被忽略规则排除的2份PDF和2份日志。32个文件逐字节保留，迁移映射与SHA-256见[收尾清单](../../../verification/output-handoff-closeout-2026-10-12.json)。原始备份清单中的旧路径按此映射解析，历史源码只供审阅，不运行或写入当前结果目录。2026-10-15将原根目录的[ENN表放大前备份](source-backups/sec13-enn-20261012-before-large/)并入本目录，另将[2026-10-11编译目录](../2026-10-11/build-20261011-190347/)归档；原字节和清单保留。新增迁移见[位置映射](../../../verification/output-organization-2026-10-15.json)。上表文件数为原轮次记录，未改写为本次计数。

# 论文预览、编译文件与历史归档

当前可审阅稿为[8页PDF](previews/2026-10-15-sec132-joint/manuscript.pdf)，基于`69c310e`后的未提交修改。图3改用简洁区间标签，两幅图都显示纵坐标，图框各加宽至7.8厘米，以两个8.7厘米等宽面板填满通栏。先前第三段与分页修订保留，表1和图3仍在第4页；页面预览为[第3页](previews/2026-10-15-sec132-joint/page-3.png)、[第4页](previews/2026-10-15-sec132-joint/page-4.png)、[第5页](previews/2026-10-15-sec132-joint/page-5.png)。

PDF及页面哈希见[当前清单](preview-manifest.json)，本次图件与版面检查见[核查记录](../verification/sec132-joint-2026-10-15.md)。图3重新导出，科学数值、分档和气泡面积比例保持不变，本次不代表整篇定稿验证。前一轮[行文与分页核查](../verification/sec132-flow-2026-10-15.md)、2026-10-14[数字核查](../verification/sec132-landscape-2026-10-14.md)及本日稍早仅整理文件位置的过程均保留原时点。

2026-10-15按明确编译指令重新生成8页稿，已同步[根目录PDF](../main.pdf)与当前审阅稿。逐页文字、页面尺寸及140 dpi渲染像素均与前次修订稿一致，现有页面预览继续有效；正文与表体源码哈希未变。**Verified**：[本次编译核查](../verification/compile-2026-10-15-102000.json)；替换前的PDF与入口文件见[原字节备份清单](archive/2026-10-15/compile-102000-before/manifest.json)。

## 目录分工

| 位置 | 内容与使用规则 |
|---|---|
| `previews/<日期-任务>/` | 当前可审阅整稿PDF和必要页面图片；现仅保留上述8页稿，旧稿退出此目录 |
| `build/<任务>/` | 图件独立编译源码、中间PDF、日志及整稿编译日志；不作为整稿审阅入口 |
| `archive/<日期>/<任务>/` | 被替代的整稿预览、试排、修改前备份和检查产物；原字节保留，不自动执行其中的旧源码 |
| `preview-manifest.json` | 绑定当前PDF、页面图片及原核查范围；历史清单按归档映射定位 |

正式论文图件仍在[figures](../figures/)，正式表体在[tables](../tables/)，数值权威为[results/summary](../results/summary/)。`output`不保存新的科学结果副本。

## 当前编译文件

- [本次整稿编译目录](build/compile-2026-10-15-102000/)及[编译输出](build/compile-2026-10-15-102000-output.txt)；[前次图3修订编译目录](build/sec132-joint-2026-10-15/manuscript/)及[编译输出](build/sec132-joint-2026-10-15/manuscript-compile-output.txt)原位保留。
- [当前联合图编译文件](build/sec132-joint-2026-10-15/figure/)；生成入口为`scripts/generate_sec13_landscape_display.py --figure-only`。前一轮[分页编译](build/sec132-flow-2026-10-15/final/)与[旧联合图编译](build/sec132-landscape/figure/)原位保留。
- [独立气泡图v3编译文件](build/area_shape_joint_bubbles_v3/)；生成入口为`scripts/plot_area_shape_joint_bubbles.py`，正式探索图仍在`figures/exploratory/area_shape_joint_bubbles_v3/`。

两个生成入口已改为写入`build/`；已有输出先按规则保存，不能覆盖后再补备份。正常修改仍遵守AGENTS.md的编译授权条件。

## 历史入口

| 任务 | 位置 |
|---|---|
| 2026-10-15图3轴标与宽度修订前 | [旧8页预览](archive/2026-10-15/sec132-flow-previous-preview/)、[原图及源码快照](archive/2026-10-15/sec132-joint-before/)、[渲染检查](archive/2026-10-15/sec132-joint-review/)；[迁移映射与哈希](../verification/sec132-joint-2026-10-15.json) |
| 2026-10-14景观9页稿及第3—5页 | [原字节归档](archive/2026-10-15/sec132-landscape-previous-preview/)；[路径与SHA-256](../verification/sec132-flow-2026-10-15-archive.json) |
| 2026-10-15行文与分页修订前文件、试排及渲染检查 | [修订前快照](archive/2026-10-15/sec132-flow-before/)、[首轮试排](archive/2026-10-15/sec132-flow-pass1/)、[最终全页渲染](archive/2026-10-15/sec132-flow-final-review/) |
| 2026-10-14景观首轮试排 | [试排PDF、页面及日志](archive/2026-10-14/sec132-landscape-pass1-preview/) |
| 2026-10-14跨站主表仅均值版 | [8页PDF及第7页预览](archive/2026-10-14/cross-f1-means-preview/)，[该版清单](archive/2026-10-14/cross-f1-means-preview/preview-manifest.json) |
| 2026-10-13 F1百分数版 | [8页PDF与全页预览](archive/2026-10-13/f1-percent-preview/)，[该版清单](archive/2026-10-14/cross-f1-means-preview/previous-preview-manifest.json)；此版主表仍为均值±标准差 |
| 2026-10-12图2/图3条形版 | [8页PDF及第3、5页预览](archive/2026-10-12/figure23-bars-preview/) |
| 2026-10-11编译与修改前备份 | [编译目录](archive/2026-10-11/build-20261011-190347/) |
| ENN表放大前备份、字体与条形修改前备份 | [源码备份](archive/2026-10-12/source-backups/)；各组原清单均保留 |
| F1展示修改前备份 | [原文件及清单](archive/2026-10-13/f1-display-before/) |
| 1.3.2景观修订前备份 | [原文件及清单](archive/2026-10-14/sec132-landscape-before/) |
| 更早的研究区、正文与表格页面 | [2026-10-12归档索引](archive/2026-10-12/README.md) |
| 本次整理前入口、脚本与引用说明 | [原字节快照](archive/2026-10-15/organization-before/)；只保存本轮实际修改的文件 |
| 根目录遗留的文献检查产物 | [参考文献检查归档](archive/2026-10-15/reference-audit/)；归档日期不代表生成日期 |

## 整理记录与后续保存

[本次迁移与核查清单](../verification/output-organization-2026-10-15.json)记录67份移动文件、3个遗留空目录、修改前快照的原/新路径、原因与SHA-256。原有历史JSON及快照不改写，旧路径通过该清单和既有迁移记录解析；同内容但承担不同备份用途的文件保留。

**Verified（2026-10-15）**：原236份文件全部保留并逐字节核对，当前PDF及3张页面图片哈希不变；201个本地文档链接和两项受影响的只读检查通过。AGENTS.md、忽略规则、正文、正式图件和科学数值未改。本轮未暂存或提交；清单的`git_preservation`列明15份原已跟踪、迁移后仍匹配既有忽略规则的文件，后续提交须显式纳入，不能因忽略规则漏掉它们。

后续完成新稿审阅后，把旧稿整体移入对应日期归档，更新本入口和当前清单；试排不与最终预览并列，编译中间文件不写入`previews/`或根目录。归档前先查引用和目标是否存在，移动后核对原字节，修正活动链接。不得用删除或扩大忽略范围来清理目录。

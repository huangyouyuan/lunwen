# 联合气泡图旧版归档

2026-10-12。按本轮旧版归档与提交安排，集中保存v1、v2和初次汇总快照。当前图为[v3](../../results/summary/area_shape_joint_bubbles_v3/README.md)，活动入口见[用途索引](../../results/summary/area_shape_joint_bubbles/README.md)。

## 范围与保留方式

- `history/`保留28份旧文件，按原仓库相对路径组织：v1/v2图件4份、两轮预览与LaTeX中间文件10份、v1/v2统计和说明12份、初次汇总CSV2份。
- `before-entry-update/`保存4份本次入口修正前快照：绘图脚本、独立核查脚本、用途索引及Git字节属性。只读`.source`快照不作为生产入口。
- [迁移清单](archive-manifest.json)逐文件记录原路径、归档路径、移动或快照方式、原因、字节数及SHA-256。移动前确认目标不存在、源和目标均位于本仓库内；全部文件移动或复制后逐项核对原字节。

## 依赖和历史说明

v2汇总CSV与v3逐字节相同，仍是当前绘图大小比例及数据不变性核查的基线。活动绘图与核查脚本现在只读`history/results/summary/area_shape_joint_bubbles_v2/`，不会调用归档脚本或向历史目录写入新结果。

归档中的README、manifest、交付清单及日志保留原文，原路径按迁移清单解析。它们的Verified指其原记录时点，不升级为本次全面科学复验；归档文档中的旧运行命令不作为当前入口。

v2时代的原代码及入口还保存在[此前的字节快照](../../output/archive/2026-10-12/area-shape-square-before/manifest.json)；v3归档前代码对应本目录`before-entry-update/`。这两层快照可按原路径和SHA-256区分，不覆盖同名文件。

本次不重绘、不编译，v3图件和统计数据保持原字节。归档后执行生产脚本的只读`--check`与独立核查，并核对Git暂存保存内容；本轮记录见[归档核查](../../verification/area-shape-bubbles-archive-2026-10-12.json)。

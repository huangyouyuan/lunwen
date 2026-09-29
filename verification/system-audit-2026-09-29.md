# 系统整理与探索核查（2026-09-29）

## 范围与总状态

**Partially verified**。本轮整理项目入口、测试目录及明确停用文件，不改正文、训练、科学计算口径和既有探索产物；不重跑产物生成、不编译、不暂存、不提交、不 push，不删除任何文件。

起始 Git：`master`，`9c52fc1`。工作区并非干净：两处 `sec33_exploration` 结果目录和四个探索/测试脚本未跟踪。旧交接中的“分组链待建”已不符合磁盘状态。

## 本轮实测

### 文件一致性：Verified

对原工作目录实际文件只读计算 SHA-256；清单输入同时核对字节数。

| 清单 | 输入哈希一致 | 输出哈希一致 | 脚本哈希 | 协议哈希 |
|---|---:|---:|---|---|
| `results/summary/sec33_exploration/run_manifest.json` | 16/16 | 18/18 | 一致 | 一致 |
| `results/summary/sec33_exploration/boundary_manifest.json` | 245/245 | 7/7 | 一致 | 未记录 |
| `results/processed/sec33_exploration/grouping_lock.json` | 3/3 | 2/2 | 不适用 | 一致 |

去重核对 285 个文件、1,906,841,384 字节：哈希不一致 0，不可访问 0。此结论说明当前文件与已有清单一致，不代表独立重现科学计算，也不证明分组确实先于模型结果读取。

### 已存检查表：Verified（仅表内复核）

| 既有检查表 | 行数 | 既有状态 |
|---|---:|---|
| `checks.csv` | 1,061 | 全部 Verified |
| `boundary_checks.csv` | 8,424 | 全部 Verified |
| `cm_closure_checks.csv` | 1,152 | 全部 Verified |
| `full_site_reference_checks.csv` | 600 | 全部 Verified |
| `boundary_identity_checks.csv` | 48 | 全部 Verified |

本轮复算检查表内的差值：闭合差值非零 0 行；按 `abs(recomputed-existing) > tolerance` 检查参考表，超限 0 行。没有重新从原始标签或预测重建 CM，不能将上述状态写成“本轮完整重跑通过”。

### 单元测试：Verified

测试由 `scripts/test_sec33_protocol.py` 移至 `scripts/test/test_sec33_protocol.py`，按文件位置加入父级脚本目录，修复直接运行及 unittest discovery 的导入。未改被测生产脚本及测试断言。原脚本逐字节快照及原哈希保存在归档目录。

以下命令实际执行，均 exit 0、7 项通过：

```text
python -B -m unittest discover -s scripts/test -p 'test_*.py' -v
python -B scripts/test/test_sec33_protocol.py
```

覆盖右闭分位、重复切点、全相等/最大值、缺失、空区间、缺类 F1 与零基准、组内 CM 汇总 F1。仅用内存构造数组，不写 mock 结果，不执行删除型清理。

## 已有探索成果

均保持 `derived / exploratory`，未自动成为正文结论。

| 层级 | 文件 | 数据行数 |
|---|---|---:|
| processed | patch_groups | 9,600 |
| processed | group_thresholds | 24 |
| processed | within_group_cm / cross_group_fold_cm | 243 / 3,645 |
| processed | boundary_within_cm / boundary_cross_fold_cm | 84 / 1,260 |
| summary | group_composition | 81 |
| summary | within_group_f1 / cross_group_per_fold / group_f1_dr | 243 / 3,645 / 729 |
| summary | full_site_f1_dr / low_high_contrasts | 72 / 216 |
| summary | site_features / source_target_feature_differences | 8 / 96 |
| summary | source_pair_comparisons / source_pair_counts | 2,916 / 500 |
| summary | area_ai_rank_redundancy | 8 |
| summary | boundary_within_error / boundary_cross_per_fold / boundary_error_summary | 252 / 3,780 / 756 |

## 未解决项

- **Partially verified**：主清单自述空间指标仅与具名 CSV 导出对照，未从标签 GeoTIFF 重算 ED、AREA_MN、AI。
- **Partially verified**：边界清单自述复用既有结果，未重跑原始距离变换；未记录协议哈希。
- **Partially verified**：边界身份表保留两条报告指纹不一致（3D U-Net、U-TAE 在 B 站的站内记录），其中 U-TAE B 站缺 GeoTIFF 标签。相对首份参考 TIFF 的文件哈希不同共三条，另含 U-TAE A 站站内记录。文件哈希差异不能直接解释为像元差异；这些异常不能因行状态为 Verified 就忽略。
- **Not verified**：`figures/exploratory/sec33/` 不存在，只有绘图脚本，没有可核验的候选图。
- **Not verified**：本轮未独立重建原始预测至分组结果全链，未验证正式排版。

## 整理后复核（2026-09-30）

- **Verified**：六个归档文件逐字节哈希及字节数一致，测试原件快照哈希一致；Git 中缺失的已跟踪旧路径均有归档目标，没有未解释的删除。当前 README 的本地 Markdown 链接均存在。
- **Verified**：正式 PDF 与五个当前预览文件哈希与清单一致；主探索脚本、冻结协议和主清单的 18 个产物哈希仍一致，本轮未覆盖探索结果。
- **Partially verified**：初次综合核查在源文件逐字节哈希处失败。随后定位到 `sections/04_results.tex` 的 CRLF/LF 差异：磁盘哈希为 `ea8a1c1c86c0f52e671675b564d58841b21d5cab62463a9b189299d0de0a19ef`，将 CRLF 规范化为 LF 后为清单记录的 `d965504eff57b6c4ad0c62dfd8d3c7c599f9553170913b260c9f3a7f4baa2830`，与 HEAD blob 完全相同。没有正文内容差异；本轮不改正文换行、不伪改历史构建哈希，也不据此重编译。其余三项源码哈希逐字节一致。
- **Verified**：`git diff --check` 无差异格式错误；Git 提示 AGENTS 将来操作时可能 LF→CRLF，是换行提示，不是测试失败。工作区仍包含本轮改动和接手时未跟踪成果，未宣称干净。

## 目录整理决定

- AGENTS 与 README 写入不删除任何文件、只归档、迁移前核查依赖、记录原路径及哈希、禁止覆盖同名归档目标。
- 明确停用的 `plan/migration-map.md` 和五张历史 `results_layout-*` / `results_spacing-*` 预览移入 `archive/2026-09-29-system整理/`，保持相对目录和文件字节。README 与预览清单更新入口；不重写过去的进度或验证记录。
- 当前正式图、当前 PDF 预览、3.3 探索脚本与结果保留。探索协议原文不改，避免改变已冻结的协议哈希。
- `analyze_generalization_36paths.py` 仍有备查用途，暂不归档。显著性表仍被表格生成链输出，不单独移动。不整体归档 legacy，不按名字移动历史推理脚本 `test_semantic.py`。
- 未查明用途的辅助文件原位保留。本轮不是对整个仓库所有历史文件的穷尽性淘汰审查。

归档记录见 `archive/2026-09-29-system整理/archive-manifest.json`；测试迁移及原内容快照见同目录 `test-migration.json` 与 `before-edit/scripts/test_sec33_protocol.py`。Git 中旧路径可能显示 D，这是未暂存移动的表现，必须结合归档目标及哈希判断，不能当成文件已销毁。

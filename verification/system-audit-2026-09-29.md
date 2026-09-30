# 系统整理与探索核查（2026-09-29）

B 站生产身份、修复时间线、旧指纹复算及 GeoTIFF 区分的集中记录见 [B 站身份问题追溯](iw2-identity-provenance.md)。本文件保留系统整理时的审查范围和后续更正。

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

## 核验范围与待厘清的记录

2026-09-30 作者纠正：景观指数和边界清单已正常计算，本轮不需要重跑；U-TAE B 站实际有 GeoTIFF 标签，生产时存在站点标记错误。原始站内分类结果位于 `D:/` 下 `20iw` 系列目录，跨站结果位于 `D:/cross_site_all_20260916`，原始训练数据位于 `G:/2560图像`；`iw2` 对应 B 站。以下“未重算”只描述本次审查范围，不构成重跑要求。

此前“U-TAE B 站缺 GeoTIFF 标签”及随后“预期路径未找到文件”的表述均撤回。根据边界脚本与清单，`geotiff_tags_present=False` 表示当次读取站内导出 TIFF 时 `tifffile` 未解析到地理元数据，不代表文件不存在。该文件为 `D:/20iw2/2023iw2utaeresults/summary/maps/reference.tif`，清单记录其大小为 6,558,978 字节。

本次只读原始跨站记录已确认：`batch_run.json` 中 15 条身份修正均将 U-TAE B 站来源模型的 `recorded_train_dataset_id=iw_2023` 纠正为 `corrected_train_dataset_id=iw2_2023`，覆盖 B→A/C/D、每路径五折。运行记录说明仅修正追踪字段，未修改模型权重。本次将对应 15 条仓库 raw CM 与外部逐折运行记录的来源、目标及九个矩阵元素比较，全部一致。该结论仅限已核对的跨站关联，不代表完整训练历史均已核验。

外部 U-TAE 的 A/C/D→B 三份 `maps/reference.tif` 已只读检查文件头：均为 2560×2560、EPSG:5070、30 m，具有地理信息。它们与上述站内导出 TIFF 是不同文件。

### 原始身份记录补查（2026-09-30）

**Verified**：已直接读取站内 `D:/20iw2/2023iw2utaeresults/summary/maps/reference.tif` 文件头。文件存在，包含 30 m 像元尺度和定位标签，左上角为 `(314900.52486949, 2183972.51880609)`，但缺少 `GeoKeyDirectoryTag`，因此 `tifffile.geotiff_metadata` 返回 `None`。准确描述是“缺完整 CRS GeoKey 信息”，不是标签缺失或完全没有空间定位。该定位与 B 站另外两模型的完整 GeoTIFF 一致，与 A 站位置不同。不得将 GeoKey 缺失与站点身份误标断言为同一原因。

身份问题已按三层追溯：

1. **训练数据生产标记**：`G:/2560图像/20iw2/2023iw2shuju/dataset_identity_migration.json` 明确记录旧配置沿用默认 `SITE=iw`，将 `dataset_id: iw_2023 → iw2_2023`、`site: iw → iw2`，并记录影像、标签及空间字段不变。本次读取当前 `metadata.csv` 共 400 行，首条身份为 B 站，`source_label=D:/重分类/2023iw2.tif`。另读取 `G:/2560图像/标签GeoTIFF/iw2_2023_label.tif` 文件头，确认 2560×2560、EPSG:5070、30 m 及 B 站定位；未扫描像元或核查 source_label 当前文件。
2. **站内运行与模型身份**：`D:/20iw2/2023iw2utaeresults/dataset_identity_migration.json` 记录 2026-09-16 将站内身份及实验名从 A 改为 B。当前 `conf.json`、`summary/details/summary_run.json` 与第一折 `test_patch_run.json` 指向 U-TAE、`iw2_2023` 和 `2023iw2shuju`。跨站模型身份修正及 15 条 CM 关联核查见上文。
3. **逐图块冗余字段漏改**：`D:/20iw2/2023iw2utaeresults/site_identity_repair_20260918.json` 记录五折 `test_patch_metrics.csv` 的 `site` 从 `iw` 修正为 `iw2`。本次逐行比较当前五份文件与 `site_identity_repair_backup_20260918/summary/details/fold_*/test_patch_metrics.csv`，每折 80 行、共 400 行，只有 `site` 变化，其余字段字符串逐行一致；`dataset_id`、`patch_uid` 已是 B 站身份。

**Verified**：上述文件头、具名修复记录、400 行仅 `site` 变化，以及 15 条跨站身份和 CM 关联核查。两条复合指纹的来源已由后续精确复算定位，见下节。保留原检查表布尔值，不修改历史清单，不重跑景观指数或边界计算，不宣称预测数组、权重及全部历史链条已重新验证。

### 两条复合指纹来源复算

**Verified**：3D U-Net 与 U-TAE 的 B 站站内报告保留了参考身份迁移前的旧复合指纹。保持实际标签数组及空间契约数值不变，仅恢复 `dataset_id=iw_2023` 和全部 400 个 `patch_uid` 的 `iw_2023__` 前缀，可精确重现两条旧报告指纹；使用当前 B 站身份则精确重现对照指纹。

算法依据为 `legacy/manuscript/HLS-Crop/src/learning/study_area_products.py` 第 255—272 行 `_reference_fingerprint()`：对包含 dataset_id、网格尺寸、geo_fields、排序后 patch_uids 的身份字典执行 `json.dumps(..., sort_keys=True, ensure_ascii=False)`，再接续参考标签数组的连续字节计算 SHA-256。模型名、模型 train_dataset_id、TIFF 文件头及距离数组不参与该指纹。

对两个模型分别使用其实际契约和参考 TIFF，四组控制复算结果完全相同：

| 契约 dataset_id | 全部 patch_uid 前缀 | 复算 SHA-256 |
|---|---|---|
| iw2_2023 | iw2_2023__ | b35a97a46ff580caa4fac59269d87303191a460f0d294dbd45187f21bf01759a |
| iw_2023 | iw2_2023__ | 86830e69c246eae575aa4a69568857bd0ce3049c8a54ca9b7636ef46aafbc175 |
| iw2_2023 | iw_2023__ | 0ae853ec96bbbf3de29c80993355cb3dc51a6a612b7996e7c497ef5f81a69cbb |
| iw_2023 | iw_2023__ | 7915446610aa3ee0090e8a1a54ff12399047a5504103b59e6dbf0473760ec3fd |

只恢复一个身份字段不能命中旧报告；两个同时恢复则精确命中。无需改变标签字节、地理坐标、CRS 或网格尺寸。

独立标签核对：读取 `G:/2560图像/20iw2/2023iw2shuju/metadata.csv` 及其 400 份 `ANNOTATIONS/TARGET_{patch_id}.npy`，按实际代码转换源标签 1/2/3 为内部 0/1/2，拼接为 uint8、2560×2560。通过 AST 仅提取所需读取、契约构造与指纹函数，未执行完整生产流程。原始标签拼接数组与 B 站三模型站内参考 TIFF 解码数组逐元素完全相等，三份空间契约均与 metadata 构造的契约相等，三模型各五折合并后的 400 个 UID 均与当前 metadata 相同。

- metadata SHA-256：`7d6be84036b1134cec0a3773a52e413ddc06bcd8325511abb8dc52a0ca2c0aff`，与数据身份迁移记录 after 值一致。
- 内部标签数组字节 SHA-256：`df281739a4c28c17a126d9d4238926acc81cd77d747f7a35c5e6916e07d627cb`。
- ConvGRU B 站站内报告原本就是当前指纹 `b35a97…`。
- 跨站 `unet3d__iw_2023__2023iwunet3dresults_db465976/iw2_2023/` 与 `utae__iw_2023__2023iwutaeresults_d65d9942/iw2_2023/` 的契约、参考标签与原始数据一致，报告指纹也为 `b35a97…`。这些路径均位于 `D:/cross_site_all_20260916/`。

生产迁移记录支持上述旧值：G 盘数据迁移记录明确修正 dataset_id、site、patch_uid；3D U-Net B 站迁移记录日期为 2026-09-11，U-TAE B 站为 2026-09-16。当前 U-TAE `summary/details/reference_assets/reference_contract.json` 文件哈希为 `29a4898a7d5f18d79997375e882d4391fe0994bbaaefdaf9be959f1ce226ea48`，与其迁移记录 after 值一致。

**Partially verified** 仅限旧文件的逐字节历史恢复：迁移记录指向的具名旧备份目录未找到；对当前契约文本反向替换身份也未重现 before 文件哈希，不能宣称恢复了完整旧文件。此限制不改变复合指纹输入差异已经精确复现的结论。两条差异应解释为参考身份迁移后保留的旧指纹，不是标签内容或空间位置差异。原始报告和检查表保留不改。

- **Partially verified**：本轮对景观指标仅核对具名 CSV 导出及哈希，未独立从标签重算 ED、AREA_MN、AI；不因此否定既有计算或要求重跑。
- **Partially verified**：本轮边界核查复用既有结果；清单未记录协议哈希，属于追溯记录范围，不是距离计算错误的证据。
- **Verified**：两条报告复合指纹差异已定位为参考身份迁移后遗留的旧指纹，控制复算见上节。现有检查表的 `reported_fingerprint_matches_first=False` 仍如实描述旧报告字符串不同，不直接翻转。U-TAE B 站站内 TIFF 缺完整 CRS GeoKey 是独立的导出元数据现象，不是本次复合指纹差异的原因。
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

# B 站身份误标与参考指纹追溯记录

记录日期：2026-09-30。适用对象：本项目作者、后续接手者及数据核查人员。本文是项目追溯记录，不是论文正文，也不替代实验结果。

## 1. 结论与使用边界

**Verified：本次两条参考复合指纹差异已定位。** 3D U-Net 与 U-TAE 的 B 站站内报告保留了按旧参考身份生成的指纹。使用实际标签和原算法，保持标签字节、空间参数和网格不变，仅恢复旧 `dataset_id` 与全部图块 UID 前缀，即可精确重现旧指纹；当前 B 站身份则精确重现对照指纹。

这次调查涉及四类不同对象，必须分开理解：

| 对象 | 发现 | 当前判断 |
|---|---|---|
| 数据及运行身份字段 | B 站历史沿用 A 站标记，已有迁移记录 | 已查明记录中的修正，不据此认定实际使用了 A 站影像 |
| 逐图块 CSV 的冗余 site 字段 | U-TAE B 站部分记录漏改，后单独修复 | 400 行前后比较，仅 site 变化 |
| 参考复合指纹 | 两模型仍保留旧身份生成的摘要 | 精确复算定位为旧身份指纹遗留 |
| 站内参考 TIFF 的 GeoKey | U-TAE B 站导出文件缺完整 CRS GeoKey | 文件及 B 站定位存在；与复合指纹差异不是同一问题 |

**不重跑景观指数或边界清单。** 作者已明确既有计算正常，本次任务是身份及追溯核查。没有修改原始数据、模型权重、历史报告或清单，没有通过把 False 改成 True 消除历史差异。

**Partially verified** 仅保留在旧文件逐字节恢复及未覆盖的完整历史链条上，不能把它理解成已经发现标签错误，也不能据此自动启动实验重跑。

## 2. 数据位置与身份约定

- A 站：`iw_2023`；B 站：`iw2_2023`。`iw` 与 `iw2` 是两个不同站点，不得按名称相似合并。
- 原始训练数据：`G:/2560图像/`；本次 B 站数据目录为 `G:/2560图像/20iw2/2023iw2shuju/`。
- B 站站内分类结果：`D:/20iw2/2023iw2{model}results/`，本次具体检查 utae、unet3d、convgru 三个目录。
- 跨站泛化结果：`D:/cross_site_all_20260916/`。目录同时包含来源模型身份与目标数据身份，不能将来源站误当作参考标签所属目标站。
- 本仓库结果入口：`results/raw/`、`results/processed/sec33_exploration/`、`results/summary/sec33_exploration/`。

生产记录中的 `/root/autodl-tmp/...`、`/mnt/g/...` 是当时运行环境路径，不因当前机器采用 D/G 盘就判定文件缺失。

## 3. 时间线：问题如何产生及修复

以下历史日期取自具名迁移/修复记录，不是本次核查的执行日期。不能据此补推未记录的生产时间或所有事件的先后顺序。

### 3.1 起因：数据生产沿用默认站点标记

`G:/2560图像/20iw2/2023iw2shuju/dataset_identity_migration.json` 记录原因为“旧数据生产配置沿用默认SITE=iw；按实际目录、source_label和独立空间网格修正稳定身份”。记录修正：

- `dataset_id: iw_2023 → iw2_2023`；
- `site: iw → iw2`；
- 图块 UID 改为 B 站前缀；
- 记录说明影像、标签及空间字段保持不变。

这是生产身份字段错误的直接证据，不是仅由目录名推测。本次核查当前 metadata 共 400 行，首条指向 B 站，`source_label=D:/重分类/2023iw2.tif`。该 source_label 当前文件不在本次核验范围。

### 3.2 2026-09-11：3D U-Net B 站身份迁移

`D:/20iw2/2023iw2unet3dresults/dataset_identity_migration.json` 记录从 `iw_2023` 改为 `iw2_2023`，包含 UID 规则及 summary 文件更新。本次未找到具名旧备份，不能声称恢复了所有被修改文件的旧字节。

### 3.3 2026-09-16：U-TAE B 站运行身份迁移

`D:/20iw2/2023iw2utaeresults/dataset_identity_migration.json` 记录：

- `previous_dataset_id=iw_2023`，新值 `iw2_2023`；
- 实验身份由 `utae__iw_2023__within_site_oof` 改为 `utae__iw2_2023__within_site_oof`；
- 依据包括真实数据目录、source_label 与 B 站空间变换；
- 修改对象包括参考契约文件。

当前 conf.json、summary_run.json 和已检查的逐折运行记录指向 U-TAE、B 站及 `2023iw2shuju`。参考契约身份已是 B 站，但其中报告指纹仍为旧值；后文通过复算解释该不一致。

### 3.4 跨站运行：来源模型身份字段得到纠正

`D:/cross_site_all_20260916/batch_run.json` 中共有 15 条相关非空 identity_repair 记录，均为 U-TAE B 来源模型：

- `recorded_train_dataset_id=iw_2023`；
- `corrected_train_dataset_id=iw2_2023`；
- 覆盖 B→A/C/D 三条路径，每条五折；
- 记录说明仅修正追踪字段，未修改模型权重。

本次将仓库 raw 中对应 15 条记录与外部逐折 `test_patch_run.json` 比较，来源、目标及九个 CM 元素全部一致。该结果确认已检查的跨站关联正确，不等于重新验证了所有模型训练历史。

### 3.5 2026-09-18：逐图块 site 冗余字段补修

`D:/20iw2/2023iw2utaeresults/site_identity_repair_20260918.json` 记录五折逐图块 CSV 的 site 从 iw 改为 iw2；dataset_id 与 patch_uid 当时已是 B 站身份。

本次实际比较五份当前文件与 `site_identity_repair_backup_20260918/summary/details/fold_*/test_patch_metrics.csv`：每折 80 行，共 400 行，只有 site 字段变化，其他字段字符串逐行一致。因此，可明确说这次补修未改变这些 CSV 中的其他结果字段；不能扩大为所有产物都完成逐字节历史比较。

### 3.6 2026-09-29—30：写作仓库核查发现遗留表象

系统核查注意到 B 站两模型的报告参考指纹不同于对照，以及 U-TAE B 站的 geotiff_tags_present 为 False。最初记录错误地把后者解释为标签缺失，随后又误写成预期路径未找到文件。

作者指出 B 站存在生产身份问题，并提供站内、跨站及原始训练数据位置。随后只读追溯确认文件存在、身份修复记录和真实 GeoKey 状况，进一步使用原始标签精确定位旧指纹。

**上述两种“标签缺失/路径未找到”解释均已撤回。** 保留这段纠错经过，是为了防止后续接手者从早期对话或提交中再次沿用错误判断。

## 4. 指纹来源：算法与最小控制复算

### 4.1 指纹到底包含什么

算法：`legacy/manuscript/HLS-Crop/src/learning/study_area_products.py` 第 255—272 行 `_reference_fingerprint()`。

先构造包含 dataset_id、网格尺寸、geo_fields、排序后 patch_uids 的身份字典，以 `json.dumps(identity, sort_keys=True, ensure_ascii=False).encode('utf-8')` 输入 SHA-256，然后接续参考标签数组的连续字节。

模型名称、模型 train_dataset_id、TIFF 文件头和距离数组不参与。数组 dtype 会通过原始字节影响指纹，不能在复算时任意转换。具体字典字段与序列化必须采用该版本代码，而不是另写一个看似相同的 JSON 结构。

### 4.2 两模型分别复算的结果

分别读取 3D U-Net、U-TAE B 站的实际空间契约及参考 TIFF。保持标签字节及全部空间数值不变，只控制 dataset_id 与 400 个 UID 的身份前缀。两个模型的结果完全相同：

| dataset_id | UID 前缀 | SHA-256 |
|---|---|---|
| iw2_2023 | iw2_2023__ | b35a97a46ff580caa4fac59269d87303191a460f0d294dbd45187f21bf01759a |
| iw_2023 | iw2_2023__ | 86830e69c246eae575aa4a69568857bd0ce3049c8a54ca9b7636ef46aafbc175 |
| iw2_2023 | iw_2023__ | 0ae853ec96bbbf3de29c80993355cb3dc51a6a612b7996e7c497ef5f81a69cbb |
| iw_2023 | iw_2023__ | 7915446610aa3ee0090e8a1a54ff12399047a5504103b59e6dbf0473760ec3fd |

第一行精确匹配当前对照报告，第四行精确匹配两模型旧报告。仅改其中一项不能命中旧指纹；两项同时恢复有迁移记录支持的旧值即可命中。结论不依赖猜测“可能是模型训练站字段造成”。

### 4.3 原始标签独立核对

从 G 盘读取 metadata 及 400 份 `ANNOTATIONS/TARGET_{patch_id}.npy`。按 `spatial_stitching.py` 实际读取和空间构造函数，将源标签 1/2/3 转为内部 0/1/2，拼接为 uint8、2560×2560；参考 TIFF 导出编码为内部值加 1，因此比较前按实际规则解码。

本次通过 AST 提取所需函数，只执行读取、契约构造和指纹计算，未执行完整生产流程、景观指标或边界距离计算。

核对结果：

- 三模型站内参考 TIFF 解码数组与原始标签拼接数组逐元素完全相等；
- 三份空间契约与原始 metadata 构造的契约相等；
- 三模型各五折合并的 400 个 UID 与当前 metadata 一致；
- ConvGRU B 站报告本来就使用当前指纹 b35a97…；
- 已检查的 3D U-Net、U-TAE A→B 跨站参考契约和数组与原始数据一致，也使用 b35a97…。来源是 A 并不意味着目标参考身份应为 A。

关键摘要：

| 对象 | SHA-256 |
|---|---|
| 当前 B 站 metadata.csv | 7d6be84036b1134cec0a3773a52e413ddc06bcd8325511abb8dc52a0ca2c0aff |
| 原始标签拼接后的内部数组字节 | df281739a4c28c17a126d9d4238926acc81cd77d747f7a35c5e6916e07d627cb |
| 当前 U-TAE B 站 reference_contract.json 文件 | 29a4898a7d5f18d79997375e882d4391fe0994bbaaefdaf9be959f1ce226ea48 |

metadata 与 U-TAE 契约的文件摘要分别匹配其迁移记录 after 值。文件摘要、标签数组摘要和复合参考指纹是三种不同对象，不得混用。

## 5. GeoTIFF 现象为什么是另一件事

`D:/20iw2/2023iw2utaeresults/summary/maps/reference.tif` 实际存在，6,558,978 字节，2560×2560。文件头包含：

- ModelPixelScaleTag：30 m；
- ModelTiepointTag：左上角 `(314900.52486949, 2183972.51880609)`；
- 缺少 GeoKeyDirectoryTag，tifffile.geotiff_metadata 返回 None。

同站另外两模型有完整 GeoKey、EPSG:5070，且定位相同；G 盘 B 站标签及已检查的跨站 B 站参考也有完整地理信息。A 站 U-TAE 的定位为 `(-30962.75827856116, 2247094.898688964)`，不是上述 B 站位置。

边界脚本的 geotiff_tags_present 实际采用 `geo is not None` 判断；文件打不开会报错，不存在“打不开就记 False”的分支。因此准确表述为：**一份站内导出 TIFF 缺完整 CRS GeoKey，但标签文件、像元尺度及 B 站定位存在。** TIFF 文件头不参与上述复合指纹，不能用 GeoKey 缺失解释两条旧指纹。

## 6. 证据索引

| 编号 | 原始位置 | 用途 |
|---|---|---|
| E1 | G:/2560图像/20iw2/2023iw2shuju/dataset_identity_migration.json | 数据生产默认站点及身份迁移 |
| E2 | 同目录 metadata.csv、ANNOTATIONS/TARGET_{patch_id}.npy | 当前身份、空间契约、400 份实际标签 |
| E3 | G:/2560图像/标签GeoTIFF/iw2_2023_label.tif | 原始 B 站地理标签文件头 |
| E4 | D:/20iw2/2023iw2unet3dresults/dataset_identity_migration.json | 3D U-Net 运行身份迁移 |
| E5 | D:/20iw2/2023iw2utaeresults/dataset_identity_migration.json | U-TAE 运行身份及契约迁移 |
| E6 | 同 U-TAE 目录 site_identity_repair_20260918.json 及 site_identity_repair_backup_20260918/ | site 冗余字段修复及逐行前后对照 |
| E7 | 三模型 summary/details/reference_assets/reference_contract.json、summary/maps/reference.tif、summary/details/fold_*/test_patch_metrics.csv | 当前契约、标签、逐图块 UID |
| E8 | D:/cross_site_all_20260916/batch_run.json，identity_repair 相关记录 | 15 条来源模型身份修正 |
| E9 | 跨站 U-TAE B 来源目录各目标 details/fold_*/test_patch_run.json；本仓库 results/raw/cross_site_confusion_matrices.csv | 15 条来源、目标和 CM 关联 |
| E10 | D:/cross_site_all_20260916/unet3d__iw_2023__2023iwunet3dresults_db465976/iw2_2023/ | 3D U-Net A→B 当前参考对照 |
| E11 | D:/cross_site_all_20260916/utae__iw_2023__2023iwutaeresults_d65d9942/iw2_2023/ | U-TAE A→B 当前参考对照 |
| E12 | legacy/manuscript/HLS-Crop/src/learning/study_area_products.py:255—272；spatial_stitching.py:181—260、391—428、635—640 | 指纹、标签读取、空间构造及导出编码算法 |
| E13 | results/summary/sec33_exploration/boundary_identity_checks.csv、boundary_manifest.json；scripts/explore_sec33_boundary.py | 此次核查发现的旧记录及布尔值实际定义 |

E10/E11 分别检查 details/reference_assets/reference_contract.json 与 maps/reference.tif。以上外部文件未复制入本仓库，本记录不等同于完整证据快照。

## 7. 影响范围与未验证边界

| 结论 | 状态 | 边界 |
|---|---|---|
| 两条旧指纹可由旧参考身份精确重现 | Verified | 两模型分别复算；不等于恢复全部旧文件字节 |
| B 站三模型当前参考标签与原始标签一致 | Verified | 参考标签，不是全部模型预测数组 |
| 当前空间契约和图块 UID 一致 | Verified | 本次具名文件及 400 个图块 |
| U-TAE 逐图块修复仅改 site | Verified | 五份当前 CSV 与对应备份，400 行 |
| U-TAE B 来源跨站关联一致 | Verified | 15 条身份及九个 CM 元素，不是全体实验重跑 |
| U-TAE B 站 TIFF 文件及空间定位存在 | Verified | 缺完整 CRS GeoKey 仍如实保留 |
| 旧契约完整文件逐字节恢复 | Partially verified | 具名旧备份未找到，文本逆替换未命中 before 文件摘要 |
| 全部历史权重、预测数组及下游产物重新核验 | Not verified | 本次未执行，也不因本问题自动要求执行 |

未找到的具名备份位置包括：

- D:/20iw2/2023iw2utaeresults_20260916_dataset_id_backup
- D:/20iw2/2023iw2unet3dresults_20260911_dataset_id_backup
- D:/2023iw2unet3dresults_20260911_dataset_id_backup
- G:/2560图像/20iw2/2023iw2shuju/identity_migration_backup_20260911

这些路径未找到不影响用实际标签和算法精确定位指纹输入差异，但不能因此声称“所有历史文件已恢复”。本次内存核查未保存成新的可执行测试脚本；记录给出原始算法、输入、编码与完整预期摘要，后续若封装核查脚本，应放 scripts/test/，只读输入且不改历史清单。

## 8. 后续接手规则

1. 不再写“B 站标签缺失”“找不到 TIFF”或“两个指纹不同所以标签不同”。准确引用本记录的具体对象及验证范围。
2. 当前计算关联采用 B 站稳定身份 iw2_2023；保留历史旧字段、旧指纹及迁移记录，不静默覆盖历史证据。
3. 原检查表中 False 表示旧报告字符串不等或地理元数据未完整解析，不为消除告警直接改 True。
4. 不因本记录自动重跑景观指数、边界清单、训练或预测；不将项目管理及身份修复经历写入论文正文。
5. 若以后确需修正导出元数据或生成新清单，应作为独立任务，保留旧文件并建立新旧对应；本轮未授权或执行此类改写。
6. 本记录是 B 站身份问题的集中解释入口；系统整理报告保留当次审查范围，进度与交接文件只维护摘要和链接，避免多份说明再次分叉。

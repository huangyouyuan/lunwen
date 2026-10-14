# 面积—形状联合气泡图（探索）

本次只汇总完整参考斑块并绘图，不修改论文，不生成分类精度或泛化解释。
结果性质为 **derived / exploratory**，不是已确定的形态类型。

## 数据与口径

- 来源：`results/processed/sec33_reference_patch_types/reference_patch_features.csv`；A/B/C/D依次为iw_2023/iw2_2023/ida_2023/il_2023。
- 对象：整幅30 m参考标签的8邻域同类连通斑块；不等同于农业田块。保留单像元和研究区外缘斑块。
- 两作物共149,234个斑块；AREA与SHAPE均无缺失，所有记录为valid。脚本遇NA、无穷值或范围外值会停止，不静默排除或改变分母。
- AREA单位ha，SHAPE无量纲。逐记录核对AREA = reference_pixels × 0.09 ha；汇总按整数像元求和后换算面积，避免浮点累加误差。
- AREA：<10、10–<50、50–<100、100–<200、200–<500、≥500；SHAPE：1–<1.5、1.5–<2、2–<3、≥3。均左闭右开，末档无上界；第一面积档仅含实际正面积。
- 分母是该站该作物的完整参考面积。`area_share_pct = 100 × 档内参考像元数 / 该站该作物参考像元数`。八组分别合计100%，不以全站面积或斑块数量为分母。
- CSV列出全部192个组合；无支持的23个组合为真实零值，图中留空；其余169个全部绘制，不设最小气泡，不插值、不平滑。

## 文件与复现

- [联合汇总](area_shape_joint_bins.csv)：`target/site/crop/crop_label`为身份；`area_bin/shape_bin`为展示分档；上下界空值只表示末档无上界；`patch_count/area_ha/area_share_pct`为数量、面积和组内面积占比。
- `reference_pixels/total_crop_area_ha`保留整数计数与分母；单像元及外缘支持列用于核查，没有据此筛选。
- [闭合检查](closure_checks.csv)：八组分档前后斑块数、像元、面积、单像元和外缘支持，以及占比总和。
- 图件：`figures/exploratory/area_shape_joint_bubbles_v3/fig_area_shape_joint_bubbles.pdf`及同名600 dpi PNG。
- 生产脚本：`scripts/plot_area_shape_joint_bubbles.py`。运行`python -B scripts/plot_area_shape_joint_bubbles.py --check --tag area_shape_joint_bubbles_v3`可只读核对；另存复现用新的`--tag`，已有输出不覆盖。
- 独立核查：`python -B scripts/test/check_area_shape_joint_bubbles.py --tag area_shape_joint_bubbles_v3`。
- 中间图框、独立LaTeX图件源码与日志在`output/build/area_shape_joint_bubbles_v3/`，不是主论文编译产物。2026-10-15只迁移中间文件并同步路径；原manifest的路径与哈希按[迁移清单](../../../verification/output-organization-2026-10-15.json)及已有气泡图归档映射核对，统计和图件没有重生成。

## 图形语义与核查范围

两个图框均为7.6×7.6 cm正方形，沿用figstyle的宋体/Times New Roman、小五9 pt及浅灰网格。画布17.4×11.2 cm，保持宽度并增加高度。子图题、共享图例和注释由独立LaTeX图件排版。仅左侧显示共享SHAPE刻度。
四站颜色固定；每格A左上、B右上、C左下、D右下，偏移不表示档内数值差异。气泡是联合档内的实际面积汇总，不代表分档中心存在一个真实斑块。
Matplotlib的`s = 15.1644837016 × 占比（%）`，真实圆面积为`πs/4`；相对v2所有气泡圆面积统一乘2，直径乘√2；共享1%、5%、20%图例用同一物理直径换算。最大直径6.5054 mm，无轮廓描边放大小值。按本轮确认，保持严格正比，不额外设置最小气泡下限。每个圆均留在自己的分档内。

本版仅调整排版；两份CSV从v2按原字节复制，生成前与完整参考数据重新汇总的结果对照一致。原始数据、分档和统计口径不变。

**Verified**：本次数据覆盖、八组闭合、与既有组成/支持表一致、圆面积比例及气泡不相交。视觉及PDF核查见本目录`verification.json`（如已生成）。
本次没有重算FRAGSTATS指标或恢复原工程配置，不升级其历史验证范围。

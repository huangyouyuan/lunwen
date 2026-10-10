# 3.3 定向混淆与空间定位核查记录

日期：2026-10-07（Asia/Shanghai）  
起始 HEAD：`e27cbe0`  
结果性质：`derived / exploratory`  
总体状态：`Verified`；历史距离生成状态：`Partially verified`

## 实际范围

本轮读取并复用整幅参考标签对应的完整混淆矩阵、七距离带、边界类型、K4 图斑计数、当前 `f1_raw_scale` 汇总和已有组成表。覆盖四个目标站、三种模型、12 条有向迁移路径、本站 OOF 结果及每条路径五次跨站预测。没有重训、重新推理、重跑 FRAGSTATS、重新生成距离数组或修改论文正文。

执行入口为：

```powershell
python -B scripts/explore_sec33_directional_confusion.py
python -B scripts/plot_sec33_directional_confusion.py
python -B -m unittest scripts.test.test_sec33_directional_confusion -v
```

## 核查结果

`results/summary/sec33_directional_confusion/directional_checks.csv` 共 18,459 项，状态计数为 `Verified=18459`。核查覆盖六种定向错分的整站重算、本站和 180 次跨站身份、五次预测完整性、玉米和大豆 FN/FP 闭合、七距离带闭合、互斥边界位掩膜闭合、K4 数组索引闭合及与现行 `f1_raw_scale` F1 的逐项一致性。

新增内存单元测试 4 项全部通过：定向错误恢复作物漏分、整数矩阵 F1 分量、五次混合方向保留和不完整五次不生成均值。随后运行 `scripts/test/` 全部测试，共 79 项，全部通过；测试未向正式结果目录写入数据。

两张探索图及底表已重新生成并实际查看：

- `figures/exploratory/sec33_directional_confusion/01_directional_increment_overview.png/.pdf`
- `figures/exploratory/sec33_directional_confusion/02_case_B_to_D_soybean_to_corn_spatial.png/.pdf`

第一张图按六种方向显示“跨站−本站”错误率增量（百分点）；第二张图分别显示 B→D 大豆→玉米的七距离带增量和最近带三类边界的描述性对照，阴影仅表示五次预测的标准差。图中未使用显著性标记，也未将错误率增量标为 ΔF1 或 DR。

## 主要产物哈希

完整输入、脚本和产物清单保存在 `results/summary/sec33_directional_confusion/analysis_manifest.json`。本轮主要产物的 SHA-256 如下：

| 路径 | SHA-256 |
|---|---|
| `scripts/explore_sec33_directional_confusion.py` | `625da27dd93d00b55e306e82bae77c4247cb917393e6e3fbea7aa80139c3e856` |
| `scripts/plot_sec33_directional_confusion.py` | `647a710f8af953e59dad4d5b1f23c96d707eacfc9084ebe77443b5a43de8b05c` |
| `scripts/test/test_sec33_directional_confusion.py` | `0969a9e31fd60836b4880a90505f9ff4c0d8f2b3989f7f4158a3a9f493ab52bf` |
| `results/summary/sec33_directional_confusion/directional_checks.csv` | `2d8d9e6c778eef768d89366f81a4ad49c01858effe9c34463c39272ed99185d3` |
| `results/summary/sec33_directional_confusion/directional_summary.csv` | `d22c8a10994a9411d2c08b796db32678299a223772504e508565295a7d6c7d77` |
| `results/summary/sec33_directional_confusion/exploration-report.md` | `0068dea89164e560fde4b125b48f5f678277caed51903d40eca33adfc444ab7c` |
| `figures/exploratory/sec33_directional_confusion/01_directional_increment_overview.png` | `a28eedfb375a98fdad068a62f544ac807a020c1421101fdd7f4aebf64e9c47cd` |
| `figures/exploratory/sec33_directional_confusion/02_case_B_to_D_soybean_to_corn_spatial.png` | `c8fcb94ddd1d027558d6750aa68eff9932dfe552c2d20d077803a38a32550c82` |

## 限制

边界类型仍是参考标签四邻域接触的重叠描述视图，没有边段 ID，不能解释为同一条边界两侧。距离数组沿用前轮历史结果，本轮没有重新执行距离变换；因此不能把历史距离生成记录升级为本轮重新验证。净错误计数差表示净变化，不是逐像元配对的新增错误数；五次跨站预测也不是五个独立地理样本。C3/C4 同时改变面积、形状和邻近条件，不能据此分离单一形态或组成效应。

上述限制已同步写入任务记录和探索报告；本轮没有扩大实验范围。

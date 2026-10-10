# 本轮实际核查范围

基线HEAD `0562e08`。既有`HANDOVER.md,bibliography/references.bib,plan/claims.md`修改保留。本轮只读取参考特征、旧频数/支持/分布和预测计数索引，未打开预测数组，未重算标签连通、距离或FRAGSTATS。独立输出未覆盖历史文件。

| 内容 | 状态 | 本次范围和限制 |
|---|---|---|
| 参考身份及字段支持 | Verified | `target,PID`与patch_uid唯一、四站三类、整数支持、边界+内部闭合、远内部为内部子集、标记一致；9个作物域与既有参考支持表对照 |
| 共同等级方向及端点 | Verified | AREA像元整数端点；SHAPE反向编号；相同实际值同档；五个定义掩膜逐记录互斥且完整 |
| 有效值及排除 | Verified | 当前149234个作物斑块两指标全有效，两方案均完整归属，无排除；排除总量及空记录表保留 |
| 数量、像元及位置闭合 | Verified | 每方案/指标/域五档恢复原斑块总量、单像元、无内部/有内部、外框、边界/内部/远内部整数；八层恢复总体逐档计数 |
| 与旧精确频数一致 | Verified | 9域×2指标×2方案，按新定义独立聚合旧实际取值频数，与新斑块归属的每档数量/像元逐项一致；未重建旧分布 |
| 保存表及覆盖阅读表 | Verified | CSV重读用round_trip；对照实际PID归属、字段、分母、比例、八层并列表；份额绝对容差1e-15，整数严格相等 |
| 面积端点一致性 | Verified | AREA与参考像元×0.09一致性按绝对容差1e-12处理；整数像元用于归档；端点和同值专项测试通过 |
| 原预测计数接口 | Partially verified | 本轮只读192行索引，核查索引键唯一及12本站/180跨站条数；数组覆盖/身份的完整历史核查沿用，未重开192份数组 |
| 原标签—PID空间双射、软件指标参数 | Partially verified | 沿用历史来源和验证，不重新逐像元恢复ID，不重审外部.patch或补造工程参数 |
| 原始距离生成 | Partially verified | 沿用历史数组及定义；本轮位置支持闭合不升级距离生成验证状态 |
| 候选断点批准 | Not verified | 候选定义和支持量已验证，作者尚未审阅批准，未冻结为正式方案 |
| 等级错误、等级F1、等级×接触类型 | Not verified | 本轮没有开展误差汇总；仅说明现有计数接口及缺少的联合维度，不制造结果 |

执行：

```powershell
python -B -m unittest discover -s scripts/test -p test_sec33_common_five_grades.py -v
python -B scripts/prepare_sec33_common_five_grades.py
python -B scripts/prepare_sec33_common_five_grades.py --audit
```

8项测试全部通过，测试夹具仅在内存，覆盖十进制AREA转像元端点、端点两侧、SHAPE反向、同值/乱序、NA与无效数值、AREA字段一致性、整数支持及重叠标记、排除记录不静默缩减域分母。生产71项检查见[production_checks.csv](production_checks.csv)，保存表635项复核见[delivery_checks.csv](delivery_checks.csv)。没有运行无关的历史实验测试或删除型清理命令。

最终封存还逐项复核三类总量表、小值段逐值摘录/细段支持、分位点的ECDF左逆不等式、ENN集中值及尾部、覆盖诊断、标签与待审阅状态，详见`reference_diagnostic_checks.csv`。这是对本轮交付表的检查，没有扩大到原始距离或预测。

生产输入和当时脚本哈希见[run_manifest.json](run_manifest.json)。生产后脚本只增加上述辅助表复核与最终封存逻辑，最终脚本哈希与生产时版本分别记录，不能混同。最终交付使用`python -B scripts/prepare_sec33_common_five_grades.py --finalize`重检5项输入未变化，并记录脚本、测试、任务记录、说明和产物哈希到`delivery_manifest.json`，清单不自哈希。历史文件未复制成新的原始测量，旧来源和本次派生清楚区分。

# 3.1四站局部作物错分图

2026-10-16，derived。用途为展示三模型对错分歧最大的局部案例，不是全站典型窗口，不用于比较站点整体难度。任务规则见[任务文档](../../../plan/tasks/2026-10-16-sec31-spatial-error-figure.md)。

## 数据与选择

输入原参考与站内五折交叉验证预测路径来自`results/processed/sec33_reference_patch_types/prediction_count_index.csv`。原GeoTIFF值1/2/3对应玉米/其它地类/大豆，计算转换为0/1/2。未训练、推理或改写输入。60份原始本站运行记录的哈希与既有身份快照一致，每折测试不属于其训练或验证折。

每站穷举256×256窗口，步长1像元；仅纳入参考全有效且两作物各≥10%的窗口。分子是三模型中1个或2个模型正确的参考作物像元数，分母为窗口全部参考作物像元。三模型全对或全错均不计分歧。准确比较整数比例，并列取行、列最小者。B、D新窗口中U-TAE局部漏分高于ConvGRU，是固定规则得到的反例，未据全站排序换窗。

| 文件 | 内容与分母 |
|---|---|
| `selected_windows.csv` | 四站坐标，0基、右端不含；候选数、分歧计数/比例、三类面积占窗口面积比例及三模型合并作物漏分率 |
| `local_metrics.csv` | 108行：四站×三模型×玉米/大豆/合并作物×整个窗口/边界/内部；合并作物不重复加入单作物统计 |
| `whole_site_metrics_reused.csv` | 48行复用全站两作物边界/内部统计，记录原表及原子集名，逐像元再核对整数与比例 |
| `local_area_shape.csv` | 所选窗口涉及完整参考斑块的原AREA、SHAPE、PID及窗口内像元数，`cut_by_window`标记仅部分进入窗口的斑块；不重新计算裁切斑块形状 |
| `old_D_window.csv` | 旧D窗在新评分下的分歧比例和三模型合并作物漏分率，仅供选择追溯 |
| `input_grid_checks.csv` | 原参考/预测网格、分辨率、投影声明及像元身份；缺少CRS标签的B站U-TAE使用相同站点已核实网格，不改原文件 |
| `verification_checks.csv`、`manifest.json` | 原输入哈希、完整30 m划分与全站计数核验，以及输出哈希 |
| `figure_manifest.json` | 配色、尺寸及16幅PDF和PNG输出哈希 |

局部`reference_pixels`和`fn`为相应作物、位置内的参考数和漏分数；`whole_crop_pixels/whole_crop_fn`为整个窗口该作物的参考数、漏分总数。`area_share=reference_pixels/whole_crop_pixels`，`omission_rate=fn/reference_pixels`，`error_share=fn/whole_crop_fn`；零分母为空值NA。全站表采用相同公式但分母为全站，不与窗口混用。CSV保存完整精度，展示时百分数两位。真实其它地类误分入作物不在作物漏分图内，不能把这些比例当成F1分解。

边界/内部在2560×2560完整标签上确定：有效异类四邻域共享边到像元中心距离≤30 m为边界，作物其余像元为内部。原图外框、存储图块切线、局部窗口边缘、无效数据边缘不作为类别交界。本次以2倍网格完整距离重新计算并逐像元比对四站首距离分组，差异均为0；其余六个距离分组不在本次重算范围。完整斑块仍为8邻域，不能与类别交界的4邻域混淆。

## 复现与核查

生产入口为`scripts/plot_within_site_errors.py --prepare`和`--plot`；前者生成统计，后者只按冻结坐标生成图件。遇到同名现有输出会停止，须先按项目规范核查归档，不能直接覆盖或删除。脚本不写正文。拼版为`figures/results/fig_within_site_errors.tex`，由当前3.1图4引用。历史D图和脚本保留，不再是当前正式入口。

`python -B scripts/test/check_sec31_spatial_examples.py`运行独立小数组暴力选窗、几何线段距离、颜色与分母检查；加`--artifacts`以完整窗口数组复核四站全局最高分、并列坐标、局部闭合、输入哈希及PDF内嵌原始像元。实际执行范围与排版结论续记任务文档及`verification/`记录。

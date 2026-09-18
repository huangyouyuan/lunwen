# 脚本更新清单（2026-09-18）

## 修改内容

### 1. 方法章节 (sections/03_methods.tex)
- ✅ 将主指标从 Crop-mIoU 改为分别报告玉米F1、大豆F1
- ✅ 添加 F1 计算公式（Precision、Recall、F1）
- ✅ 添加 OA 计算公式
- ✅ 更新泛化退化指标定义（从 Crop-mIoU 改为作物F1）
- ✅ 更新显著性检验描述（12条路径作为配对单位）

### 2. 表格生成脚本 (scripts/generate_core_tables.py)
- ✅ 表1：添加 OA 列，格式改为每个模型3行（Corn F1 / Soybean F1 / OA）
- ✅ 表3：显著性检验改为先对每条路径的5次结果求均值，再用12个路径均值进行 Friedman 检验
- ✅ 表3：修正配对比较对应关系（使用 pair_labels 字典）

### 3. 跨站CM导出脚本 (scripts/extract_cross_site_cm.py)
- ✅ 统一类别顺序为 corn=0, other=1, soybean=2（与站内一致）
- ✅ 更新注释说明类别映射

### 4. 站内F1计算脚本 (scripts/calculate_crop_f1.py)
- ✅ 已验证 OA 计算正确（使用对角线和）

## 待执行操作

用户需要依次运行以下脚本以生成更新后的数据和表格：

```powershell
# 1. 重新计算站内 F1 和 OA（验证 OA 计算）
python scripts/calculate_crop_f1.py

# 2. 重新提取跨站混淆矩阵（统一类别顺序）
python scripts/extract_cross_site_cm.py

# 3. 重新生成表1、表2、表3
python scripts/generate_core_tables.py

# 4. 重新计算泛化退化（使用新的 F1 数据）
python scripts/calculate_generalization_degradation.py
```

## 待补充数据

**站内五折稳定性数据**：
- 当前表1只有 OOF 汇总值，需补充各站点五折的均值±标准差
- 需要原始的每折混淆矩阵数据（当前 `within_site_oof_baseline.csv` 只有5折汇总）
- 数据来源路径（根据第2行）：`/mnt/d/20ida/2023convgruidaresults/summary/metrics_summary.csv`

## 待修正内容

**Results 章节注释**：
- sections/04_results.tex 中仍有旧数据的错误解释注释
- 提到"大豆下降 −3.25 pp"等过时信息
- 需要在表格重新生成后同步更新

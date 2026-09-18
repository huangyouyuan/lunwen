#!/usr/bin/env pwsh
# 更新所有表格和数据（修正OA、统一类别顺序、重新生成表格）

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  论文数据更新脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 切换到项目根目录
Set-Location $PSScriptRoot\..

Write-Host "[1/4] 重新计算站内 F1 和 OA（含五折稳定性）..." -ForegroundColor Yellow
python scripts/calculate_crop_f1.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：站内F1计算失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 完成" -ForegroundColor Green
Write-Host ""

Write-Host "[2/4] 重新提取跨站混淆矩阵（统一类别顺序）..." -ForegroundColor Yellow
python scripts/extract_cross_site_cm.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：跨站CM提取失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 完成" -ForegroundColor Green
Write-Host ""

Write-Host "[3/4] 重新计算泛化退化..." -ForegroundColor Yellow
python scripts/calculate_crop_f1_degradation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：泛化退化计算失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 完成" -ForegroundColor Green
Write-Host ""

Write-Host "[4/4] 重新生成表1、表1b、表2、表3..." -ForegroundColor Yellow
python scripts/generate_core_tables.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "错误：表格生成失败" -ForegroundColor Red
    exit 1
}
Write-Host "✓ 完成" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  所有更新完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "已更新文件：" -ForegroundColor White
Write-Host "  - results/raw/within_site_confusion_matrices.csv" -ForegroundColor Gray
Write-Host "  - results/raw/cross_site_confusion_matrices.csv" -ForegroundColor Gray
Write-Host "  - results/summary/within_site_crop_f1.csv" -ForegroundColor Gray
Write-Host "  - results/summary/within_site_crop_f1_fold_stats.csv" -ForegroundColor Gray
Write-Host "  - results/summary/cross_site_crop_f1_per_fold.csv" -ForegroundColor Gray
Write-Host "  - results/summary/cross_site_crop_f1_summary.csv" -ForegroundColor Gray
Write-Host "  - results/summary/crop_f1_degradation_36paths.csv" -ForegroundColor Gray
Write-Host "  - tables/table1_within_site_baseline.csv" -ForegroundColor Gray
Write-Host "  - tables/table1b_within_site_fold_stability.csv" -ForegroundColor Gray
Write-Host "  - tables/table2_cross_site_summary.csv" -ForegroundColor Gray
Write-Host "  - tables/table3_significance_tests.csv" -ForegroundColor Gray
Write-Host ""
Write-Host "请检查表1的OA值（应为89-95%范围）和退化表（72个值应全为正）。" -ForegroundColor Yellow

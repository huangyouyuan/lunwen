param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$archiveRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
if ($repoRoot -ne 'D:\AI\lunwen' -or $archiveRoot -ne 'D:\AI\lunwen\archive\2026-10-10-mainline') { throw 'Unexpected restoration scope' }
$outPath = Join-Path $archiveRoot 'restored-reusable.csv'
if (Test-Path -LiteralPath $outPath) { throw 'Restoration already recorded; consult restored-reusable.csv' }

$restorePaths = @(
    'results/processed/sec33_round3_distance/band_metrics_cross_fold.csv',
    'results/processed/sec33_round3_distance/band_metrics_within.csv',
    'results/processed/sec33_round3_distance/d_soybean_error_decomposition.csv',
    'results/summary/sec33_round3_distance/band_contribution_closure.csv',
    'results/summary/sec33_round3_distance/band_metrics_summary.csv',
    'results/summary/sec33_round3_distance/d_soybean_error_decomposition.csv',
    'results/summary/sec33_round3_distance/three_source_overview.csv',
    'results/summary/sec33_round3_distance/checks.csv',
    'results/summary/sec33_round3_distance/run_manifest.json',
    'results/processed/sec33_round3_closeout/d_soybean_gt6_delta_e_components_per_fold.csv',
    'results/processed/sec33_round3_closeout/nearest_vs_gt6_delta_e_per_fold.csv',
    'results/summary/sec33_round3_closeout/checks.csv',
    'results/summary/sec33_round3_closeout/delivery_manifest.json',
    'results/summary/sec33_round3_closeout/d_soybean_five_prediction_diagnostic.csv',
    'results/summary/sec33_round3_closeout/nearest_vs_gt6_delta_e_summary.csv',
    'results/summary/sec33_round3_closeout/run_manifest.json',
    'results/processed/sec33_crop_spatial_context/whole_f1_error_components_per_prediction.csv',
    'results/processed/sec33_crop_spatial_context/directed_endpoints_per_prediction.csv',
    'results/processed/sec33_crop_spatial_context/distance_class_per_prediction.csv',
    'results/processed/sec33_crop_spatial_context/distance_weighted_per_prediction.csv',
    'results/processed/sec33_crop_spatial_context/weighted_crop_gap_per_prediction.csv',
    'results/summary/sec33_crop_spatial_context/whole_f1_error_components_summary.csv',
    'results/summary/sec33_crop_spatial_context/directed_endpoints_summary.csv',
    'results/summary/sec33_crop_spatial_context/distance_common_weights.csv',
    'results/summary/sec33_crop_spatial_context/distance_class_summary.csv',
    'results/summary/sec33_crop_spatial_context/distance_weighted_summary.csv',
    'results/summary/sec33_crop_spatial_context/weighted_crop_gap_summary.csv'
)
if (($restorePaths | Select-Object -Unique).Count -ne $restorePaths.Count) { throw 'Duplicate restoration path' }
$manifest = @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'archive-manifest.csv'))
$records = foreach ($relative in $restorePaths) {
    $matches = @($manifest | Where-Object { $_.original_path -eq $relative -and $_.action -eq 'move' })
    if ($matches.Count -ne 1) { throw "Missing unique original archive record: $relative" }
    $entry = $matches[0]
    $source = [IO.Path]::GetFullPath((Join-Path $repoRoot $entry.archive_path))
    $destination = [IO.Path]::GetFullPath((Join-Path $repoRoot $relative))
    if (-not $source.StartsWith($archiveRoot + '\') -or -not $destination.StartsWith($repoRoot + '\')) { throw 'Path outside scope' }
    if (-not (Test-Path -LiteralPath $source -PathType Leaf) -or (Test-Path -LiteralPath $destination)) { throw "Missing source or occupied destination: $relative" }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower() -ne $entry.sha256) { throw "Source hash mismatch: $relative" }
    [pscustomobject]@{
        original_path = $relative
        previous_archive_path = $entry.archive_path
        action = 'restore'
        reason = 'Unique full-site or reference-conditioned result reusable for current 1.3/3.1/3.3 evidence; no recomputation'
        sha256 = $entry.sha256
        bytes = $entry.bytes
    }
}
if (-not $Apply) {
    [pscustomobject]@{ status = 'Preflight verified'; files = $records.Count; bytes = ($records | Measure-Object bytes -Sum).Sum } | ConvertTo-Json -Compress
    return
}
foreach ($row in $records) {
    $source = Join-Path $repoRoot $row.previous_archive_path
    $destination = Join-Path $repoRoot $row.original_path
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $destination
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Restored hash mismatch: $($row.original_path)" }
}
$records | Export-Csv -LiteralPath $outPath -NoTypeInformation -Encoding utf8
[pscustomobject]@{ status = 'Restored and verified'; files = $records.Count; bytes = ($records | Measure-Object bytes -Sum).Sum } | ConvertTo-Json -Compress

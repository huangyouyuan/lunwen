param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$archiveRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
if ($repoRoot -ne 'D:\AI\lunwen' -or $archiveRoot -ne 'D:\AI\lunwen\archive\2026-10-10-mainline') { throw 'Unexpected archive scope' }
$manifestPath = Join-Path $archiveRoot 'archive-manifest.csv'
if (Test-Path -LiteralPath $manifestPath) { throw 'Archive already executed; consult the manifest' }

$keepScripts = @('calculate_f1_raw_scale.py','figstyle.py','generate_core_tables.py','plot_degradation_heatmap.py','plot_within_site_f1.py','plot_within_site_map_D.py','explore_sec33_directional_confusion_closeout.py','plot_sec33_directional_confusion_closeout.py','sec33_metrics.py','.gitattributes')
$keepTests = @('test_f1_raw_scale.py','test_f1_presentation.py','test_sec33_directional_confusion.py','test_sec33_directional_confusion_closeout.py')
$referenceProcessed = @('reference_patch_features.csv','prediction_count_index.csv','id_component_correspondence.csv','input_duplicate_records.csv')
$referenceSummary = @('background_adjacency.csv','background_class.csv','background_landscape.csv','count_checks.csv','count_manifest.json','data_dictionary.md','direct_patch_table_provenance.csv','enn_reference_samples.csv','feature_audit_checks.csv','feature_audit_manifest.json','feature_correlations.csv','feature_distributions.csv','grid_inventory.csv','metric_formula_checks.csv','prepare_checks.csv','prepare_manifest.json','raw_file_identity_inventory.csv','runtime_info.json')
$directionProcessed = @('boundary_bitmask_band_cm.csv','boundary_type_direction_per_prediction.csv','crop_metrics_per_prediction.csv','directional_per_prediction.csv','distance_direction_per_prediction.csv','k4_c3_c4_type_error_per_prediction.csv')
$directionSummary = @('crop_metrics_summary.csv','directional_summary.csv','distance_direction_summary.csv','k4_c3_c4_feature_support.csv')
$snapshots = @('HANDOVER.md','README.md','AGENTS.md','.gitattributes','plan/claims.md','plan/outline.md','plan/paper-context.md','plan/progress.md','plan/results-map.md','plan/experiment-protocol.md','plan/style-guide.md','plan/terminology.md','results/summary/README.md','results/summary/sec33_evidence_overview.md','results/summary/sec33_reference_patch_types/data_dictionary.md','results/summary/sec33_indicator_grading_preparation/README.md','scripts/generate_core_tables.py','scripts/explore_sec33_directional_confusion_closeout.py','scripts/test/test_sec33_directional_confusion.py','plan/tasks/2026-10-10-sec13-sec31-foundations.md')
$moves = [System.Collections.Generic.List[object]]::new()
function Queue-Move($file, $reason) {
    $relative = $file.FullName.Substring($repoRoot.Length + 1).Replace('\','/')
    $suffix = if ($file.Extension -in @('.py','.ps1')) { '.source' } else { '' }
    $moves.Add([pscustomobject]@{original_path=$relative; archive_path=('archive/2026-10-10-mainline/history/' + $relative + $suffix); action='move'; reason=$reason; sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower(); bytes=$file.Length})
}
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'scripts') -File | Where-Object { $_.Name -notin $keepScripts } | ForEach-Object { Queue-Move $_ 'Inactive producer; frozen source only, not a current execution entry' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'scripts/test') -File | Where-Object { $_.Name -notin $keepTests -and $_.Name -ne '.gitattributes' } | ForEach-Object { Queue-Move $_ 'Historical test source; excluded from active test discovery' }
$oldDirs = @('sec33_exploration','sec33_f1_raw_scale','sec33_round2','sec33_round3_distance','sec33_round3_closeout','sec33_k4_sensitivity','sec33_common_five_grades')
foreach ($layer in @('processed','summary')) {
    foreach ($dir in $oldDirs) {
        $path = Join-Path $repoRoot "results/$layer/$dir"
        if (Test-Path -LiteralPath $path) { Get-ChildItem -LiteralPath $path -File -Recurse | ForEach-Object { Queue-Move $_ 'Historical exploratory scheme; no current consumer requires this file' } }
    }
}
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/processed/sec33_reference_patch_types') -File | Where-Object { $_.Name -notin $referenceProcessed -and $_.Name -notlike 'counts_*.npz' -and $_.Name -notlike 'reference_full_*.npz' } | ForEach-Object { Queue-Move $_ 'Historical clustering assignment or derived type result' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/summary/sec33_reference_patch_types') -File | Where-Object { $_.Name -notin $referenceSummary } | ForEach-Object { Queue-Move $_ 'Historical clustering interpretation and type comparison; reference assets retained' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/processed/sec33_crop_spatial_context') -File | Where-Object { $_.Name -ne 'whole_cm.csv' } | ForEach-Object { Queue-Move $_ 'Superseded tile/joint analysis; whole CM and full-reference arrays retained elsewhere' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/summary/sec33_crop_spatial_context') -File | ForEach-Object { Queue-Move $_ 'Superseded spatial-context exploration; corrected directional products retained' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/processed/sec33_directional_confusion') -File | Where-Object { $_.Name -notin $directionProcessed } | ForEach-Object { Queue-Move $_ 'Superseded case export; required closeout inputs retained' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/summary/sec33_directional_confusion') -File | Where-Object { $_.Name -notin $directionSummary } | ForEach-Object { Queue-Move $_ 'Superseded report/view; current corrected closeout retained' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'figures/exploratory') -Directory | Where-Object { $_.Name -ne 'sec33_directional_confusion_closeout' } | ForEach-Object { Get-ChildItem -LiteralPath $_.FullName -File -Recurse | ForEach-Object { Queue-Move $_ 'Historical exploratory figure and plot data, not used by manuscript' } }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/summary') -File | Where-Object { $_.Name -notin @('README.md','sec33_evidence_overview.md') } | ForEach-Object { Queue-Move $_ 'Superseded rounded/DR/Crop-mIoU summary or historical round report' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'results/processed') -File | ForEach-Object { Queue-Move $_ 'Historical Crop-mIoU aggregate, not used by current F1 chain' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'tables') -File | Where-Object { $_.Name -notin @('table2_cross_site_f1_12paths.csv','table2_cross_site_f1_12paths_rows.tex') } | ForEach-Object { Queue-Move $_ 'Historical backup/significance table; current manuscript table retained' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'plan/tasks') -File | Where-Object { $_.Name -notin @('.gitattributes','2026-10-10-sec13-sec31-foundations.md','2026-10-10-mainline-archive.md') } | ForEach-Object { Queue-Move $_ 'Completed or deferred historical task, not a current work instruction' }
foreach ($relative in @('plan/sec33-exploration-protocol.md','plan/capability-audit.md')) { Queue-Move (Get-Item -LiteralPath (Join-Path $repoRoot $relative)) 'Superseded exploration/system planning' }
Get-ChildItem -LiteralPath (Join-Path $repoRoot 'verification') -File | Where-Object { $_.Name -notin @('.gitattributes','iw2-identity-provenance.md','mainline-archive-2026-10-10.md') } | ForEach-Object { Queue-Move $_ 'Historical verification record; status and content preserved, not reverified' }
$copies = foreach ($relative in $snapshots) {
    $file = Get-Item -LiteralPath (Join-Path $repoRoot $relative)
    [pscustomobject]@{original_path=$relative;archive_path=('archive/2026-10-10-mainline/snapshots/' + $relative + $(if ($file.Extension -in @('.py','.ps1')) { '.source' } else { '' }));action='snapshot';reason='Preserve current bytes, including uncommitted edits, before active revision';sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower();bytes=$file.Length}
}
$records = @($moves.ToArray()) + @($copies)
if (($records.archive_path | Select-Object -Unique).Count -ne $records.Count) { throw 'Duplicate archive destinations' }
foreach ($row in $records) {
    $destination = [IO.Path]::GetFullPath((Join-Path $repoRoot $row.archive_path))
    $source = [IO.Path]::GetFullPath((Join-Path $repoRoot $row.original_path))
    if (-not $destination.StartsWith($archiveRoot + '\') -or -not $source.StartsWith($repoRoot + '\')) { throw 'Path outside verified scope' }
    if (Test-Path -LiteralPath $destination) { throw "Existing archive destination: $destination" }
}
if (-not $Apply) { $records | Group-Object action | Select-Object Name,Count; $records | Export-Csv -LiteralPath (Join-Path $archiveRoot 'proposed-archive.csv') -NoTypeInformation -Encoding utf8; return }
$protected = @('bibliography/references.bib','main.tex') + @(Get-ChildItem -LiteralPath (Join-Path $repoRoot 'sections') -File | ForEach-Object { $_.FullName.Substring($repoRoot.Length+1) })
foreach ($relative in @('results/raw','results/processed/f1_raw_scale','results/summary/f1_raw_scale','figures/results','figures/study_area','results/processed/sec33_reference_patch_types','results/summary/sec33_indicator_grading_preparation','results/processed/sec33_indicator_grading_preparation','results/summary/sec33_directional_confusion_closeout','results/processed/sec33_directional_confusion_closeout','tables')) {
    $path = Join-Path $repoRoot $relative
    if (Test-Path -LiteralPath $path) { $protected += @(Get-ChildItem -LiteralPath $path -File -Recurse | ForEach-Object { $_.FullName.Substring($repoRoot.Length+1) }) }
}
$movePaths = @($moves | ForEach-Object { $_.original_path })
$protected = $protected | ForEach-Object { $_.Replace('\','/') } | Sort-Object -Unique | Where-Object { $_ -notin $movePaths -and $_ -notin $snapshots }
$protected | ForEach-Object { $file=Get-Item -LiteralPath (Join-Path $repoRoot $_); [pscustomobject]@{path=$_;sha256=(Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLower();bytes=$file.Length} } | Export-Csv -LiteralPath (Join-Path $archiveRoot 'protected-inputs.csv') -NoTypeInformation -Encoding utf8
$records | Export-Csv -LiteralPath $manifestPath -NoTypeInformation -Encoding utf8
foreach ($row in $records) {
    $source = Join-Path $repoRoot $row.original_path
    $destination = Join-Path $repoRoot $row.archive_path
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Source changed: $source" }
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    if ($row.action -eq 'move') { Move-Item -LiteralPath $source -Destination $destination } else { Copy-Item -LiteralPath $source -Destination $destination }
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Archive hash mismatch: $destination" }
}
$records | Group-Object action | Select-Object Name,Count

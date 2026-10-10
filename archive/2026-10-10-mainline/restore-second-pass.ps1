param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$archiveRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
if ($repoRoot -ne 'D:\AI\lunwen' -or $archiveRoot -ne 'D:\AI\lunwen\archive\2026-10-10-mainline') { throw 'Unexpected restoration scope' }
$ledgerPath = Join-Path $archiveRoot 'restored-second-pass.csv'
$reviewPath = Join-Path $archiveRoot 'second-pass-review.csv'
if (Test-Path -LiteralPath $ledgerPath) { throw 'Second-pass restoration already recorded' }

function Classify-Path([string]$path) {
    if ($path -match '^results/(processed|summary)/sec33_(reference_patch_types|k4_sensitivity|common_five_grades)/' -or
        $path -match '^figures/exploratory/sec33_(reference_patch_types|k4_sensitivity)/' -or
        $path -eq 'results/processed/sec33_directional_confusion/case_D_soybean_k4_c3_c4_all_sources.csv') {
        return @('restore','whole_reference_patch','Validated full-reference patch K2/K4 data or unapproved reference-only grade candidate; retain explicit historical status')
    }
    if ($path -match '^results/(processed|summary)/sec33_round3_(distance|closeout)/' -or
        $path -match '^figures/exploratory/sec33_round3_(distance|closeout)/' -or
        $path -match '^results/processed/sec33_exploration/boundary_(within|cross_fold)_cm\.csv$' -or
        $path -match '^results/summary/sec33_exploration/(boundary_.*|cm_closure_checks|full_site_reference_checks)\.(csv|json)$') {
        return @('restore','whole_site_distance','Original reference-distance integer counts, paired comparisons, definitions or exploratory plots; keep absolute and incremental rates distinct')
    }
    if ($path -match '^results/processed/sec33_crop_spatial_context/(joint_(counts_index\.csv|cross_.*\.npz|within_.*\.npz)|reference_[^/]+\.npz|metadata_[^/]+\.csv)$') {
        return @('restore','lossless_joint_counts','128x128 is only a storage partition; summing 400 partitions reproduces full-site band x bitmask x class integer counts')
    }
    if ($path -match '^results/processed/sec33_crop_spatial_context/(type_band_cm|distance_direction_per_prediction|exclusive_type_.*|type_(contribution|direction)_.*|boundary_asymmetry_.*|whole_(class|direction)_.*|crop_gap_per_prediction)\.csv$' -or
        $path -match '^results/summary/sec33_crop_spatial_context/(boundary_(absolute_asymmetry|asymmetry|third_class).*|distance_direction_summary|exclusive_type_direction_summary|reference_type_band_support|inclusive_type_reference_support|type_direction_summary|whole_(class|direction)_summary|crop_gap_summary|corn_f1_advantage_exceptions|f1_leakage_ordering_exceptions|count_checks|count_manifest|prepare_checks|prepare_manifest|analyze_checks|analyze_manifest|asset-and-definition-inventory|asset_inventory|data_dictionary|table_catalog|scientific_counts|na_negative_inventory|figure1_plot_data)\.(csv|json|md)$' -or
        $path -match '^figures/exploratory/sec33_crop_spatial_context/01_distance_distribution_common_weights\.(png|svg)$') {
        return @('restore','whole_site_direction_and_boundary','Full-site directional errors, mutually exclusive bitmask, distance, reference support or provenance; not a patch-shape result')
    }
    if ($path -match '^results/summary/sec33_directional_confusion/(source_target_composition|crop_f1_difference|case_(B_to_D|D)_soybean_to_(corn|other)_by_distance(_all_sources)?)\.csv$' -or
        $path -match '^figures/exploratory/sec33_directional_confusion/01_directional_increment_overview(\.(pdf|png)|_data\.csv)$') {
        return @('restore','source_composition_or_distance','Distinct full-site composition or soybean directed distance contrast with the current reference definition')
    }
    if ($path -match '^verification/sec33-(reference-patch-types|k4-sensitivity|round3-distance|round3-closeout|crop-spatial-context)-.*\.md$') {
        return @('restore','historical_verification','Original verification scope needed to interpret restored derived results; not a new validation')
    }
    if ($path -match '^results/(processed|summary)/sec33_crop_spatial_context/(area_|area-|matched_|matched-|fixed_matches|frozen_area|patch_features|comparison_rules|frozen_group|area_ai_rank|figure[23]_plot|matched_support)' -or
        $path -match '^results/(processed|summary)/sec33_(exploration|f1_raw_scale|round2)/' -or
        $path -match '^figures/exploratory/sec33_round2/') {
        return @('retain_history','tile_landscape_or_older_round','128x128 landscape grouping, matching or older version; available in archive, not the full-reference patch mainline')
    }
    if ($path -match '^scripts/' -or $path -match '^plan/' -or $path -match '^verification/') {
        return @('retain_history','historical_procedure','Historical producer, test or task with old write paths / obsolete workflow; frozen source or record remains directly accessible')
    }
    if ($path -match '^results/summary/(crop_f1_|cross_site_crop_f1|within_site_|generalization_|model_significance|sec33_experiments)' -or
        $path -match '^results/processed/generalization_analysis' -or $path -match '^tables/') {
        return @('retain_history','superseded_formal_metric','Old or duplicated F1/DR/significance presentation; verified f1_raw_scale is the active numeric source')
    }
    return @('retain_history','superseded_or_context','Previously archived descriptive view or historical report; no unique current full-reference count needed for the mainline')
}

$previous = @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'restored-reusable.csv'))
$rows = @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'archive-manifest.csv') | Where-Object { $_.action -eq 'move' -and $_.original_path -notin $previous.original_path })
$review = foreach ($row in $rows) {
    $classification = Classify-Path $row.original_path
    [pscustomobject]@{
        original_path=$row.original_path
        archive_path=$row.archive_path
        decision=$classification[0]
        category=$classification[1]
        reason=$classification[2]
        sha256=$row.sha256
        bytes=$row.bytes
    }
}
$selected = @($review | Where-Object decision -eq 'restore')
foreach ($row in $selected) {
    $source = [IO.Path]::GetFullPath((Join-Path $repoRoot $row.archive_path))
    $destination = [IO.Path]::GetFullPath((Join-Path $repoRoot $row.original_path))
    if (-not $source.StartsWith($archiveRoot + '\') -or -not $destination.StartsWith($repoRoot + '\') -or
        -not (Test-Path -LiteralPath $source -PathType Leaf) -or (Test-Path -LiteralPath $destination)) { throw "Missing source or occupied destination: $($row.original_path)" }
    if ((Get-FileHash -LiteralPath $source -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Source hash mismatch: $($row.original_path)" }
}
if (-not $Apply) {
    $review | Group-Object decision,category | Sort-Object Name | Select-Object Name,Count | Format-Table -AutoSize
    [pscustomobject]@{ status='Preflight verified'; reviewed=$review.Count; restore=$selected.Count; retain_history=$review.Count-$selected.Count; bytes=($selected | Measure-Object bytes -Sum).Sum } | ConvertTo-Json -Compress
    return
}
foreach ($row in $selected) {
    $source = Join-Path $repoRoot $row.archive_path
    $destination = Join-Path $repoRoot $row.original_path
    New-Item -ItemType Directory -Path (Split-Path -Parent $destination) -Force | Out-Null
    Move-Item -LiteralPath $source -Destination $destination
    if ((Get-FileHash -LiteralPath $destination -Algorithm SHA256).Hash.ToLower() -ne $row.sha256) { throw "Restored hash mismatch: $($row.original_path)" }
}
$review | Export-Csv -LiteralPath $reviewPath -NoTypeInformation -Encoding utf8
$selected | Select-Object original_path,@{Name='previous_archive_path';Expression={$_.archive_path}},@{Name='action';Expression={'restore'}},category,reason,sha256,bytes | Export-Csv -LiteralPath $ledgerPath -NoTypeInformation -Encoding utf8
[pscustomobject]@{ status='Restored and verified'; reviewed=$review.Count; restored=$selected.Count; retained=$review.Count-$selected.Count; bytes=($selected | Measure-Object bytes -Sum).Sum } | ConvertTo-Json -Compress

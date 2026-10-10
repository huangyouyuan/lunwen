$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../..')).Path
$archiveRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
if ($repoRoot -ne 'D:\AI\lunwen' -or $archiveRoot -ne 'D:\AI\lunwen\archive\2026-10-10-mainline') { throw 'Unexpected verification scope' }

function Require-Hash($relative, $expected) {
    $path = [IO.Path]::GetFullPath((Join-Path $repoRoot $relative))
    if (-not $path.StartsWith($repoRoot + '\') -or -not (Test-Path -LiteralPath $path -PathType Leaf)) { throw "Missing or out-of-scope file: $relative" }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLower() -ne $expected) { throw "Hash mismatch: $relative" }
}

$manifest = @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'archive-manifest.csv')) + @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'supplemental-manifest.csv'))
if (Test-Path -LiteralPath (Join-Path $archiveRoot 'second-pass-snapshots.csv')) {
    $manifest += @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'second-pass-snapshots.csv'))
}
if (($manifest.archive_path | Select-Object -Unique).Count -ne $manifest.Count) { throw 'Duplicate archive destination' }
$restored = @()
foreach ($name in @('restored-reusable.csv','restored-second-pass.csv')) {
    $restorationPath = Join-Path $archiveRoot $name
    if (Test-Path -LiteralPath $restorationPath) { $restored += @(Import-Csv -LiteralPath $restorationPath) }
}
if (($restored.original_path | Select-Object -Unique).Count -ne $restored.Count) { throw 'Duplicate restored path' }
$restoredByPath = @{}
foreach ($row in $restored) {
    if ($row.action -ne 'restore') { throw 'Invalid restoration action' }
    $original = @($manifest | Where-Object { $_.action -eq 'move' -and $_.original_path -eq $row.original_path })
    if ($original.Count -ne 1 -or $original[0].archive_path -ne $row.previous_archive_path -or $original[0].sha256 -ne $row.sha256) { throw "Restoration without matching archive record: $($row.original_path)" }
    $restoredByPath[$row.original_path] = $row
}
foreach ($row in $manifest) {
    $destination = [IO.Path]::GetFullPath((Join-Path $repoRoot $row.archive_path))
    if (-not $destination.StartsWith($archiveRoot + '\')) { throw 'Archive destination outside archive' }
    if ($row.action -eq 'move' -and $restoredByPath.ContainsKey($row.original_path)) {
        if (Test-Path -LiteralPath $destination) { throw "Restored file still at archive path: $($row.archive_path)" }
        Require-Hash $row.original_path $row.sha256
    } else {
        Require-Hash $row.archive_path $row.sha256
        if ($row.action -eq 'move' -and (Test-Path -LiteralPath (Join-Path $repoRoot $row.original_path))) { throw "Moved file still at original path: $($row.original_path)" }
    }
    if ($row.action -notin @('move','snapshot')) { throw 'Invalid archive action' }
    if ($row.original_path -match '\.(py|ps1)$' -and -not $row.archive_path.EndsWith('.source')) { throw 'Historical source remains executable' }
}

$moved = @($manifest | Where-Object action -eq 'move')
$locations = @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'effective-locations.csv'))
if ($locations.Count -ne $moved.Count -or ($locations.original_path | Select-Object -Unique).Count -ne $locations.Count) { throw 'Incomplete or duplicate effective locations' }
$movedByPath = @{}
foreach ($row in $moved) { $movedByPath[$row.original_path] = $row }
foreach ($row in $locations) {
    if (-not $movedByPath.ContainsKey($row.original_path)) { throw "Unexpected effective location: $($row.original_path)" }
    $original = $movedByPath[$row.original_path]
    $wasRestored = $restoredByPath.ContainsKey($row.original_path)
    $expectedPath = if ($wasRestored) { $row.original_path } else { $original.archive_path }
    $expectedState = if ($wasRestored) { 'restored' } else { 'historical_archive' }
    if ($row.current_path -ne $expectedPath -or $row.state -ne $expectedState -or $row.sha256 -ne $original.sha256 -or [long]$row.bytes -ne [long]$original.bytes) { throw "Incorrect effective location: $($row.original_path)" }
    if ((Get-Item -LiteralPath (Join-Path $repoRoot $row.current_path)).Length -ne [long]$row.bytes) { throw "Byte count mismatch: $($row.original_path)" }
}

$protected = @(Import-Csv -LiteralPath (Join-Path $archiveRoot 'protected-inputs.csv'))
foreach ($row in $protected) { Require-Hash $row.path $row.sha256 }

$countRoot = 'results/processed/sec33_reference_patch_types'
$index = @(Import-Csv -LiteralPath (Join-Path $repoRoot ($countRoot + '/prediction_count_index.csv')))
$expected = [System.Collections.Generic.HashSet[string]]::new()
$actual = [System.Collections.Generic.HashSet[string]]::new()
$countFiles = [System.Collections.Generic.HashSet[string]]::new()
$sites = @('iw_2023','iw2_2023','ida_2023','il_2023')
$models = @('convgru','unet3d','utae')
foreach ($model in $models) {
    foreach ($source in $sites) {
        $null = $expected.Add("within|$model|$source|$source|0")
        foreach ($target in $sites) {
            if ($source -eq $target) { continue }
            foreach ($predictionId in 1..5) { $null = $expected.Add("cross|$model|$source|$target|$predictionId") }
        }
    }
}
foreach ($row in $index) {
    $key = @($row.kind,$row.model,$row.source,$row.target,$row.fold) -join '|'
    if (-not $actual.Add($key)) { throw "Duplicate prediction identity: $key" }
    if ($row.file -ne [IO.Path]::GetFileName($row.file) -or -not $countFiles.Add($row.file)) { throw 'Invalid or duplicate indexed count file' }
    Require-Hash ($countRoot + '/' + $row.file) $row.sha256
}
if (-not $actual.SetEquals($expected) -or $index.Count -ne 192) { throw 'Incomplete 12 within / 180 cross coverage' }

$entries = @('HANDOVER.md','README.md','plan/outline.md','plan/paper-context.md','plan/progress.md','plan/results-map.md','plan/claims.md','plan/experiment-protocol.md','plan/style-guide.md','plan/terminology.md','plan/tasks/2026-10-10-sec13-sec31-foundations.md','plan/tasks/2026-10-10-mainline-archive.md','plan/tasks/2026-10-10-reusable-results-retention.md','results/summary/README.md','results/summary/sec33_evidence_overview.md','results/summary/sec33_reference_patch_types/data_dictionary.md','results/summary/sec33_indicator_grading_preparation/README.md','results/summary/sec33_directional_confusion_closeout/README.md','results/processed/sec33_crop_spatial_context/README.md','results/processed/sec33_directional_confusion/README.md','archive/2026-10-10-mainline/README.md','verification/mainline-archive-2026-10-10.md','verification/mainline-retention-2026-10-10.md')
$linkCount = 0
$entries += @('results/summary/reuse-status.md','results/summary/sec33_common_five_grades/USE_STATUS.md','results/summary/sec33_k4_sensitivity/USE_STATUS.md','plan/tasks/2026-10-11-second-pass-reuse-audit.md','verification/second-pass-reuse-2026-10-11.md')
$entries += @('plan/version-notes-2026-10-11.md')
foreach ($entry in $entries) {
    $entryPath = Join-Path $repoRoot $entry
    $content = [string](Get-Content -LiteralPath $entryPath -Raw -Encoding utf8)
    foreach ($match in [regex]::Matches($content, '\[[^\]\r\n]+\]\(([^)]+)\)')) {
        $target = $match.Groups[1].Value.Trim('<','>')
        if ($target -match '^(https?://|#|mailto:)') { continue }
        $target = $target.Split('#')[0]
        $resolved = [IO.Path]::GetFullPath((Join-Path (Split-Path -Parent $entryPath) $target))
        if (-not (Test-Path -LiteralPath $resolved)) { throw "Broken active link: $entry -> $target" }
        $linkCount++
    }
}

[pscustomobject]@{
    status='Verified'
    moved_files=@($manifest | Where-Object action -eq 'move').Count
    restored_files=$restored.Count
    remaining_archived_files=@($manifest | Where-Object action -eq 'move').Count - $restored.Count
    snapshots=@($manifest | Where-Object action -eq 'snapshot').Count
    archive_hash_checks=$manifest.Count - $restored.Count
    restored_hash_checks=$restored.Count
    effective_location_checks=$locations.Count
    protected_hash_checks=$protected.Count
    indexed_prediction_hash_checks=$index.Count
    independent_within=@($index | Where-Object kind -eq 'within').Count
    cross_predictions=@($index | Where-Object kind -eq 'cross').Count
    active_documents=$entries.Count
    active_local_links=$linkCount
} | ConvertTo-Json -Compress

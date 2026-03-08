<#
.SYNOPSIS
    Vollständige Beat Saber Song Konvertierung (Hybrid Version).
#>

param([Parameter(Mandatory=$true)][string]$Folder)

$Folder = (Resolve-Path $Folder).Path
$dllPath = Join-Path $PSScriptRoot "Tools\UABEA\AssetsTools.NET.dll"
$masterPy = Join-Path $PSScriptRoot "convert_beatmap_master.py"
$oldPy = Join-Path $PSScriptRoot "convert_beatmap_master_old.py"

Write-Host "--- Master Start (Hybrid Mode) ---" -ForegroundColor Cyan

# 1. Bundle und Ressourcen finden
$bundleFile = Get-ChildItem -Path $Folder -File | Where-Object { [string]::IsNullOrEmpty($_.Extension) } | Select-Object -First 1
if (-not $bundleFile) { Write-Error "Kein Bundle gefunden!"; return }

$bundlePath = $bundleFile.FullName
$sharedAssets = Join-Path $Folder "sharedassets0.assets"
$sharedResource = Join-Path $Folder "sharedassets0.resource"
$workingBundle = Join-Path $Folder "working.bundle"

# SCHRITT 1: Resource Replacement (UABEA)
Write-Host "[1/3] Ersetze Resource-Bytes (UABEA)..." -ForegroundColor Yellow
Add-Type -Path $dllPath
$manager = New-Object AssetsTools.NET.Extra.AssetsManager
$bundleInst = $manager.LoadBundleFile($bundlePath, $true)

$internalResName = $null
foreach ($info in $bundleInst.file.BlockAndDirInfo.DirectoryInfos) {
    if ($info.Name.EndsWith(".resource")) { $internalResName = $info.Name; break }
}

if ($null -eq $internalResName) { Write-Error "Keine .resource im Bundle!"; return }

$newResBytes = [System.IO.File]::ReadAllBytes($sharedResource)
$replacer = New-Object AssetsTools.NET.BundleReplacerFromMemory($internalResName, $internalResName, $true, $newResBytes, $newResBytes.Length, -1)

$outMs = New-Object System.IO.MemoryStream
$writer = New-Object AssetsTools.NET.AssetsFileWriter($outMs)
$bundleInst.file.Write($writer, [AssetsTools.NET.BundleReplacer[]]@($replacer))
[System.IO.File]::WriteAllBytes($workingBundle, $outMs.ToArray())
$outMs.Close()
$manager.UnloadAll($true)
Write-Host "      Resource ersetzt." -ForegroundColor Green

# SCHRITT 2: Audio Metadaten Patchen (Master Script)
Write-Host "[2/3] Patche Audio-Metadaten (Master Script)..." -ForegroundColor Yellow
python "$masterPy" --bundle "$workingBundle" --sharedassets "$sharedAssets" --output "$workingBundle"

# SCHRITT 3: Beatmaps Injektion (Old Script)
Write-Host "[3/3] Injiziere Beatmaps (Old Script)..." -ForegroundColor Yellow
$datFiles = Get-ChildItem -Path $Folder -Filter "*.dat" | Where-Object { $_.Name -notmatch "info|save|bpm" }
foreach ($dat in $datFiles) {
    Write-Host "      -> Processing Beatmap: $($dat.Name)" -ForegroundColor Cyan
    # Das alte Skript nutzt: dat bundle --output output
    python "$oldPy" "$($dat.FullName)" "$workingBundle" --output "$workingBundle"
}

# FINISH
$finalPath = Join-Path $Folder ($bundleFile.Name + "_final.bundle")
if (Test-Path $finalPath) { Remove-Item $finalPath }
Move-Item $workingBundle $finalPath

Write-Host "`n--- SUCCESS ---" -ForegroundColor Green
Write-Host "Finales Bundle erstellt: $finalPath"

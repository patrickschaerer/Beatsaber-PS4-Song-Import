<#
.SYNOPSIS
    Vollständige Konvertierung eines Beat Saber Songs für PS4.
.DESCRIPTION
    1. Ersetzt die interne .resource Datei mittels AssetsTools.NET.
    2. Korrigiert AudioClip Metadaten (m_Length, m_Size) mittels UnityPy.
.PARAMETER BundlePath
    Pfad zum Original-Bundle (z.B. worship).
.PARAMETER SourceAssets
    Pfad zur Quelldatei für Metadaten (z.B. sharedassets0.assets).
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$BundlePath,
    [Parameter(Mandatory=$true)]
    [string]$SourceAssets
)

# --- KONFIGURATION (Portabel mittels $PSScriptRoot) ---
$toolsDir = $PSScriptRoot
$dllPath = Join-Path $toolsDir "Tools\UABEA\AssetsTools.NET.dll"
$pythonScript = Join-Path $toolsDir "process_bundle.py"

# Pfade auflösen
$bundleDir = Split-Path -Parent (Resolve-Path $BundlePath)
$bundleFileName = Split-Path -Leaf $BundlePath
$newResourcePath = Join-Path $bundleDir "sharedassets0.resource"
$tempBundlePath = Join-Path $bundleDir ($bundleFileName + "-temp.bundle")
$finalBundlePath = Join-Path $bundleDir ($bundleFileName + "_final.bundle")
$cabInfoPath = Join-Path $bundleDir "CAB-Info.txt"

Write-Host "`n=== Beat Saber PS4 Song Conversion ===" -ForegroundColor Cyan
Write-Host "Bundle:      $BundlePath"
Write-Host "Source:      $SourceAssets"
Write-Host "Resource:    $newResourcePath"
Write-Host "Final Output: $finalBundlePath`n"

# Check Voraussetzungen
if (-not (Test-Path $BundlePath)) { Write-Error "Bundle nicht gefunden!"; return }
if (-not (Test-Path $SourceAssets)) { Write-Error "Source Assets nicht gefunden!"; return }
if (-not (Test-Path $newResourcePath)) { Write-Error "sharedassets0.resource nicht im Ordner gefunden!"; return }

try {
    # --- SCHRITT 1: Resource Replacement (PowerShell + AssetsTools.NET) ---
    Write-Host "[1/3] Replacing .resource file..." -ForegroundColor Yellow
    Add-Type -Path $dllPath
    $manager = New-Object AssetsTools.NET.Extra.AssetsManager
    $bundleInst = $manager.LoadBundleFile($BundlePath, $true)

    # Namen finden
    $internalResourceName = $null
    $internalCabName = $null
    foreach ($info in $bundleInst.file.BlockAndDirInfo.DirectoryInfos) {
        if ($info.Name.EndsWith(".resource")) { $internalResourceName = $info.Name }
        elseif ($info.Name.StartsWith("CAB-")) { $internalCabName = $info.Name }
    }

    if (-not $internalResourceName) { throw "Keine .resource Datei im Bundle gefunden!" }
    Write-Host "      Found: $internalResourceName"

    # CAB-Info für Python speichern
    $cabInfoContent = "CAB-Asset: $internalCabName`r`nCAB-Resource: $internalResourceName"
    $cabInfoContent | Out-File -FilePath $cabInfoPath -Encoding utf8

    # Ersetzen
    $newResourceBytes = [System.IO.File]::ReadAllBytes($newResourcePath)
    $replacer = New-Object AssetsTools.NET.BundleReplacerFromMemory(
        $internalResourceName, $internalResourceName, $true, $newResourceBytes, $newResourceBytes.Length, -1
    )
    
    $outMemStream = New-Object System.IO.MemoryStream
    $writer = New-Object AssetsTools.NET.AssetsFileWriter($outMemStream)
    $bundleInst.file.Write($writer, [AssetsTools.NET.BundleReplacer[]]@($replacer))
    [System.IO.File]::WriteAllBytes($tempBundlePath, $outMemStream.ToArray())
    $outMemStream.Close()
    $manager.UnloadAll($true)
    Write-Host "      Resource replaced successfully." -ForegroundColor Green

    # --- SCHRITT 2: Metadata Update (Python + UnityPy) ---
    Write-Host "`n[2/3] Updating AudioClip metadata..." -ForegroundColor Yellow
    
    # Python Aufruf vorbereiten
    $pyArgs = @(
        "`"$pythonScript`"",
        "--sharedassets", "`"$SourceAssets`"",
        "--bundle", "`"$tempBundlePath`"",
        "--output", "`"$finalBundlePath`""
    )
    
    $pyCommand = "python " + ($pyArgs -join " ")
    Write-Host "      Running: $pyCommand"
    Invoke-Expression $pyCommand

    # --- SCHRITT 3: Cleanup ---
    Write-Host "`n[3/3] Cleaning up temporary files..." -ForegroundColor Yellow
    if (Test-Path $tempBundlePath) { Remove-Item $tempBundlePath }
    # CAB-Info.txt behalten wir zur Sicherheit/Doku im Ordner

    Write-Host "`n=======================================" -ForegroundColor Cyan
    Write-Host "CONVERSION COMPLETE!" -ForegroundColor Green
    Write-Host "Result: $finalBundlePath"
    Write-Host "=======================================" -ForegroundColor Cyan

} catch {
    Write-Error "Fehler während der Konvertierung: $_"
}

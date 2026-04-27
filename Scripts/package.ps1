param(
    [string]$ProjectRoot,
    [string]$Preset = "Default",
    [ValidateSet("development", "production")][string]$Environment = "development",
    [ValidateSet("debug", "release")][string]$ExportMode = "release",
    [int]$BuildNumber
)

$ErrorActionPreference = "Stop"

function Get-GoshPackageJson {
    param([string]$RootPath)

    return Get-Content -LiteralPath (Join-Path $RootPath "package.json") -Raw | ConvertFrom-Json
}

function Clear-AndEnsureDirectory {
    param([string]$Path)

    Remove-Item -LiteralPath $Path -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
}

$PackageJson = Get-GoshPackageJson -RootPath $ProjectRoot
$ReleaseName = "$($PackageJson.name)-$($PackageJson.version)-$BuildNumber"
$BuildInputDir = Join-Path (Join-Path $ProjectRoot "__BUILD") $ReleaseName
$PackageOutputDir = Join-Path (Join-Path $ProjectRoot "__DIST") $ReleaseName

if (-not (Test-Path -LiteralPath $BuildInputDir -PathType Container)) {
    throw "Build output not found: $BuildInputDir"
}

Write-Host "==> Packaging: $ReleaseName"
Write-Host "==> Build input: $BuildInputDir"
Write-Host "==> Package output: $PackageOutputDir"

Clear-AndEnsureDirectory -Path $PackageOutputDir
Copy-Item -Recurse -Force -Path (Join-Path $BuildInputDir "*") -Destination $PackageOutputDir

Write-Host "==> Done"

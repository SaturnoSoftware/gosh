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

function Copy-IfPresent {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )

    if (Test-Path -LiteralPath $SourcePath) {
        Copy-Item -LiteralPath $SourcePath -Destination $DestinationPath -Recurse -Force
    }
}

$PackageJson = Get-GoshPackageJson -RootPath $ProjectRoot
$ReleaseName = "$($PackageJson.name)-$($PackageJson.version)-$BuildNumber"
$BuildOutputDir = Join-Path (Join-Path $ProjectRoot "__BUILD") $ReleaseName
$AppOutputDir = Join-Path $BuildOutputDir "App"

Write-Host "==> Building: $ReleaseName"
Write-Host "==> Output directory: $BuildOutputDir"

Clear-AndEnsureDirectory -Path $BuildOutputDir
New-Item -ItemType Directory -Force -Path $AppOutputDir | Out-Null

$FilesToCopy = @(
    "README.md",
    "COPYING.txt",
    "AUTHORS.txt",
    "CHANGELOG.txt",
    "install.sh",
    "install.ps1"
)

foreach ($File in $FilesToCopy) {
    Copy-IfPresent -SourcePath (Join-Path $ProjectRoot $File) -DestinationPath $BuildOutputDir
}

@(
    "gosh2.py",
    "gosh.sh",
    "gosh.ps1"
) | ForEach-Object {
    Copy-Item -LiteralPath (Join-Path (Join-Path $ProjectRoot "gosh") $_) -Destination (Join-Path $AppOutputDir $_) -Force
}

Copy-Item -LiteralPath (Join-Path $ProjectRoot "package.json") -Destination (Join-Path $BuildOutputDir "package.json") -Force

Write-Host "==> Done"

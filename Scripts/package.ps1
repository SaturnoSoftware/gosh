param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent),
    [string]$BuildOutputDir = (Join-Path $ProjectRoot "out/build"),
    [string]$PackageOutputDir = (Join-Path $ProjectRoot "out/package"),
    [string]$ReleaseName = "gosh"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $BuildOutputDir -PathType Container)) {
    throw "Build output not found: $BuildOutputDir. Run build.ps1 first."
}

Write-Host "==> Packaging: $ReleaseName"

Remove-Item -LiteralPath $PackageOutputDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $PackageOutputDir | Out-Null
Copy-Item -Recurse -Force -Path (Join-Path $BuildOutputDir "*") -Destination $PackageOutputDir

Write-Host "==> Done"

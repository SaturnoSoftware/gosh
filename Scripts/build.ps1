# ---------------------------------------------------------------------------- #
#                               *       +                                      #
#                         '                  |                                 #
#                     ()    .-.,="``"=.    - o -                               #
#                           '=/_       \\     |                                #
#                        *   |  '=._    |                                      #
#                             \\     `=./`,        '                           #
#                          .   '=.__.=' `='      *                             #
#                                                                              #
#                                                                              #
# File      : build.ps1                                                        #
# Project   : gosh                                                             #
# Date      : 2026-05-30                                                       #
# Copyright : Saturno Software - 2026                                          #
# Author    : mateusdigital <hello@mateus.digital>                             #
# ---------------------------------------------------------------------------- #

param(
    [string]$ProjectRoot = (Split-Path $PSScriptRoot -Parent),
    [string]$BuildOutputDir = (Join-Path $ProjectRoot "out/build"),
    [string]$ReleaseName = "gosh"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path -LiteralPath $ProjectRoot).ProviderPath
$AppOutputDir = Join-Path $BuildOutputDir "App"

Write-Host "==> Building: $ReleaseName"

Remove-Item -LiteralPath $BuildOutputDir -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $AppOutputDir | Out-Null

$PackageJson = Join-Path $ProjectRoot "package.json"
if (-not (Test-Path -LiteralPath $PackageJson -PathType Leaf)) {
    throw "package.json not found at: $PackageJson"
}
Copy-Item -LiteralPath $PackageJson -Destination $BuildOutputDir -Force

$OptionalFiles = @("README.md", "COPYING.txt", "AUTHORS.txt", "CHANGELOG.txt", "install.sh", "install.ps1")
foreach ($File in $OptionalFiles) {
    $Source = Join-Path $ProjectRoot $File
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -LiteralPath $Source -Destination $BuildOutputDir -Force
    }
}

$AppFiles = @("gosh2.py", "gosh.sh", "gosh.ps1")
foreach ($File in $AppFiles) {
    Copy-Item -LiteralPath (Join-Path $ProjectRoot "gosh/$File") -Destination $AppOutputDir -Force
}

Write-Host "==> Done"

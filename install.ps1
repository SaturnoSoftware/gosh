## -------------------------------------------------------------------------- ##
##                               *       +                                    ##
##                         '                  |                               ##
##                     ()    .-.,="``"=.    - o -                             ##
##                           '=/_       \\     |                              ##
##                        *   |  '=._    |                                    ##
##                             \\     `=./`,        '                         ##
##                          .   '=.__.=' `='      *                           ##
##                                                                            ##
##                                                                            ##
## File      : install.ps1                                                    ##
## Project   : gosh                                                           ##
## Date      : 2026-05-29                                                     ##
## Copyright : Saturno Software - 2026                                        ##
## Author    : mateusdigital <hello@mateus.digital>                           ##
## -------------------------------------------------------------------------- ##

$ErrorActionPreference = "Stop"

$ScriptDir    = Split-Path $MyInvocation.MyCommand.Path -Parent
$HomeDir      = if ($HOME -eq "") { "$env:USERPROFILE" } else { $HOME }
$ProgramName  = "gosh"
$RootPath     = Join-Path $HomeDir ".saturnosoftware/$ProgramName"
$BinPath      = Join-Path $RootPath "bin"
$ConfigPath   = Join-Path $RootPath "config"
$DataPath     = Join-Path $RootPath "data"

if (Test-Path -LiteralPath (Join-Path $ScriptDir "App") -PathType Container) {
    $SourcePath = Join-Path $ScriptDir "App"
}
elseif (Test-Path -LiteralPath (Join-Path $ScriptDir "gosh") -PathType Container) {
    $SourcePath = Join-Path $ScriptDir "gosh"
}
else {
    throw "[gosh] Missing packaged App/ or legacy gosh/ source directory."
}

$PackageJson = Join-Path $ScriptDir "package.json"
if (-not (Test-Path -LiteralPath $PackageJson -PathType Leaf)) {
    throw "[gosh] Missing package.json metadata file."
}

Write-Output "Installing ..."

foreach ($Dir in @($RootPath, $BinPath, $ConfigPath, $DataPath)) {
    if (-not (Test-Path -LiteralPath $Dir)) {
        Write-Output "  Creating: $Dir"
        $null = New-Item -Path $Dir -ItemType Directory -Force
    }
}

Get-ChildItem -LiteralPath $SourcePath -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $BinPath $_.Name) -Force
}
Copy-Item -LiteralPath $PackageJson -Destination (Join-Path $RootPath "package.json") -Force

Write-Output ""
Write-Output "$ProgramName was installed at:"
Write-Output "  $RootPath"
Write-Output "Binary directory:"
Write-Output "  $BinPath"
Write-Output "Data directory:"
Write-Output "  $DataPath"
Write-Output ""
Write-Output "You might need to add it to the PATH."
Write-Output "  Or source it directly: . `"$BinPath/gosh.ps1`""
Write-Output ""
Write-Output "Done... ;D"

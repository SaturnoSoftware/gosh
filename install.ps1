##~---------------------------------------------------------------------------##
##                               *       +                                    ##
##                         '                  |                               ##
##                     ()    .-.,="``"=.    - o -                             ##
##                           '=/_       \     |                               ##
##                        *   |  '=._    |                                    ##
##                             \     `=./`,        '                          ##
##                          .   '=.__.=' `='      *                           ##
##                 +                         +                                ##
##                      O      *        '       .                             ##
##                                                                            ##
##  File      : install.ps1                                                   ##
##  Project   : gosh                                                          ##
##  Date      : 10 Apr, 2021                                                  ##
##  License   : GPLv3                                                         ##
##  Author    : mateus.digital <hello@mateus.digital>                         ##
##  Copyright : mateus.digital 2021 - 2023                                    ##
##                                                                            ##
##  Description :                                                             ##
##    gosh for powershell.                                                    ##
##---------------------------------------------------------------------------~##

##----------------------------------------------------------------------------##
## Constants                                                                  ##
##----------------------------------------------------------------------------##
##------------------------------------------------------------------------------
## Script
$SCRIPT_FULLPATH = $MyInvocation.MyCommand.Path;
$SCRIPT_DIR      = Split-Path "$SCRIPT_FULLPATH" -Parent;
$HOME_DIR        = if($HOME -eq "") { "$env:USERPROFILE" } else { $HOME };
$APP_SOURCE_PATH = Join-Path $SCRIPT_DIR "App";
$LEGACY_SOURCE_PATH = Join-Path $SCRIPT_DIR "gosh";
## Program
$PROGRAM_NAME        = "gosh";
$PROGRAM_ROOT_PATH   = Join-Path $HOME_DIR ".saturnosoftware\$PROGRAM_NAME";
$PROGRAM_BIN_PATH    = Join-Path $PROGRAM_ROOT_PATH "bin";
$PROGRAM_CONFIG_PATH = Join-Path $PROGRAM_ROOT_PATH "config";
$PROGRAM_DATA_PATH   = Join-Path $PROGRAM_ROOT_PATH "data";

if (Test-Path -LiteralPath $APP_SOURCE_PATH -PathType Container) {
    $PROGRAM_SOURCE_PATH = $APP_SOURCE_PATH;
}
elseif (Test-Path -LiteralPath $LEGACY_SOURCE_PATH -PathType Container) {
    $PROGRAM_SOURCE_PATH = $LEGACY_SOURCE_PATH;
}
else {
    throw "[gosh] Missing packaged App/ or legacy gosh/ source directory."
}


##----------------------------------------------------------------------------##
## Script                                                                     ##
##----------------------------------------------------------------------------##
##------------------------------------------------------------------------------
Write-Output "Installing ...";

## Create the install directories...
foreach ($Path in @($PROGRAM_ROOT_PATH, $PROGRAM_BIN_PATH, $PROGRAM_CONFIG_PATH, $PROGRAM_DATA_PATH)) {
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Output "Creating directory at: ";
        Write-Output "    $Path";
        $null = (New-Item -Path $Path -ItemType Directory -Force);
    }
}

## Copy the app files to the install dir...
Get-ChildItem -LiteralPath $PROGRAM_SOURCE_PATH -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $PROGRAM_BIN_PATH $_.Name) -Force
}


Write-Output "$PROGRAM_NAME was installed at:";
Write-Output "    $PROGRAM_ROOT_PATH";
Write-Output "Binary directory:";
Write-Output "    $PROGRAM_BIN_PATH";
Write-Output "Data directory:";
Write-Output "    $PROGRAM_DATA_PATH";
Write-Output "You might need add it to the PATH";

Write-Output "Done... ;D";
Write-Output "";

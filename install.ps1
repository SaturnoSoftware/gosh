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
$PROGRAM_NAME              = "gosh";
$DIRECTORY_NAME            = "${PROGRAM_NAME}_";
$PROGRAM_INSTALL_ROOT_PATH = "${HOME_DIR}/.mateusdigital/bin";
$PROGRAM_INSTALL_SUB_PATH  = "${PROGRAM_INSTALL_ROOT_PATH}/${DIRECTORY_NAME}";

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

## Create the install directory...
if (-not (Test-Path -LiteralPath $PROGRAM_INSTALL_SUB_PATH)) {
    Write-Output "Creating directory at: ";
    Write-Output "    $PROGRAM_INSTALL_SUB_PATH";
    $null = (New-Item -Path $PROGRAM_INSTALL_SUB_PATH -ItemType Directory -Force);
}

## Copy the file to the install dir...
Copy-Item -Force (Join-Path $PROGRAM_SOURCE_PATH "gosh2.py") `
                 (Join-Path $PROGRAM_INSTALL_SUB_PATH "gosh2.py")
Copy-Item -Force (Join-Path $PROGRAM_SOURCE_PATH "gosh.ps1") `
                 (Join-Path $PROGRAM_INSTALL_ROOT_PATH "gosh.ps1");


Write-Output "$PROGRAM_NAME was installed at:";
Write-Output "    $PROGRAM_INSTALL_ROOT_PATH";
Write-Output "You might need add it to the PATH";

Write-Output "Done... ;D";
Write-Output "";

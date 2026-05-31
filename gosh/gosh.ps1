##----------------------------------------------------------------------------##
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
##  File      : gosh.ps1                                                      ##
##  Project   : gosh                                                          ##
##  Date      : Aug 12, 2015                                                  ##
##  License   : See project's COPYING.TXT for full info.                      ##
##  Author    : mateus.digital <hello@mateus.digital>                         ##
##  Copyright : mateus.digital - 2015 - 2025                                  ##
##  Copyright : Saturno Software - 2026                                       ##
##                                                                            ##
##  Description :                                                             ##
##                                                                            ##
##----------------------------------------------------------------------------##

##----------------------------------------------------------------------------##
## Constants                                                                  ##
##----------------------------------------------------------------------------##
$SCRIPT_FULLPATH = $MyInvocation.MyCommand.Path;
$SCRIPT_DIR      = (Split-Path "$SCRIPT_FULLPATH" -Parent);
$GOSH_EXE        = (Join-Path $SCRIPT_DIR "gosh2.py");

if (-not $script:GOSH_PYTHON_EXE) {
    $script:GOSH_PYTHON_EXE  = "python";
    $script:GOSH_PYTHON_ARGS = @();

    if (-not (Get-Command "python" -ErrorAction SilentlyContinue)) {
        if (Get-Command "python3" -ErrorAction SilentlyContinue) {
            $script:GOSH_PYTHON_EXE = "python3";
        }
        elseif (Get-Command "py" -ErrorAction SilentlyContinue) {
            $script:GOSH_PYTHON_EXE = "py";
            $script:GOSH_PYTHON_ARGS = @("-3");
        }
    }
}
$PYTHON_EXE  = $script:GOSH_PYTHON_EXE;
$PYTHON_ARGS = $script:GOSH_PYTHON_ARGS;

##----------------------------------------------------------------------------##
## Gosh                                                                       ##
##----------------------------------------------------------------------------##
## No args, just list the bookmarks.
if($args.Count -eq 0) {
    & $PYTHON_EXE @PYTHON_ARGS $GOSH_EXE --help;
    return;
}

## If any arg starts with -, it's a management action.
$has_flags = $false;
foreach ($a in $args) {
    if ($a.ToString().StartsWith("-")) {
        $has_flags = $true;
        break;
    }
}

if ($has_flags) {
    & $PYTHON_EXE @PYTHON_ARGS $GOSH_EXE $args;
}
## Changing directory...
else {
    $path = (& $PYTHON_EXE @PYTHON_ARGS $GOSH_EXE $args);
    if (($null -ne $path) -and (Test-Path -PathType Container $path)) {
        Set-Location $path;
    } else {
        Write-Output "$path";
    }
}

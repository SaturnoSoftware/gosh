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
$PYTHON_EXE      = "python";

if($IsMacOS) {
    $python_path  = (which python);
    if($python_path) {
        $PYTHON_EXE = "$python_path";
    } else {
        $PYTHON_EXE = "python3"
    }
}

##----------------------------------------------------------------------------##
## Gosh                                                                       ##
##----------------------------------------------------------------------------##
## No args, just list the bookmarks.
if($args.Count -eq 0) {
    & $PYTHON_EXE $GOSH_EXE --help;
    return;
}

## Concat all the arguments to make a string.
## Then search for the string for any flags.
## If we find this flags means that gosh is doing an action
## and we don't need to care about changing the directory.
## Otherwise we need to capture the output of it and make the
## poweshell to cd to that dir ;D
$cmd_line=" "
for(($i = 0); ($i -lt $args.Count); (++$i)) {
    $cmd_line += $args[$i].ToString();
}

$has_short_flags = $cmd_line.Contains(" -");
$has_long_flags  = $cmd_line.Contains(" --");

## Making an action...
if(($has_short_flags) -or ($has_long_flags)) {
    & $PYTHON_EXE $GOSH_EXE $args;
}
## Changing directory...
else {
    $path = (& $PYTHON_EXE $GOSH_EXE $args);
    if (($null -ne $path) -and (Test-Path -PathType Container $path)) {
        Set-Location $path;
    } else {
        Write-Output "$path";
    }
}

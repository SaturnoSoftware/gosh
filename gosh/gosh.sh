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
##  File      : gosh.sh                                                       ##
##  Project   : gosh                                                          ##
##  Date      : 2023-01-02                                                    ##
##  License   : See project's COPYING.TXT for full info.                      ##
##  Author    : mateus.digital <hello@mateus.digital>                         ##
##  Copyright : mateus.digital - 2023 - 2025                                  ##
##  Copyright : Saturno Software - 2026                                       ##
##                                                                            ##
##  Description :                                                             ##
##                                                                            ##
##----------------------------------------------------------------------------##

## -----------------------------------------------------------------------------
function gosh() {
    ## Constants
    local SCRIPT_FULLPATH="${BASH_SOURCE}";
    local SCRIPT_DIR="$(dirname "$SCRIPT_FULLPATH")";
    local GOSH_EXE="${SCRIPT_DIR}/gosh2.py";
    local -a PYTHON_CMD=();
    local target_path="";

    if command -v "python3" >/dev/null 2>&1 && python3 --version >/dev/null 2>&1; then
        PYTHON_CMD=("python3");
    elif command -v "python" >/dev/null 2>&1 && python --version >/dev/null 2>&1; then
        PYTHON_CMD=("python");
    elif command -v "py" >/dev/null 2>&1 && py -3 --version >/dev/null 2>&1; then
        PYTHON_CMD=("py" "-3");
    else
        echo "[gosh] Missing a working Python interpreter (tried: python3, python, py -3)";
        return 1;
    fi;

    if [ ! -f "$GOSH_EXE" ]; then
        echo "[gosh] Missing ($GOSH_EXE)";
        return 1;
    fi;

    ## No args, just list the bookmarks.
    if [ $# -eq 0 ]; then
        "${PYTHON_CMD[@]}" "$GOSH_EXE" --help;
        return 0;
    fi;

    ## If any arg has a flag, it's a management action — no cd needed.
    for item in "$@"; do
        if [ "${item:0:1}" == "-" ]; then
            "${PYTHON_CMD[@]}" "$GOSH_EXE" "$@";
            return;
        fi;
    done;

    ## Changing directory...
    target_path="$("${PYTHON_CMD[@]}" "$GOSH_EXE" "$@")" || return $?;
    target_path="${target_path//$'\r'/}";

    if command -v "cygpath" >/dev/null 2>&1 && [[ "$target_path" =~ ^[A-Za-z]:/ ]]; then
        target_path="$(cygpath -u "$target_path")";
    fi;

    if [ -d "$target_path" ]; then
        cd "$target_path" || exit 1;
        echo "[gosh] ${PWD}";
        return 0;
    fi;

    return 1;
}

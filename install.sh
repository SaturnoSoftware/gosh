#!/usr/bin/env bash
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
## File      : install.sh                                                     ##
## Project   : gosh                                                           ##
## Date      : 2026-05-29                                                     ##
## Copyright : Saturno Software - 2026                                        ##
## Author    : mateusdigital <hello@mateus.digital>                           ##
## -------------------------------------------------------------------------- ##

set -euo pipefail

SCRIPT_DIR="$(dirname "$(realpath "$0")")"
HOME_DIR="${HOME:-$USERPROFILE}"

if command -v cygpath >/dev/null 2>&1 && [[ "$HOME_DIR" =~ ^[A-Za-z]:[\\/] ]]; then
    HOME_DIR="$(cygpath -u "$HOME_DIR")"
fi

PROGRAM_NAME="gosh"
ROOT_PATH="${HOME_DIR}/.saturnosoftware/${PROGRAM_NAME}"
BIN_PATH="${ROOT_PATH}/bin"
CONFIG_PATH="${ROOT_PATH}/config"
DATA_PATH="${ROOT_PATH}/data"

if [ -d "${SCRIPT_DIR}/App" ]; then
    SOURCE_PATH="${SCRIPT_DIR}/App"
elif [ -d "${SCRIPT_DIR}/gosh" ]; then
    SOURCE_PATH="${SCRIPT_DIR}/gosh"
else
    echo "[gosh] Missing packaged App/ or legacy gosh/ source directory."
    exit 1
fi

PACKAGE_JSON="${SCRIPT_DIR}/package.json"
if [ ! -f "${PACKAGE_JSON}" ]; then
    echo "[gosh] Missing package.json metadata file."
    exit 1
fi

echo "Installing ..."

for dir in "$ROOT_PATH" "$BIN_PATH" "$CONFIG_PATH" "$DATA_PATH"; do
    if [ ! -d "$dir" ]; then
        echo "  Creating: $dir"
        mkdir -p "$dir"
    fi
done

cp -f "${SOURCE_PATH}/"* "${BIN_PATH}/"
cp -f "${PACKAGE_JSON}" "${ROOT_PATH}/package.json"

echo ""
echo "$PROGRAM_NAME was installed at:"
echo "  $ROOT_PATH"
echo "Binary directory:"
echo "  $BIN_PATH"
echo "Data directory:"
echo "  $DATA_PATH"
echo ""
echo "You might need to add it to the PATH."
echo "  Or source it directly: source \"$BIN_PATH/gosh.sh\""
echo ""
echo "Done... ;D"

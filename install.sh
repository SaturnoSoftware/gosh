#!/usr/bin/env bash

##----------------------------------------------------------------------------##
## Constants                                                                  ##
##----------------------------------------------------------------------------##
SCRIPT_FULLPATH="$(realpath "$0")";
SCRIPT_DIR="$(dirname "$SCRIPT_FULLPATH")";
HOME_DIR="${HOME:-$USERPROFILE}";

PROGRAM_NAME="gosh";
PROGRAM_ROOT_PATH="${HOME_DIR}/.saturnosoftware/${PROGRAM_NAME}";
PROGRAM_BIN_PATH="${PROGRAM_ROOT_PATH}/bin";
PROGRAM_CONFIG_PATH="${PROGRAM_ROOT_PATH}/config";
PROGRAM_DATA_PATH="${PROGRAM_ROOT_PATH}/data";

if [ -d "${SCRIPT_DIR}/App" ]; then
    PROGRAM_SOURCE_PATH="${SCRIPT_DIR}/App";
elif [ -d "${SCRIPT_DIR}/${PROGRAM_NAME}" ]; then
    PROGRAM_SOURCE_PATH="${SCRIPT_DIR}/${PROGRAM_NAME}";
else
    echo "[gosh] Missing packaged App/ or legacy gosh/ source directory.";
    exit 1;
fi

##----------------------------------------------------------------------------##
## Script                                                                     ##
##----------------------------------------------------------------------------##
echo "Installing ...";

## Create the install directories if they don't exist
for directory in "$PROGRAM_ROOT_PATH" "$PROGRAM_BIN_PATH" "$PROGRAM_CONFIG_PATH" "$PROGRAM_DATA_PATH"; do
    if [ ! -d "$directory" ]; then
        echo "Creating directory at:";
        echo "    $directory";
        mkdir -p "$directory";
    fi
done

## Copy files
cp -f "${PROGRAM_SOURCE_PATH}/"* "${PROGRAM_BIN_PATH}/";

echo "$PROGRAM_NAME was installed at:";
echo "    $PROGRAM_ROOT_PATH";
echo "Binary directory:";
echo "    $PROGRAM_BIN_PATH";
echo "Data directory:";
echo "    $PROGRAM_DATA_PATH";
echo "You **need** to source it to use, for example:";
echo "    source \"$PROGRAM_BIN_PATH/gosh.sh\"";

echo "Done... ;D";
echo "";

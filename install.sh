#!/usr/bin/env bash

##----------------------------------------------------------------------------##
## Constants                                                                  ##
##----------------------------------------------------------------------------##
SCRIPT_FULLPATH="$(realpath "$0")";
SCRIPT_DIR="$(dirname "$SCRIPT_FULLPATH")";
HOME_DIR="${HOME:-$USERPROFILE}";

PROGRAM_NAME="gosh";
DIRECTORY_NAME="${PROGRAM_NAME}_";
PROGRAM_INSTALL_ROOT_PATH="${HOME_DIR}/.mateusdigital/bin";
PROGRAM_INSTALL_SUB_PATH="${PROGRAM_INSTALL_ROOT_PATH}/${DIRECTORY_NAME}";

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

## Create the install directory if it doesn't exist
if [ ! -d "$PROGRAM_INSTALL_SUB_PATH" ]; then
    echo "Creating directory at:";
    echo "    $PROGRAM_INSTALL_SUB_PATH";
    mkdir -p "$PROGRAM_INSTALL_SUB_PATH";
fi

## Copy files
cp -f "${PROGRAM_SOURCE_PATH}/gosh2.py" "${PROGRAM_INSTALL_SUB_PATH}/gosh2.py";
cp -f "${PROGRAM_SOURCE_PATH}/gosh.sh" "${PROGRAM_INSTALL_ROOT_PATH}/gosh.sh";

echo "$PROGRAM_NAME was installed at:";
echo "    $PROGRAM_INSTALL_ROOT_PATH";
echo "You **need** to source it to use, for example:";
echo "    source \"$PROGRAM_INSTALL_ROOT_PATH/gosh.sh\"";

echo "Done... ;D";
echo "";

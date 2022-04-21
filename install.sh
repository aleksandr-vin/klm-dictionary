#!/usr/bin/env bash

set -e

source .env

echo "Installing into ${DEST_PATH}".
mkdir -p "${DEST_PATH}"
ditto --noextattr --norsrc "objects/target/${DICT_NAME}.dictionary" "${DEST_PATH}/${DICT_NAME}.dictionary"
touch "${DEST_PATH}"
echo "Done."
echo "To test the new dictionary, open Dictionary.app, then open Preferences and enable ${DICT_NAME} dictionary"

#!/bin/sh
STORAGE_ACCOUNT_NAME=${1:-devstoreaccount1}

if [ $STORAGE_ACCOUNT_NAME = "devstoreaccount1" ]; then
    echo "Initializing emulator account '${STORAGE_ACCOUNT_NAME}'"
    BLOB_ARGS="--blob-endpoint https://localhost:10000/devstoreaccount1"
else
    echo "Initializing Azure storage account '${STORAGE_ACCOUNT_NAME}'"
    BLOB_ARGS="--account-name ${STORAGE_ACCOUNT_NAME}"
fi

echo "\tCreating data container"
az storage container create $BLOB_ARGS --auth-mode login --name data --public-access blob

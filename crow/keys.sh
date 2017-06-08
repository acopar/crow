#!/bin/bash

AUTH_FILE="/home/crow/cache/authorized_keys"
if [[ ! -f $AUTH_FILE ]]; then
    echo "No authorized_keys file"
    exit 0
fi

cp $AUTH_FILE /home/crow/.ssh/authorized_keys

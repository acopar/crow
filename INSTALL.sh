#!/bin/bash

DIRNAME=$(dirname $0)
if [ -e /dev/nvidiactl ]; then
    $DIRNAME/scripts/install-gpu-deps.sh
fi
$DIRNAME/scripts/install-docker.sh
#$DIRNAME/scripts/install-docker-compose.sh
if [ -e /dev/nvidiactl ]; then
    $DIRNAME/scripts/install-nvidia-docker2.sh
fi
$DIRNAME/scripts/install-crow.sh

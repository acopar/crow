#!/bin/bash

DIRNAME=$(dirname $0)
if [ -e /dev/nvidiactl ]; then
    $DIRNAME/RUN-GPU.sh
else
    $DIRNAME/RUN-CPU.sh
fi

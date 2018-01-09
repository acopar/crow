#!/bin/bash

DIRNAME=$(dirname $0)
$DIRNAME/scripts/install-gpu-deps.sh
$DIRNAME/scripts/install-docker.sh
#$DIRNAME/scripts/install-docker-compose.sh
$DIRNAME/scripts/install-nvidia-docker2.sh
$DIRNAME/scripts/install-crow.sh

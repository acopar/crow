#!/bin/bash

DIRNAME=$(dirname $0)
$DIRNAME/scripts/install-docker.sh
$DIRNAME/scripts/install-docker-compose.sh
$DIRNAME/scripts/install-nvidia-docker.sh
$DIRNAME/scripts/install-nvidia-docker-compose.sh

#!/bin/bash

DIRNAME=$(dirname $0)
$DIRNAME/scripts/install-docker.sh
$DIRNAME/scripts/install-docker-compose.sh

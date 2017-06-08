#!/bin/bash

DIRNAME=$(dirname $0)
$DIRNAME/scripts/install-docker.sh
$DIRNAME/scripts/install-docker-compose.sh
$DIRNAME/scripts/install-crow.sh
$DIRNAME/scripts/set-uid.sh
$DIRNAME/scripts/set-sshkey.sh

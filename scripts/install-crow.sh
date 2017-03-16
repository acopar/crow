#!/bin/bash

INSTALL_DIR=/usr/local/bin
CPATH=$(pwd)
DIRNAME=$(dirname $0)
cd $DIRNAME
sudo cp crow ${INSTALL_DIR}/crow
sudo cp crow-exec ${INSTALL_DIR}/crow-exec
sudo cp crow-ssh ${INSTALL_DIR}/crow-ssh

cd ${INSTALL_DIR}
sudo ln -s crow crow-test
sudo ln -s crow crow-conv

cd $CPATH

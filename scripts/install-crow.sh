#!/bin/bash

# update container if needed
docker pull acopar/crow:latest

# create links to helper scripts
INSTALL_DIR=/usr/local/bin
CPATH=$(pwd)
DIRNAME=$(dirname $0)
cd $DIRNAME
sudo cp crow ${INSTALL_DIR}/crow
sudo cp crow-exec ${INSTALL_DIR}/crow-exec
sudo cp crow-ssh ${INSTALL_DIR}/crow-ssh
sudo cp crow-start ${INSTALL_DIR}/crow-start

cd ${INSTALL_DIR}
sudo chmod +x crow crow-exec crow-ssh crow-start
if [ ! -e crow-test ]; then
    sudo ln -s crow crow-test
fi

if [ ! -e crow-conv ]; then
    sudo ln -s crow crow-conv
fi

cd $CPATH

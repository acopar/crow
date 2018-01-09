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
sudo cp crow-sudo ${INSTALL_DIR}/crow-sudo
sudo cp crow-ssh ${INSTALL_DIR}/crow-ssh
sudo cp crow-start ${INSTALL_DIR}/crow-start
sudo cp crow-stop ${INSTALL_DIR}/crow-stop
sudo cp crow-set-uid ${INSTALL_DIR}/crow-set-uid
sudo cp crow-set-sshkey ${INSTALL_DIR}/crow-set-sshkey

cd ${INSTALL_DIR}
sudo chmod +rx crow crow-exec crow-ssh crow-start crow-stop crow-set-uid crow-set-sshkey 
if [ ! -e crow-test ]; then
    sudo ln -s crow crow-test
fi

if [ ! -e crow-conv ]; then
    sudo ln -s crow crow-conv
fi

cd $CPATH

if [ ! -d data ]; then
    mkdir data
fi
if [ ! -d cache ]; then
    mkdir cache
fi
if [ ! -d results ]; then
    mkdir results
fi

#!/bin/bash

if which docker-compose; then
    echo "Docker-compose already installed"
    exit 0
fi

# Install docker-compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.11.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod a+x /usr/local/bin/docker-compose

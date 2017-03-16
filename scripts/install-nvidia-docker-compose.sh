#!/bin/bash

if which nvidia-docker-compose; then
    echo "Nvidia-docker-compose already installed"
    exit 0
fi

# Install nvidia-docker-compose
git clone https://github.com/eywalker/nvidia-docker-compose /tmp/nvidia-docker-compose
sudo cp /tmp/nvidia-docker-compose/bin/nvidia-docker-compose /usr/local/bin

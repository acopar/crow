#!/bin/bash

if which nvidia-docker; then
    echo "Nvidia-docker already installed"
    exit 0
fi

# Install nvidia-docker
VERSION='1.0.1'
wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v${VERSION}/nvidia-docker_${VERSION}_amd64.tar.xz
sudo tar --strip-components=1 -C /usr/bin -xvf /tmp/nvidia-docker*.tar.xz && rm /tmp/nvidia-docker*.tar.xz
#sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log

DIRNAME=$(dirname $0)

# Register with systemd
if [ -d /lib/systemd/system ]; then
    sudo cp $DIRNAME/service/nvidia-docker.service /lib/systemd/system/nvidia-docker.service
    sudo ln -s /lib/systemd/system/nvidia-docker.service /etc/systemd/system/nvidia-docker.service
    sudo systemctl enable nvidia-docker
    sudo systemctl start nvidia-docker
else
    echo "Systemd not available. Make sure this is executed at boot:"
    echo "sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log"
fi

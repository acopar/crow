.. _docker:

Docker setup guide
==================

Install docker engine
---------------------

These instructions work for Ubuntu Linux. For other Linux distributions and other platforms refer to the `Official docker install guide <https://docs.docker.com/engine/installation>`_.

::

    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install docker-ce

docker-compose
--------------

Download a recent version of docker compose:

::
    
    sudo curl -L "https://github.com/docker/compose/releases/download/1.11.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod a+x /usr/local/bin/docker-compose


nvidia-docker
-------------

Download and install nvidia-docker. These instructions work on all Linux distributions. Alternatively, Ubuntu and CentOS users can also use the `provided deb and rpm packages <https://github.com/NVIDIA/nvidia-docker>`_.

::

    wget -P /tmp https:?/github.com/NVIDIA/nvidia-docker/releases/download/v1.0.0/nvidia-docker_1.0.0_amd64.tar.gz
    sudo tar --strip-components=1 -C /usr/bin -xvf /tmp/nvidia-docker*.tar.xz && rm /tmp/nvidia-docker*.tar.xz
    sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log


nvidia-docker-compose
---------------------

Download and install nvidia-docker-compose:

::

    git clone https://github.com/eywalker/nvidia-docker-compose
    sudo cp nvidia-docker-compose/bin/nvidia-docker-compose /usr/local/bin
    
    
    

Troubleshooting
===============

The setup instructions for these application can change very quickly. If these instructions fail post a `issue on github <https://github.com/acopar/crow/issues>`_ so we can update them.
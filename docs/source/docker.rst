.. _docker:

Host requirements
=================

Docker install requirements for all environments:

* `docker-ce >= 17.03 <https://docs.docker.com/engine/installation>`_

Requirements for GPU environments:

* `CUDA >= 8.0 <https://developer.nvidia.com/cuda-downloads>`_
* `nvidia-docker >= 2.0 <https://github.com/NVIDIA/nvidia-docker>`_

If you don't have these programs on the system, you can install them using ``make`` (see below) or install them manually. If you install dependencies manually, run ``scripts/install-crow.sh`` after to install ``crow`` executables.


Quick setup
-----------

You can use the provided install scripts to setup requirements automatically. Currently Ubuntu-based systems are supported through helper scripts, otherwise, use manual instructions below. Clone the repository to access install scripts.

::
    
    git clone https://github.com/acopar/crow && cd crow


Install the framework and its dependencies (Ubuntu users):

::
    
    make install
    



CUDA
------------

If you do not have nvidia driver and CUDA on your system, refer to this section: :ref:`CUDA install guide <manual_cuda>`.


Docker engine
---------------------

Here are instructions for Ubuntu Linux. For other Linux distributions and other platforms refer to the `Official docker install guide <https://docs.docker.com/engine/installation>`_.

::

    sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    sudo apt-get update
    sudo apt-get install docker-ce


Nvidia-docker
-------------

Download and install nvidia-docker. These instructions will work on most Linux distributions. Alternatively, Ubuntu and CentOS users can also use the `provided deb and rpm packages <https://github.com/NVIDIA/nvidia-docker>`_. This software is for GPU hosts only.

::

    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
    curl -s -L https://nvidia.github.io/nvidia-docker/ubuntu16.04/amd64/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
    sudo apt-get update
    
    # Install nvidia-docker2 and reload the Docker daemon configuration
    sudo apt-get install -y nvidia-docker2
    sudo pkill -SIGHUP dockerd


Add user to docker group
------------------------

In order to execute docker commands as a regular user, you need to have docker privileges:

::

    sudo gpasswd -a $(whoami) docker    
    



Legacy nvidia-docker
====================

Use of nvidia-docker v1.0 is deprecated, we recommend the new v2.0, which is supported in the latest version of ``crow``. For backward compatibility, here are instructions on how to install the legacy version:

::

    wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1_amd64.tar.xz
    sudo tar --strip-components=1 -C /usr/bin -xvf /tmp/nvidia-docker*.tar.xz && rm /tmp/nvidia-docker*.tar.xz

In order to use nvidia-docker, you need to run ``nvidia-docker-plugin`` at boot. If this was not enabled through nvidia-docker packages (deb, rpm), you can run this command on system boot.

::
    
    sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log



nvidia-docker-compose
---------------------

Legacy versions also require ``nvidia-docker-compose`` library:

::

    git clone https://github.com/eywalker/nvidia-docker-compose
    sudo cp nvidia-docker-compose/bin/nvidia-docker-compose /usr/local/bin


This application depends on yaml python module, which can be installed with ``pip``.

::
    
    sudo pip install pyyaml


or using the packages from your distribution.

::
    
    sudo apt-get install python-yaml
    
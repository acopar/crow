.. _docker:

Host requirements
=================

Docker install requirements for all environments:

* `docker >= 1.12.9 <https://docs.docker.com/engine/installation>`_
* `docker-compose >= 1.9.0 <https://docs.docker.com/compose/install/>`_

Requirements for GPU environments:

* `CUDA >= 8.0 <https://developer.nvidia.com/cuda-downloads>`_
* `nvidia-docker >= 1.0.1 <https://github.com/NVIDIA/nvidia-docker>`_
* `nvidia-docker-compose <https://github.com/eywalker/nvidia-docker-compose>`_
* `Python library yaml <https://wiki.python.org/moin/YAML>`_.

If you don't have these programs on the system, you can install them using ``make`` (see below) or follow the links above to install them manually. Note that you still need to call ``make`` to install crow-specific entry points, user and group configuration and ssh keys.


Quick setup
-----------

You can use the provided install scripts to setup requirements automatically. Currently Ubuntu-based systems are supported through helper scripts, otherwise, use manual instructions below. Clone the repository to access install scripts.

::
    
    git clone https://github.com/acopar/crow && cd crow


For machines without CUDA-enabled GPU devices, use CPU version.

::
    
    make install
    

If you have GPU devices present, use the following command to also install GPU dependencies.

::

    make install-gpu



Install CUDA
------------

If you do not have nvidia driver and CUDA on your system, refer to this section: :ref:`CUDA install guide <manual_cuda>`.


Install docker engine
---------------------

Here are instructions for Ubuntu Linux. For other Linux distributions and other platforms refer to the `Official docker install guide <https://docs.docker.com/engine/installation>`_.

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

Download and install nvidia-docker. These instructions will work on most Linux distributions. Alternatively, Ubuntu and CentOS users can also use the `provided deb and rpm packages <https://github.com/NVIDIA/nvidia-docker>`_. This is for GPU environments only.

::

    wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1_amd64.tar.xz
    sudo tar --strip-components=1 -C /usr/bin -xvf /tmp/nvidia-docker*.tar.xz && rm /tmp/nvidia-docker*.tar.xz

In order to use nvidia-docker, you need to run ``nvidia-docker-plugin`` at boot. If this was not enabled through nvidia-docker packages (deb, rpm), you can run this command on system boot.

::
    
    sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log


If you have systemd, you can enable a nvidia-docker service like this:

::

    git clone https://github.com/acopar/crow
    cd crow/scripts/
    sudo cp service/nvidia-docker.service /lib/systemd/system/nvidia-docker.service
    sudo ln -s /lib/systemd/system/nvidia-docker.service /etc/systemd/system/nvidia-docker.service
    sudo systemctl enable nvidia-docker
    sudo systemctl start nvidia-docker



nvidia-docker-compose
---------------------

Download and install nvidia-docker-compose. For GPU environment only.

::

    git clone https://github.com/eywalker/nvidia-docker-compose
    sudo cp nvidia-docker-compose/bin/nvidia-docker-compose /usr/local/bin


This application depends on yaml python module, which can be installed with ``pip``.

::
    
    sudo pip install yaml


or using the packages from your distribution.

::
    
    sudo apt-get install python-yaml
    

Add user to docker group
------------------------

In order to execute docker commands as a regular user, you need to be in docker group.

::

    sudo gpasswd -a $(whoami) docker    
    

Troubleshooting
---------------

Default user in docker image has user id 1000, which may differ from the id of your host user. To avoid permission trouble inside the container, run the following script:

::

    scripts/user_permissions.sh


This must be re-run after you start a clean image and after each reinstall.


If additional problems occur, post a `issue on github <https://github.com/acopar/crow/issues>`_ so we can fix them.

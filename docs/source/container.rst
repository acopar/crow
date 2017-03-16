.. _container:

Start docker containers
=======================

Quick start
-----------

Start the container with provided ``RUN.sh`` script. 

::

    ./RUN.sh 

If this fails for any reason, try to start the containers manually (instructions below). Otherwise, you can skip the rest of this section and proceed with :ref:`connecting to a running container <container_connect>`.

Start GPU container
-------------------

Before the initial run of the container, you need to create docker volume for CUDA-related libraries. You only need to do this once, unless you remove the volume. Change the volume name depending on your driver version. You can check the driver version with nvidia-smi, or use the provided query script ``scripts/get_volume.py``. It this fails, check again if ``nvidia-docker-plugin`` is :ref:`set up correctly <docker>`.

::
    
    docker volume create -d nvidia-docker --name=nvidia_driver_367.57

After that, you can run the container with ``nvidia-docker-compose``, which will take care of pulling the official docker image from `Docker hub <hub.docker.org/acopar/crow>`_. 

::
    
    nvidia-docker-compose up

This process is automated in ``RUN-GPU.sh`` script. 

CPU only container
------------------

For CPU only install, use ``docker-compose`` directly.

::
    
    docker-compose up

This process is automated in ``RUN-CPU.sh`` script. 


Without docker-compose
----------------------

You can manually start CPU instances of docker container without docker-compose, but you will need to provide path to external volumes explicitly. With this command, you are dropped directly into the contanier and you can skip directly to the :ref:`data section <data>`. 

::

    docker run -v <source-dir>:/home/crow/src
             -v <data-dir>:/home/crow/data:ro
             -v <cache-dir>:/home/crow/cache
             -v <results-dir>:/home/crow/results
             --rm -it acopar/crow /bin/bash



.. _container_connect:

Connect to a running docker instance
====================================

If you used one of the install scripts, shortcuts were copied into your path, and you can use one of the following commands to attach to a container:


::
    
    crow-exec
    crow-ssh


If these commands are missing, you just need to run ``scripts/install-crow.sh`` or use this script, which is provided in the project home folder:

::

    ./CONNECT.sh

If this fails, check the output of ``docker ps`` and chec if the container is running.


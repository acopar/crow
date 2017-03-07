.. _install:

Installation
============

Setup guide
-----------

We recommend building and running CROW with docker to avoid recompiling libraries manually. If you want to install on host server directly, follow the :ref:`Manual setup <manual>`.

Install requirements:

* `docker >= 1.12.9 <https://docs.docker.com/engine/installation>`_
* `docker-compose >= 1.9.0 <https://docs.docker.com/compose/install/>`_
* `nvidia-docker >= 1.0.0 <https://github.com/NVIDIA/nvidia-docker>`_
* `nvidia-docker-compose <https://github.com/eywalker/nvidia-docker-compose>`_

If you don't have these programs installed, follow the :ref:`quick requirements installation <docker>` or links above for setup instructions on various platforms.


Move to directory containing Dockerfile and build the container with nvidia-docker-compose.

::
    
    nvidia-docker-compose build
    docker volume create --name=nvidia_driver_367.57


Once inside docker container, you can call the application to compute NMTF.




Supported platforms
-------------------
This software has been developed and tested for Linux platform. The provided docker images should also work on other platforms. Follow the `official instructions <https://docs.docker.com/engine/installation>`_ on how to set up docker environment for your platform.
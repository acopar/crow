.. _install:

Installation
============

Setup guide
-----------

We recommend building and running CROW with docker to avoid recompiling libraries manually. If you want to install on host server directly, follow the :ref:`Manual setup <manual>`.

Docker install requirements for all environments:

* `docker >= 1.12.9 <https://docs.docker.com/engine/installation>`_
* `docker-compose >= 1.9.0 <https://docs.docker.com/compose/install/>`_

Requirements for GPU environments:

* `CUDA >= 8.0 <https://developer.nvidia.com/cuda-downloads>`_
* `nvidia-docker >= 1.0.1 <https://github.com/NVIDIA/nvidia-docker>`_
* `nvidia-docker-compose <https://github.com/eywalker/nvidia-docker-compose>`_
* `Python library yaml <https://wiki.python.org/moin/YAML>`_.

If you don't have these programs installed, you can setup them using ``make``. Follow the :ref:`requirements setup guide <docker>` or links above for setup instructions of individual packages. 

::

    make install # install CPU-only version
    make install-gpu # install on a GPU system



If you have not done so while installing the requirements, clone the `crow git repository <https://github.com/acopar/crow>`_.

::
    
    git clone https://github.com/acopar/crow && cd crow


Configuration
-------------

Crow docker images makes use of the following external volumes. 

* crow: path to the crow source code 
* data: path to directory with data, mounted read-only.
* results: this is where the factorized data will be stored.
* cache: path to directory, where the application stores intermediate files. Starting with empty folder, the cache can take several gigabytes, depending on your data so make sure that you have enough space on the partition. You can safely clean this folder, but note that it may take some time to process the data again. 

Open the ``docker-compose.yml`` directory and make sure that the mount directories point to the desired locations. By default, mount points for each volume points to a folder in the current working directory. You can use symbolic links to connect path to your data, like this:

::

    ln -s <path-to-your-data-folder> data
    mkdir results
    mkdir -p ../tmp/crow-cache
    ln -s ../tmp/crow-cache cache

Alternatively, change ``docker-compose.yml`` to point to the desired locations, for example:

::

    - ./crow:/home/crow/src
    - /mnt/data:/home/crow/data:ro
    - ../tmp/crow-cache:/home/crow/cache
    - ./results:/home/crow/results


Start containers
----------------

Start the container with provided ``crow-start`` script. For manual run or development, check :ref:`manual setup guide <manual>`. To force CPU-only version on a system with GPUs available, you can explicitly call ``./RUN-CPU.sh``.

::

    crow-start


Then connect to a container with ``crow-exec`` script.

::

    crow-exec

Alternatively, you can connect to the container with ssh, using ``crow-ssh`` script.

::
    
    crow-ssh


If the above commands are not found, try to reinstall the application ``scripts/install-crow.sh`` or move to ``scripts`` folder and call them directly. Once inside docker the container, follow the :ref:`Tutorial <tutorial>` on how to use NMTF on your data. 


Supported platforms
-------------------
This software has been developed and tested for Linux platform. The provided docker images should also work on other platforms. Follow the `official instructions <https://docs.docker.com/engine/installation>`_ on how to set up docker environment for your platform.

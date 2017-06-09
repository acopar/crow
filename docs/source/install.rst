.. _install:

Installation
============

Setup guide
-----------

We recommend building and running CROW with docker to avoid recompiling libraries manually. If you want to install on host server directly, follow the :ref:`Manual setup <manual>`.



Before you use ``make`` you need to clone the repository `crow git repository <https://github.com/acopar/crow>`_.

::
    
    git clone https://github.com/acopar/crow && cd crow


Provide one of the two arguments ``install`` or ``install-gpu``, which depend on whether CUDA-enabled GPUs are available on your system. 

::

    make install # install CPU-only version
    make install-gpu # install on a GPU system


In case of any problems, check your dependencies and follow the :ref:`requirements setup guide <docker>`.

Start containers
----------------

Start the container with provided ``crow-start`` command. If you have any problems, check :ref:`manual setup guide <manual>`. To force CPU-only version on a system with GPUs available, you can explicitly call ``./RUN-CPU.sh``. To run docker container in the background, use:

::

    crow-start -d


.. _connect:

Connect to a running container
------------------------------

Then connect to a container with either ``crow-exec``, like this:

::

    crow-exec


Alternatively, you can ssh into the container. For login, ``crow-ssh`` uses dedicated identity files that are located at ~/.ssh/crow and ~/.ssh/crow.pub. The keys should be generated during installation and the public key should be copied authorized within the container automatically. If this fails for any reason, copy your public key to ``.ssh/authorized_keys`` inside the container.

::

    crow-ssh


You can login into container as admin like this:

::

    crow-sudo


If the above commands are not found, try to reinstall the application ``scripts/install-crow.sh`` or move to ``scripts`` folder and call them directly. Once inside docker the container, follow the :ref:`Tutorial <tutorial>` on how to use NMTF on your data. 


Test run
--------

Once you have the environment up and running, you can use this command to test if everything works correctly.

::
    
    crow-test


This command generates a small random dataset and tries to factorize it. To test factorization with GPUs, add ``-g`` switch.

::
    
    crow-test -g


Documentation for more in-depth benchmarks is found here :ref:`Benchmark <benchmark>`.


Location of data and results
----------------------------

Crow docker images makes use of the following external volumes. 

* crow: path to the crow source code (for development).
* data: path to directory with data, mounted read-only.
* results: this is where the factorized data will be stored.
* cache: path to directory, where the application stores intermediate files. Starting with empty folder, the cache can take several gigabytes, depending on your data so make sure that you have enough space on the partition. You can safely clean this folder, but note that it may take some time to process the data again. 

Open the ``docker-compose.yml`` directory and make sure that the mount directories point to the desired locations. By default, mount points for each volume points to a folder in the current working directory. Refer to the :ref:`data section  <data>` for more information. 


Supported platforms
-------------------

This software has been developed and tested for Linux platform. The provided docker images should also work on other platforms. Follow the `official instructions <https://docs.docker.com/engine/installation>`_ on how to set up docker environment for your platform.

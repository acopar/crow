.. _install:

Setup guide
===========

We recommend building and running CROW with docker to avoid recompiling libraries manually. If you want to install on host server directly, follow the :ref:`Manual setup <manual>`.



Before you use ``make`` you need to clone the repository `crow git repository <https://github.com/acopar/crow>`_.

::
    
    git clone https://github.com/acopar/crow && cd crow


The following command will install ``docker`` and copy ``crow`` executables. Depending on whether you have CUDA-enabled GPUs, it will also install nvidia-docker and CUDA toolkit.

::

    make install


In case of any problems, check your dependencies and follow the :ref:`requirements setup guide <docker>`.

Docker containers
=================

Start the container with provided ``crow-start`` command:

::

    crow-start


You can force CPU-only version on a system with GPUs available with ``crow-start cpu``. Container will run in the background. You can check if the container is running with ``docker ps``. You can stop the container with ``crow-stop`` command, or use specific ``docker`` commands (`Tutorial <https://docker-curriculum.com/>`_).


.. _connect:

Connect to a running container
------------------------------

Then connect to a container with either ``crow-exec``, like this:

::

    crow-exec


Alternatively, you can ssh into the container. For login, ``crow-ssh`` uses dedicated identity files that are located at ~/.ssh/crow and ~/.ssh/crow.pub. The keys are generated during installation added to container's authorized keys automatically.

::

    crow-ssh


You can login into container as admin like this:

::

    crow-sudo


Docker volumes
--------------

Crow docker images makes use of the following external volumes. 

* crow: path to the crow source code (for development versions).
* data: path to directory with data, mounted read-only.
* results: this is where the factorized data will be stored.
* cache: path to directory, where the application stores intermediate files. Starting with empty folder, the cache can take several gigabytes, depending on your data so make sure that you have enough space on the partition. You can safely clean this folder, but note that it may take some time to process the data again. 

By default, mount points for each volume points to a folder in the current working directory. Refer to the :ref:`data section  <data>` for more information on how to manage folders shared with the container. Any data not stored in shared folders will disappear when you stop the container.


Now, you can proceed to the :ref:`Tutorial <tutorial>`.


Non-sudo users
--------------

Users without administrator privileges need to be in ``docker`` group. Also, CUDA and nvidia-docker2 need to be installed on the host. You can manage containers with executables located in ``scripts`` folder (add it to your PATH). Once inside docker the container, follow the :ref:`Tutorial <tutorial>` on how to factorize your data. 


Test run
--------

After you have the environment up and running, you can use this command to test if everything works correctly. 

::
    
    crow-test -g


This command generates a small random dataset and tries to factorize it. The ``-g`` switch tells the test to use the GPUs.


Documentation for more in-depth benchmarks is found here :ref:`Benchmark <benchmark>`.


Supported platforms
-------------------

This software has been developed and tested for Linux platform. The provided docker images should also work on other platforms. Follow the `official instructions <https://docs.docker.com/engine/installation>`_ on how to set up docker environment for your platform.

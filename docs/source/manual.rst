.. _manual:

Manual setup
============

Alternatively, you can install manually (refer to the dockerfile for details).
Install requirements:

* Python == 2.7
* CUDA == 8.0
* openMPI >= 2.0 (make sure that the --with-cuda flag is set during configure time)
* openBLAS >= 1.12

Python
------

::

    apt-get install python-dev python-pip



.. _manual_cuda:

CUDA
----

If you have CUDA-enabled GPU devices, you have probably already installed nvidia drivers and CUDA. If not, you can install them from your package repository, like this:

::

    sudo apt-get install nvidia-cuda-toolkit
    reboot # nvidia driver requires reboot

This should also take care of installing current nvidia driver. If you want the latest version of CUDA or specific instructions for different platform, follow the `Official CUDA installation guide <http://docs.nvidia.com/cuda/cuda-installation-guide-linux>`_.


openMPI
-------

::

    wget https://www.open-mpi.org/software/ompi/v2.0/downloads/openmpi-2.0.0.tar.gz
    tar xzf openmpi-2.0.0.tar.gz
    cd openmpi-2.0.0
    ./configure --with-cuda=/usr/local/cuda --prefix=/openmpi
    make -j$(nproc) && make install

openBLAS
--------

::

    git clone https://github.com/xianyi/OpenBLAS
    cd OpenBLAS && make -j$(nproc) FC=gfortran && make PREFIX=/OpenBLAS install
    echo '/OpenBLAS/lib' > /etc/ld.so.conf.d/openblas.conf && ldconfig


NumPy
-----


Compile numpy with openblas support

::

    pip install cython
    git clone https://github.com/numpy/numpy
    printf "[openblas]\n" \
    "libraries = openblas\n" \
    "library_dirs = /OpenBLAS/lib\n" \
    "include_dirs = /OpenBLAS/include\n" \
    "runtime_library_dirs = /OpenBLAS/lib\n" >> numpy/site.cfg

    cd numpy && python setup.py config && \
        python setup.py build -j $(nproc) && python setup.py install
    

Other system dependencies
-------------------------

Install libraries required for cuda-cffi module and zmq module.

::

    apt-get install libffi-dev libzmq3-dev


Install crow and python dependencies
------------------------------------

Set up environment variables, so it can find CUDA, OpenBLAS and openMPI libraries. To make changes permanent after reboot, you need to append these lines to /etc/profile or ~/.bashrc (depending on your configuration).

::

    export PATH="/OpenBLAS/bin:/openmpi/bin:$PATH"
    export LD_LIBRARY_PATH="/OpenBLAS/lib:/openmpi/lib:$LD_LIBRARY_PATH"
    export CUDA_ROOT="/usr/local/cuda"


First download crow source from github.

::

    git clone https://github.com/acopar/crow
    cd crow


Install python requirements for CPU and GPU systems.

::

    pip install -r requirements.txt


GPU module dependencies
-----------------------

Install python modules for GPU environment. Skip this step on computer without GPU devices.

::

    pip install -r requirements-gpu.txt


You may need to get more recent version of scikit-cuda. 

::

    git clone https://github.com/lebedov/scikit-cuda
    cd scikit-cuda && python setup.py install


Install crow module
-------------------

Finally, you can install the package:

::

    python setup.py install


You can also use pip to install current package.

::

    pip install -e .


Test the configuration
----------------------

You can check if the installed modules work correctly by importing them. Also check if your CUDA_ROOT and PATH environment variables are set correctly. If you use different distribution, path to CUDA can be different. 

::

    echo $CUDA_ROOT
    ls $CUDA_ROOT


::

    python -c 'import pycuda' # CUDA for python library
    python -c 'from cuda_cffi import cusparse' # for sparse GPU operations
    python -c 'import numpy; numpy.__config__.show()' # check blas info
.. _tutorial:

Tutorial
========

The application reads the provided ``coo`` file into data matrix *X*. Then it the data into three non-negative latent factors, such that:

.. math::
    
    X \approx U S V^T


Examples
--------

Serial configuration using one CPU core where both factorization ranks are 20.

::

    crow -k1 20 data.coo


Using single GPU, number of iterations is set to 200 and factorization ranks are 20x30. 

::

    crow -g -k1 20 -k2 30 -i 200 data.coo


Example usage for 4-GPU run with 2x2 block configuration and factorization rank 20.

::

    crow -g -b 2x2 -k1 20 data.coo


When the process is finished, you should have the following files in ``results`` directory:

* U.npz - contains left factor matrix. 
* V.npz - contains right factor matrix.
* S.npz - contains middle factor matrix.


Command line arguments
----------------------

The following options can be set:

* -b: block configuration, for example 2x2.
* -e: calculate and print error function in each iteration. This can slow down factorization considerably.
* -g: use this argument to run on GPUs. By default, only CPU cores will be used.
* -i: maximum number of iterations, default is 100.
* -k1: left factorization rank. Defines number of latent vectors of matrix U.
* -k2: right factorization rank. Defines number of latent vectors of matrix V. By default, value of k1 is used. 
* -o: impose orthogonality in factors U and V. By default non-orthogonal NMTF will be used. 
* -p: parallelization degree, by default number of blocks equals to parallelization degree, but you can use parallelization degree smaller than the number of blocks. 
* -s: use sparse data structures. Do not use this if the matrix density is larger than 10%.
* -t: additional stopping criteria. By default, factorization will run for number of iterations specified by -i.

Arguments:

* Single argument specifies path to data file. You can also provide basename of data files that exist in :ref:`data directory <data>`.


.. _tutorial:

Tutorial
========

The application reads the provided ``coo`` file into data matrix *X*. Then it the data into three non-negative latent factors, such that:

.. math::
    
    X \approx U S V^T



Command line arguments
----------------------

The program takes the following arguments:

* -a: factorization rank, for example ``k=20``, or ``k=20,l=30`` if the factorization ranks are different.
* -b: block configuration, for example 2x2.
* -e: calculate and print error function in each iteration. This can slow down factorization considerably.
* -g: use this argument to run on GPUs. By default, only CPU cores will be used.
* -i: maximum number of iterations, default is 100.
* -o: impose orthogonality in factors U and V. By default non-orthogonal NMTF will be used. 
* -p: parallelization degree, by default number of blocks equals to parallelization degree, but you can use parallelization degree smaller than the number of blocks. 
* -s: Use sparse data structures. Do not use this if the matrix density is larger than 10%.
* -t: additional stopping criteria, default is None.
* Last argument is path to data file.

Examples
--------

Serial configuration using one core, run for 100 iterations.

::

    crow -i 100 -a k=20 ../data/data.coo

Example usage for 4-GPU run with 2x2 block configuration and factorization rank 20.

::

    crow -g -p 4 -b 2x2 -a k=20 -i 100 ../data/data.coo


When the process is finished, you should have the following files in ``results`` directory:

* U.npz - contains left factor matrix. 
* V.npz - contains right factor matrix.
* S.npz - contains middle factor matrix.
* factors.pkl - pickle file containing dictionary with numpy matrices. Numpy matrices contain the same values as csv files, but raw format. More efficient than csv if you use python to further process the data.
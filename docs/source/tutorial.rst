.. _tutorial:

Tutorial
========


Command line arguments
----------------------

The program takes the following arguments:

* -a: factorization rank, for example k=20, or k=20,l=30 if the factorization ranks differ.
* -b: block configuration, for example 2x2.
* -e: calculate and print error function in each iteration. 
* -g: use this argument to use GPUs. By default, only CPU cores will be used.
* -i: maximum number of iterations.
* -p: parallelization degree: must be equal or less than the number of blocks. 
* -r: update rules. Use nmtf_long for non-orthogonal or nmtf_ding for orthogonal NMTF.
* -s: Use sparse data structures. Do not use this if the matrix density is larger than 10%.
* Last argument is path to data file.

Examples
--------

Serial configuration using one core, run for 100 iterations.

.. 

    crow -i 100 -a k=20 ../data/data.csv

Example usage for 4-GPU run with 2x2 block configuration and factorization rank 20.

.. 

    crow -g -p 4 -b 2x2 -a k=20 -i 100 ../data/data.csv



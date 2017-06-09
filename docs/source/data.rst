.. _data:

Docker volumes
==============

Crow docker images makes use of the following external volumes. 

* crow: path to the crow source code (for development).
* data: path to directory with data, mounted read-only.
* results: this is where the factorized data will be stored.
* cache: path to directory, where the application stores intermediate files. Starting with empty folder, the cache can take several gigabytes, depending on your data so make sure that you have enough space on the partition. You can safely clean this folder, but note that it may take some time to process the data again. 

Open the ``docker-compose.yml`` directory and make sure that the mount directories point to the desired locations. By default, mount points for each volume points to a folder in the current working directory. Refer to the :ref:`data section  <data>` for more information. 

You can use symbolic links to connect path to your data, like this:

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


.. _data_manipulation:

Data manipulation
=================

Before you can factorize your data, you first need to convert it into an appropriate format.

Input data
----------
The data can be provided in coordinate list format (coo), which is a form of csv file, where each row describes one element in a matrix with row, column, value and header stores matrix dimensions. In header, we define matrix dimensions **n,m**. After that, each row of the file represents one non-zero value in the matrix. In each row, the first column represents index at first dimension **i**, second column index of second dimension **j** and third column represents the value of data matrix **X** at location X[i,j].

For example, consider this 2D matrix:

::

    [[1, 0, 0], [5, 5, 0]]

Corresponding ``coo`` data file would look like this:

::

    2,3
    0,0,1
    1,0,5
    1,1,5


The following formats are used:

* coo - this is the default input data format, using coordinate list representation. 
* npz - this method uses `numpy.savez <https://docs.scipy.org/doc/numpy/reference/generated/numpy.savez.html>`_.  Default format for resulting factors. It is also used to cache dense or csr sparse matrices internally.
* pkl - used to store other python data, such as dictionaries.
* csv - not used internally, but supported through conversion. Note that when converting back, there is no header line. 


Convert between different csv and coo formats
---------------------------------------------

By default, data format used is coordinate list file (coo), and is currently used to represent input data for both sparse and dense matrices. However, dense matrices are often formated with a 2D csv table, separated by commas or tabulars. The following commands show examples how can you convert existing csv file into coo format. If there is a header line, you need to provide an option, so the converter knows to ignore the first row.


::

    crow-conv --header 2d-table.csv coo-value-list.coo


Examples with explicit delimiter (comma by default) and no header.

::

    crow-conv -d comma 2d-table.csv key-value.coo
    crow-conv -d tab 2d-table.tab key-value.coo


Convert between npz and csv
---------------------------

Without command line arguments, the conversion is done based on file extension. If the file extension does not correspond to the content, use arguments to explicitly tell the input and output type. Arguments are checked with ``crow-conv --help``.

::
    
    crow-conv results/U.npz results/U.coo
    crow-conv results/U.npz results/U.csv

Pickle to csv
-------------

There is also a convenience tool, which can convert pickled numpy array to csv format (dense).

::
    
   crow-conv test.pkl test.csv
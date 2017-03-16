.. _data:

Data manipulation
=================

In order to use the application, you first need to convert your data into appropriate format. 

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
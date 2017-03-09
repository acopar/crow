.. _data:

Data manipulation
=================

In order to use the application, you first need to convert your data into appropriate format. 

Input data
----------
The data can be provided in csv in row-column-value format, which is a common non-binary format to store sparse matrix data. In header, we define matrix dimensions **n,m**. After that, each row of the csv file represents one non-zero value in the matrix. In each row, the first column represents index at first dimension **i**, second column index of second dimension **j** and third column represents the value of data matrix **X** at location X[i,j].

For example, consider this 2D matrix:

::

    [[1, 0, 0], [5, 5, 0]]

Corresponding data file would look like this:

::

    2,3
    0,0,1
    1,0,5
    1,1,5


The following formats are used:

* csv - this is the default input and output data format, using row-column-value representation. 
* npz - this method uses `numpy.savez <https://docs.scipy.org/doc/numpy/reference/generated/numpy.savez.html>`_, used to store dense or csr sparse matrices internally.
* pkl - used to store other python data, such as dictionaries.

Convert between different csv formats
-------------------------------------

Csv by default is recognized as row-column-value file, which is common for sparse matrices. However, dense matrices are often formated with a 2D table, separated by commas or tabulars. If there is a header line, you need to provide an option, so the converter knows to ignore the first row.


::

    crow-csv --header 2d-table.csv key-value.csv


Examples with explicit delimiter (comma by default) and no header.

::

    crow-csv -d comma 2d-table.csv key-value.csv
    crow-csv -d tab 2d-table.tab key-value.csv

Convert between npz and csv
---------------------------

Without command line arguments, the conversion is done based on file extension. If the file extension does not correspond to the content, use one of the arguments, which you can see with command ``crow-conv --help``.

::
    
    crow-conv results/U.npz results/U.csv

Pickle to csv
-------------

There is also a convenience tool, which can convert pickled numpy array to csv format.

::
    
   crow-conv test.pkl test.csv
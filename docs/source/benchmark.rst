.. _data:

Download data
=============

To download preprocessed benchmark datasets, use the provided ``get_datasets.sh`` script.
::

    scripts/get_datasets.sh


This script downloads five datasets that have already been converted into coordinate list format:

* [ArrayExpress](http://file.biolab.si/crow/ArrayExpress.coo): 22283x5896, file size: 3.5GB
* [TCGA-BRCA](http://file.biolab.si/crow/TCGA-BRCA.coo): 1222x60483, file size: 1.5GB
* [Fetus](http://file.biolab.si/crow/fetus.coo): 25569x25608, file size: 622M
* [Retina](http://file.biolab.si/crow/retina.coo): 25823x25822, file size: 2.9GB
* [Cochlea](http://file.biolab.si/crow/cochlea.coo): 25824x25824, file size: 5.6GB


Benchmark
=========


Quick start
-----------

Download repository ``crow-plot`` benchmarking and plotting framework and run it. Note that for this to work, you need to have a running crow docker container.

::

    git clone https://github.com/acopar/crow-plot
    cd crow-plot
    ./speedup-bench.sh


If everything works correctly, you should have a few png and pdf files in img directory. The results should give you an idea on speedups you can get from your hardware configuration. 


Run benchmark
-------------

This part is already included in ``speedup-bench`` script, however if you want to change parameters or use a different visualization, you need to run this stage of the script separately.

::

    python crowpl/benchmark.py ArrayExpress TCGA-BRCA fetus retina cochlea
    

If you want to test non-default configurations, edit ``crowpl/benchmark.py`` file and change global EXPERIMENTS variable. To include your own dataset (assuming, it is already stored in data directory), you must also include it in SPARSE_MAP dictionary as well as adding it as an argument to the python script. To test orthogonal NMTF, you need to provide method option, for example:

::

    python crowpl/benchmark.py -m nmtf_ding <your-dataset-name>
    

Visualize results
-----------------

When running benchmarks, you can read the time of iteration for each configuration from the terminal. If you wath to visualize, you can use the automated script which uses docker image, or install the packages manually. 

The results that you see in the output of benchmark script, are also stored in the results folder in csv files. If you want to use automated visualization framework, use the following command:

::

    scripts/crow-plot python /app/crowpl -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea
    
To avoid the use of docker image for visualization, you can install ``crow-plot`` module manually. System dependencies of ``crow-plot`` are imagemagick and latex in addition to python modules listed in requirements.txt.

::

    python setup.py install
    python crowpl -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea

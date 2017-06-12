.. _benchmark:

Download data
=============

To download preprocessed benchmark datasets, use the provided ``get_datasets.sh`` script.
::

    scripts/get_datasets.sh


This script downloads five datasets that have already been converted into coordinate list format:

* `ArrayExpress <http://file.biolab.si/crow/ArrayExpress.coo>`_: 22283x5896, file size: 3.5GB
* `TCGA-BRCA <http://file.biolab.si/crow/TCGA-BRCA.coo>`_: 1222x60483, file size: 1.5GB
* `Fetus <http://file.biolab.si/crow/fetus.coo>`_: 25569x25608, file size: 622M
* `Retina <http://file.biolab.si/crow/retina.coo>`_: 25823x25822, file size: 2.9GB
* `Cochlea <http://file.biolab.si/crow/cochlea.coo>`_: 25824x25824, file size: 5.6GB


Benchmark
=========

When running benchmarks, you can read the time of iteration for each configuration from the terminal. If you wath to visualize, you can use the automated scripts, which use docker image.


Quick start
-----------

Download repository ``crow-plot`` benchmarking and plotting framework and run it. Note that for this to work, you need to have a running crow docker container.

::

    git clone https://github.com/acopar/crow-plot
    cd crow-plot
    ./speedup-bench.sh


If everything works correctly, you should have a few png and pdf files in img directory. The results should give you an idea on speedups you can get from your hardware configuration. 


Benchmark list
--------------

Here is a list of available benchmarks:

* speedup-bench.sh: comparison of speedup on 1-4GPUs compared to a single processor configuration.
* efficiency-bench.sh: efficiency and communication overhead of multi-block configurations as described by percentage of linear speedup. 
* rank-bench.sh: impact of factorization rank on speed.
* balanced-bench.sh: speedup of balanced partitioning compared to imbalanced partitioning on sparse datasets.


By default, GPU and multi-GPU configurations are compared against single-processor configuration. If you want to compare the speedup of multi-processor against a single-processor as well, add ``-a`` option to each benchmark script, for example:

::

    ./speedup-bench.sh -a


To test orthogonal NMTF, you need to provide ``-o`` option to the script:

::

    ./speedup-bench.sh -o


Note, that for orthogonal visualizations, you need to run visualization separately (see the next section).

Visualize results
-----------------

The results that you see in the output of benchmark script, are also stored in the results folder in csv files. If you want to visualize the results, you can use the provided ``scripts/crow-plot`` script, like this:

::

    scripts/crow-plot python /app/crowpl -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea


Option ``-a`` defines which type of visualization to perform. Available visualizations types are:


* speedup: visualize speedup compared to single-processor approach.
* efficiency: visualize efficiency on multi-block configurations.
* transfer: visualize percentage of communication overhead.
* k: visualize iteration times for different factorization ranks.
* balance: visualize speedup of balanced partitioning over imbalanced on sparse data.

To visualize results for orthogonal NMTF benchmarks, you also need to provide ``-o`` argument.

::

    scripts/crow-plot python /app/crowpl -o -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea



Manual setup
------------

To run benchmarks without visualization, it is not necessary to install the ``crow-plot`` package. You can run this command directly, provided that crow docker container is running. 

::

    python crowpl/benchmark.py ArrayExpress TCGA-BRCA fetus retina cochlea


Benchmark command line arguments:

* -a: run all experiments, including multi-processor.
* -c: run with disabled data transfer for communication overhead calculation.
* -i: run sparse datasets imbalanced, thus checking the partitioning speedup.
* -o: run orthogonal NMTF (Ding et al., 2006) instead of default non-orthogonal (Long et al., 2005) method.
* -r: benchmark factorization rank values.
* -u: update, configurations that were already computed are skipped. 


To avoid the use of docker image for visualization, you can install ``crow-plot`` module manually. System dependencies of ``crow-plot`` are imagemagick and latex in addition to python modules listed in requirements.txt.

::

    python setup.py install


After the installation is complete you can run crowpl module like this:

::

    python crowpl -a speedup ArrayExpress TCGA-BRCA fetus retina cochlea

# CROW: Fast Non-Negative Matrix Tri-Factorization

A scalable implementation of non-negative matrix tri-factorization for multi-processor and multi-GPU environments.

## Quick Setup ###

The most convenient way to setup the environment is to use provided docker images. Here is a quick setup guide for Ubuntu-based platforms. For other platforms and detailed setup instructions, please refer to the [Online documentation](https://crow.readthedocs.io/).

#### Clone git repository

```sh
    git clone https://github.com/acopar/crow
    cd crow
```

#### Install for CPU-only environment

This script skips CUDA and nvidia-docker installation. Useful for systems without CUDA-enabled GPU devices. This command also updates crow docker image to the latest version. 

```sh
    make install
```

#### Install for GPU environment

```sh
    make install-gpu
```

#### Start docker container

This script checks if there are nvidia devices present, otherwise it falls back to CPU-only version (use `-d` option to put the process in the background). See [Setup guide](https://crow.readthedocs.io/en/latest/install.html) for details.


```sh
    crow-start
```

## Attach to a running container

To get inside the container use `crow-exec` or `crow-ssh`.

```sh
    crow-exec
```

Check [this section](https://crow.readthedocs.io/en/latest/install.html#connect) if you encounter any problems with connection. 

### Test your configuration

Once you have the environment up and running, you can use `crow-test` script to test if everything works correctly. This generates a small random dataset and tries to factorize it. To test factorization using GPU environment, use `-g` switch.

```sh
    crow-test -g
```

## Volumes and data

### Docker volumes

Crow docker images makes use of the following external volumes:
- crow: path to the crow source code (for development)
- data: path to directory with data, mounted read-only.
- cache: path to directory, where the application stores intermediate files. 
Note that cache can take several gigabytes, depending on your data. You can 
safely clean this folder, but note that it may take some time to process the data again. 
- results: this is where the factorized data will be stored.

You can modify the volume paths depending on where you store the data on your host system. This can be done by editing docker-compose.yml prior to `docker-compose` or `nvidia-docker-compose` call. By default, docker-compose creates the folders in the current directory. Instead of editing docker-compose file you can also use symbolic links or mount to link data, cache or results to a different folder or device.

### Data

To download preprocessed benchmark datasets, use the provided ``get_datasets.sh`` script.
```
    scripts/get_datasets.sh
```

This script downloads datasets that have already been preprocessed and converted into coordinate list or npz format:
- [ArrayExpress](http://file.biolab.si/crow/ArrayExpress.coo): 22283x5896, file size: 3.5GB
- [TCGA-BRCA](http://file.biolab.si/crow/TCGA-BRCA.coo): 1222x60483, file size: 1.5GB
- [Fetus](http://file.biolab.si/crow/fetus.coo): 25569x25608, file size: 622M
- [Retina](http://file.biolab.si/crow/retina.coo): 25823x25822, file size: 2.9GB
- [Cochlea](http://file.biolab.si/crow/cochlea.coo): 25824x25824, file size: 5.6GB
- [TCGA-Methyl](http://file.biolab.si/crow/TCGA-Methyl.npz): 10181x485577, file size: 19GB
- [TCGA-Methyl (cancer gene subset)](http://file.biolab.si/crow/TCGA-Methyl-cancer.npz): 10181x14299, file size: 556MB

#### Data format

The data can be provided in coordinate list format (coo), which is a form of csv file, where each row describes one element in a matrix with row, column, value and header stores matrix dimensions. In header, we define matrix dimensions **n,m**. After that, each row of the file represents one non-zero value in the matrix. In each row, the first column represents index at first dimension **i**, second column index of second dimension **j** and third column represents the value of data matrix **X** at location X[i,j].

For example, consider this 2D matrix:
```
    [[1, 0, 0], [5, 5, 0]]
```
Corresponding data file would look like this:
```
    2,3
    0,0,1
    1,0,5
    1,1,5
```

For convenient conversion between csv, npz and coo formats, ``crow-conv`` tool is provided in the docker image. Additional instructions can be found in [Data manipulation section](https://crow.readthedocs.io/en/latest/data.html).


## Factorize your data

### Examples

Here, we demonstrate how to quickly factorize data on one of the provided datasets. To use different data, just replace the filename. Factorization rank (20 in these cases) is defined with '-k1' option. 

For example: to factorize ArrayExpress dataset on 1-CPU, 1-GPU and 4-GPU (2x2 block) configurations, use the following commands:

```
    crow -k1 20 ArrayExpress.coo
    crow -g -k1 20 ArrayExpress.coo
    crow -g -b 2x2 -k1 20 ArrayExpress.coo
```

Once the process is finished, you will see average iteration time (seconds) and Frobenius norm error function. Factorized data is stored in results folder. 

Note that first run takes longer (up to a few minutes), since the program needs to read large files from disk and convert them to dense numpy or sparse matrices. Subsequent runs on the same data will load faster, because the data is cached. More detailed information on how to reproduce and visualize the results can be found in the [Benchmark section](https://crow.readthedocs.io/en/latest/benchmark.html). We demonstrate application of NMTF including interpretation of results a [co-clustering example](https://github.com/acopar/crow-example).


### Command line arguments

The following options can be set:

- -b: block configuration, for example 2x2.
- -e: calculate and print error function in each iteration. This can slow down factorization considerably.
- -g: use this argument to run on GPUs. By default, only CPU cores will be used.
- -i: maximum number of iterations, default is 10, but you should increase this number to get satisfactory results. 
- -k1: left factorization rank. Defines number of latent vectors of matrix U.
- -k2: right factorization rank. Defines number of latent vectors of matrix V. By default, value of k1 is used. 
- -o: impose orthogonality in factors U and V. By default non-orthogonal NMTF will be used. 
- -p: parallelization degree, by default number of blocks equals to parallelization degree, but you can use parallelization degree smaller than the number of blocks. Useful to reduce memory requirements in GPU applications.
- -s: use sparse data structures. Do not use this if the matrix density is larger than 10%.
- -t: additional stopping criteria. By default, factorization will run for the number of iterations specified by -i. Available arguments are e4, e5, e6, e7. For example, when passing e6 parameter, the factorization stops after error function in two consecutive iterations changes for less than 10^-6. 

Arguments:

- Single argument specifies path to data file. You can also provide basename of data files that exist in data directory.

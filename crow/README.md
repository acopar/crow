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

This script skips CUDA and nvidia-docker installation. Useful for systems without CUDA-enabled GPU devices.

```sh
    ./INSTALL_CPU.sh
```

#### Install for GPU environment

```sh
    ./INSTALL_GPU.sh
```

#### Start docker container

This script checks if there are nvidia devices present, otherwise it falls back to CPU-only version.

```sh
    ./RUN.sh
```

## Attach to a running container

```sh
    ./CONNECT.sh
```

Alternatively, you can ssh into the container, you just need to check ssh port of the container with `docker ps`.

```
    ssh -p <container-ssh-port> crow@localhost
```

### Test your configuration

Once you have the environment up and running, you can use this script to test if everything works correctly.

```sh
    crow-test
```

This generates a small random dataset and tries to factorize it. 



## Docker volumes

Crow docker images makes use of the following external volumes:
- crow: path to the crow source code 
- data: path to directory with data, mounted read-only.
- cache: path to directory, where the application stores intermediate files. 
Note that cache can take several gigabytes, depending on your data. You can 
safely clean this folder, but note that it may take some time to process the data again. 
- results: this is where the factorized data will be stored.

You can modify the volume paths depending on where you store the data on your host system. This can be done by editing docker-compose.yml prior to `docker-compose` or `nvidia-docker-compose` call. By default, docker-compose creates the folders in the current directory. Therefore, you can also use symbolic links and point to the directory where you want to store data, cache or results.


## Data format

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

You can use provided tool `crow-conv` to conveniently convert between csv and coo formats.


### Command line arguments

The program takes the following arguments:

- -a: factorization rank, for example ``k=20``, or ``k=20,l=30`` if the factorization ranks are different.
- -b: block configuration, for example 2x2.
- -e: calculate and print error function in each iteration. This can slow down factorization considerably.
- -g: use this argument to run on GPUs. By default, only CPU cores will be used.
- -i: maximum number of iterations, default is 100.
- -o: impose orthogonality in factors U and V. By default non-orthogonal NMTF will be used. 
- -p: parallelization degree, by default number of blocks equals to parallelization degree, but you can use parallelization degree smaller than the number of blocks. 
- -s: Use sparse data structures. Do not use this if the matrix density is larger than 10%.
- -t: additional stopping criteria, default is None.
- Last argument is path to data file.


### Examples

Serial configuration using one core, run for 100 iterations.

    crow -i 100 -a k=20 ../data/data.coo

Example usage for 4-GPU run with 2x2 block configuration and factorization rank 20.

    crow -g -p 4 -b 2x2 -a k=20 -i 100 ../data/data.coo



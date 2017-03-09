# CROW 
============
A scalable implementation of non-negative matrix tri-factorization for multi-processor and multi-GPU environments.

### Quick Setup ###
-------------------

The most convenient way to setup the environment is to use provided docker images. Refer to the [Online documentation](https://crow.readthedocs.io/) for detailed explanation on how to setup your environment. Here is a quick setup guide.

#### CPU-only version

First, clone the crow source repository.
```sh
    git clone https://github.com/acopar/crow crow
    cd crow
    nvidia-docker-compose up
```

#### GPU-enabled version

First, clone the crow source repository.
```sh
    git clone https://github.com/acopar/crow crow
    cd crow
    docker-compose up
```

#### Docker volumes

Crow docker images makes use of the following external volumes:
- crow: path to the crow source code 
- data: path to directory with data, mounted read-only.
- cache: path to directory, where the application stores intermediate files. 
Note that cache can take several gigabytes, depending on your data. You can 
safely clean this folder, but note that it may take some time to process the data again. 
- results: this is where the factorized data will be stored.

You can modify the volume paths depending on where you store the data on your host system. This can be done by editing docker-compose.yml prior to `docker-compose` or `nvidia-docker-compose` call. By default, docker-compose tries to connect the volumes in current directory. Therefore, you can also use symbolic links and point to the directory where you want to store data, cache or results.

You can do this by creating symbolic links or in the same directory as docker-compose.yml, for example:
```sh
    ln -s <path-to-your-data-folder> data
    mkdir /tmp/crow-cache
    ln -s /tmp/crow-cache cache
    mkdir results
```

After you changed volume paths, you need to call docker-compose again.
```sh
    docker volume create --name=nvidia_driver_367.57
    nvidia-docker-compose up
```

#### Connect to the container

Now, you can connect to the running docker container:

```
    docker exec --it crow_head_1 /bin/bash
```

Alternatively, you can ssh into the container, you just need to check the correct ssh port with `docker ps`.

```
    ssh -p <container-ssh-port> mpirun@localhost
```

#### Run docker standalone

If you run docker container as standalone application, instead of using `docker-compose`, 
you need to provide path to external volumes manually. For GPU-enabled version refer to the `nvidia-docker-compose.yml` file (which is generated after initial `nvidia-docker-compose`) and provide all volumes and devices from command line. 

```sh
   docker run -v <source-dir>:/home/mpirun/crow 
             -v <data-dir>:/home/mpirun/data:ro
             -v <cache-dir>:/home/mpirun/cache 
             -v <results-dir>:/home/mpirun/results
             --rm -it acopar/crow /bin/bash
```

### Test your configuration ###
-------------------------------

Once you have the environment up and running, you can use this script to test if everything works correctly.
```sh
    crow-test
```
This generates a small random dataset and tries to factorize it.

### Data format ###
-------------------
The data can be provided in csv in row-column-value format (regardless of data sparsity). In header, we define matrix dimensions **n,m**. After that, each row of the csv file represents one non-zero value in the matrix. In each row, the first column represents index at first dimension **i**, second column index of second dimension **j** and third column represents the value of data matrix **X** at location X[i,j].

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

There is a convenience tool, which can convert pickled numpy array to the correct format.

```
   crow-convert test.pkl test.csv
```


### Command line arguments ###
-------------------------

The program takes the following arguments:
- -a: factorization rank, for example k=20, or k=20,l=30 if the factorization ranks differ.
- -b: block configuration, for example 2x2.
- -e: calculate and print error function in each iteration. 
- -g: use this argument to use GPUs. By default, only CPU cores will be used.
- -i: maximum number of iterations.
- -p: parallelization degree: must be equal or less than the number of blocks. 
- -r: update rules. Use nmtf_long for non-orthogonal or nmtf_ding for orthogonal NMTF.
- -s: Use sparse data structures. Do not use this if the matrix density is larger than 10%.
- Last argument is path to data file.

### Usage examples ###
-----------------

Serial configuration using one core, run for 100 iterations.

    crow -i 100 -a k=20 ../data/data.csv

Example usage for 4-GPU run with 2x2 block configuration and factorization rank 20.

    crow -g -p 4 -b 2x2 -a k=20 -i 100 ../data/data.csv



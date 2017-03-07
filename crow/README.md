CROW 
============
A scalable implementation of non-negative matrix tri-factorization for multi-processor and multi-GPU environments.

### Setup ###
------------

Docker
-----------
We recommend building and running CROW with nvidia-docker to ensure the environment is set up correctly.

Install prerequesites:
- docker >= 1.2
- docker-compose >= 1.9.0
- nvidia-docker >= 1.0.0 (https://github.com/NVIDIA/nvidia-docker)
- nvidia-docker-compose (https://github.com/eywalker/nvidia-docker-compose)

Install docker (for other distributions follow the [[https://docs.docker.com/engine/installation]official install guide])
```
sudo apt-get install docker.io
```

Download recent version of docker compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.11.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod a+x /usr/local/bin/docker-compose
```

Download and install nvidia-docker:
```
wget -P /tmp https:?/github.com/NVIDIA/nvidia-docker/releases/download/v1.0.0/nvidia-docker_1.0.0_amd64.tar.gz
sudo tar --strip-components=1 -C /usr/bin -xvf /tmp/nvidia-docker*.tar.xz && rm /tmp/nvidia-docker*.tar.xz
sudo -b nohup nvidia-docker-plugin > /tmp/nvidia-docker.log
```

Move to directory containing Dockerfile and build the container with nvidia-docker-compose.
```
nvidia-docker-compose build
docker volume create --name=nvidia_driver_367.57
```

Run the container and attach the data directory:
```
nvidia-docker run -v $DATA_DIR:/home/mpirun/src/data -it crowdocker_crow_head /bin/bash
```
Once inside docker container, you can call the application to compute NMTF (see usage section for examples).

Alternatively, you can call the program directly:
```
nvidia-docker run -v $DATA_DIR:/home/mpirun/src/data -it crowdocker_crow_head crow -i 100 -a k=20 data.csv
```

Manual setup
------------
Alternatively, you can install manually.

Install prerequesites:
- Python == 2.7
- openBLAS >= 1.12
- openMPI >= 2.0 (make sure that the --with-cuda flag is set during configure time)
- CUDA == 8.0

Install python modules for CPU environment:

    pip install -r requirements.txt

Install python modules for GPU environment (skip this step on computer without GPU devices):

    pip install -r requirements-gpu.txt

Install library:

    python setup.py install

You can also run

    pip install -e .


Data Format
-----------
The data can be provided in csv in row-column-value format. For example of this numpy array:
```
    [[1, 0, 0], [5, 5, 0]]
```
Corresponding data file would look like this:

    0,0,1
    1,0,5
    1,1,5
   

Usage
-----

Serial configuration using one core, run for 100 iterations.

    crow -i 100 -a k=20 data.csv

Example usage for 4-GPU run with 2x2 block configuration and factorization rank 20.

    crow -g -p 4 -b 2x2 -a k=20 -i 100 data.csv


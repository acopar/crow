Setup guide
============

### Docker ###
--------------

We recommend building and running CROW with nvidia-docker to ensure the environment is set up correctly.

Install prerequesites:
- docker >= 1.12.9
- docker-compose >= 1.9.0
- nvidia-docker >= 1.0.0 (https://github.com/NVIDIA/nvidia-docker)
- nvidia-docker-compose (https://github.com/eywalker/nvidia-docker-compose)

Install docker engine. These instructions work for Ubuntu linux. For troubleshooting and other distributions follow the [[https://docs.docker.com/engine/installation] Official docker install guide].
```
sudo apt-get install apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce
```

Download a recent version of docker compose:
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

Once inside docker container, you can call the application to compute NMTF (see [[https://github.com/acopar/crow/README.md]usage section] for examples).


### Manual setup ###
--------------------
Alternatively, you can install manually (refer to the dockerfile for details).

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

You can also use pip to install current package.

    pip install -e .



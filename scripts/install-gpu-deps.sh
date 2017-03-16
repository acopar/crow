#!/bin/bash

if [ $(which locate) == "" ]; then
    sudo apt-get install locate
fi

has_yaml=$(python -c 'import yaml' 2>&1 | wc -l)
has_cuda=$(locate libcuda.so | wc -l)

if [ $has_yaml -ne 0 ]; then
    sudo apt-get install python-yaml
fi

if [ $has_cuda -eq 0 ]; then
    sudo apt-get install nvidia-cuda-toolkit
fi


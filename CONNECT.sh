#!/bin/bash

if [ $# -eq 0 ]; then
    docker exec -it crow_head_1 su -m mpirun 
else
    docker exec -it crow_head_1 su -m mpirun -s /bin/bash -c "$*"
fi

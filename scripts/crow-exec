#!/bin/bash

if [ $# -eq 0 ]; then
    docker exec -it crow_head_1 su -m crow
else
    docker exec -it crow_head_1 su -m crow -s /bin/bash -c "$*"
fi

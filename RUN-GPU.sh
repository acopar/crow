#!/bin/bash

VOLUME=$(python scripts/nvidia_get_volume.py)
if [ -z $VOLUME ]; then
    echo "No nvidia volume found"
    echo "Perhaps nvidia-docker-plugin is not running?"
    exit 0
fi

has_volume=$(docker volume ls | grep $VOLUME | wc -l)
if [ $has_volume -eq 0 ]; then
    echo "Creating volume $VOLUME..."
    docker volume create -d nvidia-docker --name=$VOLUME
fi

nvidia-docker-compose up

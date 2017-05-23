#!/bin/bash

CPATH=$(pwd)
DIRNAME=$(dirname $0)
cd $DIRNAME
for file in ArrayExpress TCGA-BRCA fetus retina cochlea; do
    if [ -f ../data/$file.coo ]; then
        echo "File $file is already downloaded"
        continue
    fi
    wget http://file.biolab.si/crow/$file.coo -O ../data/$file.coo
done

cd $CPATH

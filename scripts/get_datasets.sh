#!/bin/bash

CPATH=$(pwd)
DIRNAME=$(dirname $0)
cd $DIRNAME
for file in ArrayExpress.coo TCGA-BRCA.coo fetus.coo retina.coo cochlea.coo TCGA-Methyl.npz TCGA-Methyl-cancer.npz; do
    if [ -f ../data/$file ]; then
        echo "File $file is already downloaded"
        continue
    fi
    wget http://file.biolab.si/crow/$file -O ../data/$file
done

cd $CPATH

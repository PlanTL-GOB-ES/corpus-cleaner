#!/usr/bin/env bash

mkdir -p CorpusCleaner/lib

# Onion
wget -O onion-1.2.tar.gz 'http://corpus.tools/raw-attachment/wiki/Downloads/onion-1.2.tar.gz'
tar xzf onion-1.2.tar.gz
mv onion-1.2 CorpusCleaner/lib
PREFIX=CorpusCleaner/lib/onion-1.2
echo "#JUDY_INC=-I/opt/local/include
#JUDY_LIB=-L/opt/local/lib
PREFIX=${PREFIX}
INSTALL_BIN=${PREFIX}/bin
INSTALL_DATA=${PREFIX}/share" > CorpusCleaner/lib/onion-1.2/Makefile.config
make -C CorpusCleaner/lib/onion-1.2
make -C CorpusCleaner/lib/onion-1.2 install

# fasttext
wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
mv lid.176.bin CorpusCleaner/lib/
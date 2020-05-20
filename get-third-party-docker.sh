#!/usr/bin/env bash

mkdir -p /cc/corpus-cleaner/lib

# Onion
wget -O onion-1.2.tar.gz 'http://corpus.tools/raw-attachment/wiki/Downloads/onion-1.2.tar.gz'
tar xzf onion-1.2.tar.gz
mv onion-1.2 /cc/corpus-cleaner/lib
PREFIX=/cc/corpus-cleaner/lib/onion-1.2
echo "#JUDY_INC=-I/opt/local/include
#JUDY_LIB=-L/opt/local/lib
INSTALL_BIN=${PREFIX}/bin
INSTALL_DATA=${PREFIX}/share" > /cc/corpus-cleaner/lib/onion-1.2/Makefile.config
make -C /cc/corpus-cleaner/lib/onion-1.2
make -C /cc/corpus-cleaner/lib/onion-1.2 install

# fasttext
wget -q https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
mv lid.176.bin /cc/corpus-cleaner/lib/

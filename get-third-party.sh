#!/usr/bin/env bash
mkdir -p lib

# Onion
wget -O onion-1.2.tar.gz 'http://corpus.tools/raw-attachment/wiki/Downloads/onion-1.2.tar.gz'
tar xzf onion-1.2.tar.gz
mv onion-1.2 lib
cd lib/onion-1.2/
PREFIX=$(pwd)
sudo apt-get install libjudy-dev gawk rsync
echo "#JUDY_INC=-I/opt/local/include
#JUDY_LIB=-L/opt/local/lib
PREFIX=${PREFIX}
INSTALL_BIN=${PREFIX}/bin
INSTALL_DATA=${PREFIX}/share" > Makefile.config
make
make install
cd ../..
rm onion-1.2.tar.gz


# fasttext
wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
mv lid.176.bin lib/

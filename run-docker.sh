#!/usr/bin/env bash

o=$(realpath output)
d=$(realpath data)

docker build -t corpuscleaner . && docker run -v ${o}:/output -v ${d}:/data -it corpuscleaner $*
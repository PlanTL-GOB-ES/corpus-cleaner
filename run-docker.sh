#!/usr/bin/env bash

o=$(realpath output)
d=$(realpath data)

docker run -v ${o}:/scratch/output -v ${d}:/scratch/data -it corpuscleaner $*
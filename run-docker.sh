#!/usr/bin/env bash

o=$(realpath output)
d=$(realpath data)

docker run -v ${o}:/cc/output -v ${d}:/cc/data -it corpuscleaner $*
#!/usr/bin/env bash

o=$(realpath output)
d=$(realpath data)

docker build -t corpuscleaner .
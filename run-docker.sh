#!/usr/bin/env bash
docker build -t corpuscleaner . && docker run -v output:/output -v data:/data -it corpuscleaner

docker build -t dv . && docker run -v mount:/mount -it dv
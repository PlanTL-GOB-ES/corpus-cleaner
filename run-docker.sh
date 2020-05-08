#!/usr/bin/env bash
docker build -t corpuscleaner . && docker run -v output:/output -v data:/data -it corpuscleaner
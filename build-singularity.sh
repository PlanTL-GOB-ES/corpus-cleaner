#!/usr/bin/env bash


docker run -v /var/run/docker.sock:/var/run/docker.sock  -v $(realpath .):/output  --privileged -t --rm  quay.io/singularity/docker2singularity -m "/scratch/data /scratch/output" --name corpuscleaner-singularity corpuscleaner

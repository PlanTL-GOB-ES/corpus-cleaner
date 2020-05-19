#!/usr/bin/env bash

USER="dummyuser"
GROUP="dummygroup"
VERSION=$(date +"%d/%m/%Y")
PATH="/gpfs/projects/${GROUP}/corpus-cleaner/${VERSION}"

scp -r corpuscleaner-singularity.sif run-singularity.sh run-singularity-slurm.sh data/ output/ ${USER}@dt01.bsc.es:${PATH}
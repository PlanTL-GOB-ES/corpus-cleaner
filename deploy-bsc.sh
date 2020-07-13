#!/usr/bin/env bash

USER="dummyuser"
GROUP="dummygroup"
VERSION=$(date +"%d-%m-%Y")
DIR_PATH="/gpfs/projects/${GROUP}/corpus-cleaner/${VERSION}"
ssh ${USER}@dt01.bsc.es 'mkdir -p ' ${DIR_PATH}/data ${DIR_PATH}/output ${DIR_PATH}/logs
scp -r corpuscleaner-singularity.sif run-singularity.sh run-singularity-slurm.sh ${USER}@dt01.bsc.es:${DIR_PATH}

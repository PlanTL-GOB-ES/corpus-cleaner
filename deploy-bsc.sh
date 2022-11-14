#!/usr/bin/env bash

USER=$1
SUFFIX=$2
VERSION=$(date +"%d-%m-%Y")_$SUFFIX
DIR_PATH="/gpfs/projects/bsc88/tools/corpus-cleaner/${VERSION}"
ssh ${USER}@dt01.bsc.es 'mkdir -p ' ${DIR_PATH}/data ${DIR_PATH}/output ${DIR_PATH}/logs ${DIR_PATH}/scripts
scp -r corpuscleaner-singularity.sif run-singularity.sh run-singularity.slurm.sh run-singularity-dist.slurm.sh corpuscleaner-singularity-legacy.sif ${USER}@dt01.bsc.es:${DIR_PATH}
ssh ${USER}@dt01.bsc.es 'find ' ${DIR_PATH} ' -type d -exec chmod 775 {} +'
ssh ${USER}@dt01.bsc.es 'find ' ${DIR_PATH} ' -type f -exec chmod 664 {} +'

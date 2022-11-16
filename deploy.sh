#!/usr/bin/env bash

USER=$1
HOSTNAME=$2 
DEPLOY_DIR=$3
NAME=$4

VERSION=$(date +"%d-%m-%Y")-${NAME}
RELEASE_NOTE=release-note-container.txt
echo -e "\nPlease, add a description of the current version features:" >> ${RELEASE_NOTE}
vim ${RELEASE_NOTE}

# Then, deploy corpus-cleaner container, scripts and toy data
DIR_PATH=${DEPLOY_DIR}/${VERSION}
ssh ${USER}@${HOSTNAME} 'mkdir -p ' ${DIR_PATH}/data ${DIR_PATH}/output ${DIR_PATH}/logs ${DIR_PATH}/scripts
scp -r corpuscleaner-singularity.sif run-singularity.sh run-singularity.slurm.sh run-singularity-dist.slurm.sh run-resume-singularity.sh data/toy_wiki ${USER}@${HOSTNAME}:${DIR_PATH}
ssh ${USER}@${HOSTNAME} 'find ' ${DIR_PATH} ' -type d -exec chmod 775 {} +'
ssh ${USER}@${HOSTNAME} 'find ' ${DIR_PATH} ' -type f -exec chmod 664 {} +'

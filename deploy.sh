#!/usr/bin/env bash

USER=$1
HOSTNAME=$2 
DEPLOY_DIR=$3
NAME=$4

VERSION=$(date +"%d-%m-%Y")-${NAME}

# First, create release note for the current version
RELEASE_NOTE="release-note-container.txt"
start=$(git log | grep -n commit | sed -n "1p" | cut -d ":" -f 1)
end=$(git log | grep -n commit | sed -n "2p" | cut -d ":" -f 1)
end=$(echo ${end} - 1 | bc)

echo $(git log | sed -n "${start},${end}p") > ${RELEASE_NOTE}
echo -e "\nPlease, add a brief description of the deploy below:" >> ${RELEASE_NOTE}
vim ${RELEASE_NOTE}

# Then, deploy corpus-cleaner container, scripts and toy data
DIR_PATH=${DEPLOY_DIR}/${VERSION}
ssh ${USER}@${HOSTNAME} 'mkdir -p ' ${DIR_PATH}/data ${DIR_PATH}/output ${DIR_PATH}/logs ${DIR_PATH}/scripts
scp -r corpuscleaner-singularity.sif run-singularity.sh run-singularity.slurm.sh run-singularity-dist.slurm.sh data/toy_wiki ${USER}@${HOSTNAME}:${DIR_PATH}
ssh ${USER}@${HOSTNAME} 'find ' ${DIR_PATH} ' -type d -exec chmod 775 {} +'
ssh ${USER}@${HOSTNAME} 'find ' ${DIR_PATH} ' -type f -exec chmod 664 {} +'

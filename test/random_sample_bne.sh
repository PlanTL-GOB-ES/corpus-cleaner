#!/bin/bash
# Small script to randomly sample file from BNE corpora
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DATA_DIR=$1
SAMPLE_SIZE=$2
NUMBER_FILES=$3
SEED=${4:-42}

if [[ -z ${DATA_DIR}] || -z ${SAMPLE_SIZE} ]]; then
  echo "Please pass DATA_DIR and SAMPLE_SIZE arguments"
  exit 0
fi

MAX_NUMBER_FILES=200
if [[ ${NUMBER_FILES} -gt ${MAX_NUMBER_FILES} ]]; then
  echo "A maximum number of 200 random files can be extracted to avoid memory errors"
  exit 0
fi

SAMPLE_DIR=${SCRIPT_DIR}/random_sample_bne_${SAMPLE_SIZE}
mkdir -p ${SAMPLE_DIR}

# Generates random seed for shuffling
get_seeded_random()
{
  SEED=$1
  openssl enc -aes-256-ctr -pass pass:"${SEED}" -nosalt \
    </dev/zero 2>/dev/null
}

function random_sample_files_bne() {
  DATA_DIR=$1
  NUMBER_FILES=$2
  SEED=$3
  find ${DATA_DIR} -type f  -not -name '*metadat.json' | \
    shuf -n ${NUMBER_FILES} --random-source=<(get_seeded_random ${SEED})
}

function read_lines() {
    INPUT_FILE=$1
    while IFS= read -r line; do
      echo "$line"
    done < ${INPUT_FILE}
}

# First, sample ${NUMBER_FILES} random files from each BNE directory and write their content to a single file
echo "Creating random sample of BNE files of size "
cat $(random_sample_files_bne ${DATA_DIR} ${NUMBER_FILES} ${SEED}) > \
  ${SAMPLE_DIR}/files_bne_${NUMBER_FILES}

RANDOM_SAMPLE_FILES_SIZE=$(du -h ${SAMPLE_DIR}/files_bne_${NUMBER_FILES} | cut -f1)
echo "Collected random sample of BNE files with size: ${RANDOM_SAMPLE_FILES_SIZE}"

# Second, sample ${SAMPLE_SIZE} documents from the previous ${NUMBER_FILES} random files
echo "Extracting ${SAMPLE_SIZE} random documents"
read_lines ${SAMPLE_DIR}/files_bne_${NUMBER_FILES} | \
  shuf -n ${SAMPLE_SIZE} --random-source=<(get_seeded_random ${SEED}) >> \
    ${SAMPLE_DIR}/docs_bne_${SAMPLE_SIZE}

rm ${SAMPLE_DIR}/files_bne_${NUMBER_FILES}

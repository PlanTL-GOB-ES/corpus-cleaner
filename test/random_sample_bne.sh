#!/bin/bash
# Small script to randomly sample file from BNE corpora
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

DATA_DIR=$1
SAMPLE_SIZE=$2
SEED=$3

if [[ -z ${DATA_DIR}] || -z ${SAMPLE_SIZE} ]]; then
  echo "Please pass DATA_DIR and SAMPLE_SIZE arguments"
  exit 0
fi

if [[ -z ${SEED} ]]; then
  SEED=42
fi

SAMPLE_DIR=${SCRIPT_DIR}/random_sample_bne_${SAMPLE_SIZE}
mkdir -p ${SAMPLE_DIR}


# Generates random seed for shuffling
get_seeded_random()
{
  openssl enc -aes-256-ctr -pass pass:"$SEED" -nosalt \
    </dev/zero 2>/dev/null
}

function random_sample_files_bne() {
  DATA_DIR=$1
  find ${DATA_DIR} -type f  -not -name '*metadat.json' | shuf -n 100 --random-source=<(get_seeded_random ${SEED})
}

function read_lines() {
    INPUT_FILE=$1
    while IFS= read -r line; do
      echo "$line"
    done < ${INPUT_FILE}
}

# First, sample 1000 random files from each BNE directory and write their content to a single file
echo "Create random sampling of BNE files"
cat $(random_sample_files_bne ${DATA_DIR}) > ${SAMPLE_DIR}/files_bne_1000

# Second, sample ${SAMPLE_SIZE} documents from the previous 1000 random files
echo "Extracting random ${SAMPLE_SIZE} documents"
read_lines ${SAMPLE_DIR}/files_bne_1000 | shuf -n ${SAMPLE_SIZE} --random-source=<(get_seeded_random ${SEED}) >> \
  ${SAMPLE_DIR}/docs_bne_${SAMPLE_SIZE}
rm ${SAMPLE_DIR}/files_bne_1000

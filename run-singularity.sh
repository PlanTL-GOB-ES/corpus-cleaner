#!/usr/bin/env bash
module load singularity/3.6.4

PARAMETERS="example-output \
        --input-path data/toy_wiki  \
        --input-format wikipedia \
        --output-format fairseq-lm \
        --lang-filter ca \
        --parallel"



singularity exec --writable-tmpfs \
           --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif \
           bash -c "cd /cc/corpus-cleaner && python3 clean.py $*"
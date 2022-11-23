#!/usr/bin/env bash
module load singularity/3.6.4

PARAMETERS="example-output \
        --input-path data/toy_wiki  \
        --input-format wikipedia \
        --output-format fairseq-lm \
        --lang-filter ca \
        --parallel"



singularity exec --writable-tmpfs \
           --bind $(realpath data):/cc/cc/data --bind $(realpath outputcc/):/cc/output corpuscleaner-singularity.sif \
           bash -ccc/ "cd /cc/corpus-cleaner && python3 clean.py $*"
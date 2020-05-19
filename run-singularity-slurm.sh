#!/usr/bin/env bash

module load singularity/3.5.2

PARAMETERS="example-output --input-path data/toy_wiki --input-format wikipedia --output-format fairseq-lm --lang-filter ca"

bash run-singularity.sh ${PARAMETERS}
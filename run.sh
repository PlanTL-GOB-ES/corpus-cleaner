#!/usr/bin/env bash
source venv/bin/activate

PARAMETERS="example-output \
        --input-path data/toy_wiki  \
        --input-format wikipedia \
        --output-format fairseq-lm \
        --lang-filter ca \
        --parallel"

python clean.py $PARAMETERS
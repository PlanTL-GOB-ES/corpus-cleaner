#!/usr/bin/env bash

rm -rf /scratch/corpus-cleaner/data && rm -rf /scratch/corpus-cleaner/output && ln -s /scratch/data /scratch/corpus-cleaner/data && ln -s /scratch/output /scratch/corpus-cleaner/output && cd /scratch/corpus-cleaner && python3 clean.py $*
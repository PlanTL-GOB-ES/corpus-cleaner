#!/usr/bin/env bash

rm -rf /scratch/CorpusCleaner/data && rm -rf /scratch/CorpusCleaner/output && ln -s /scratch/data /scratch/CorpusCleaner/data && ln -s /scratch/output /scratch/CorpusCleaner/output && cd /scratch/CorpusCleaner && python3 clean.py $*
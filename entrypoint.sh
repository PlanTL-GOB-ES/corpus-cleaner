#!/usr/bin/env bash

rm -rf /CorpusCleaner/data && rm -rf /CorpusCleaner/output && ln -s /scratch/data /CorpusCleaner/data && ln -s /scratch/output /CorpusCleaner/output && cd /CorpusCleaner && python3 clean.py $*
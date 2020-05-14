#!/usr/bin/env bash

ln -s /scratch/data /CorpusCleaner/data && ln -s /scratch/output /CorpusCleaner/output && cd /CorpusCleaner && python3 clean.py $*
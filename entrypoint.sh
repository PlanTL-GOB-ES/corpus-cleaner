#!/usr/bin/env bash

ls CorpusCleaner/data && rm -rf data/ && rm -rf output/ && ln -s /data CorpusCleaner/data && ln -s /output CorpusCleaner/output && python3 CorpusCleaner/clean.py $*
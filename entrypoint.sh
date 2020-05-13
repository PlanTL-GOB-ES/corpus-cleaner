#!/usr/bin/env bash

ln -s /data /CorpusCleaner/data && ln -s /output /CorpusCleaner/output && cd /CorpusCleaner && python3 clean.py $*
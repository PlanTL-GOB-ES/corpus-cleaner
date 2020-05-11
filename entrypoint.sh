#!/usr/bin/env bash

ln -s /data CorpusCleaner/data && ln -s /output CorpusCleaner/output && ls CorpusCleaner/data && python3 CorpusCleaner/clean.py $*
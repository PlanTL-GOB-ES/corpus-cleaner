#!/usr/bin/env bash

rm -rf /cc/CorpusCleaner/data && rm -rf /cc/CorpusCleaner/output && ln -s /cc/data /cc/CorpusCleaner/data && ln -s /cc/output /cc/CorpusCleaner/output && cd /cc/CorpusCleaner && python3 clean.py $*
#!/usr/bin/env bash

ln -s /data CorpusCleaner/data & ln -s /output CorpusCleaner/output & python3 CorpusCleaner/clean.py $*
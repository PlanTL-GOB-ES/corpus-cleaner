#!/usr/bin/env bash

rm -rf /cc/corpus-cleaner/data && rm -rf /cc/corpus-cleaner/output && ln -s /cc/data /cc/corpus-cleaner/data && ln -s /cc/output /cc/corpus-cleaner/output && cd /cc/corpus-cleaner && python3 clean.py $*

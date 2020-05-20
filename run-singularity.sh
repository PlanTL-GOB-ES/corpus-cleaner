#!/usr/bin/env bash

singularity exec --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif bash -c "cd /cc/corpus-cleaner && python3.6 clean.py $*"
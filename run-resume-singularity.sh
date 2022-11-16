#!/usr/bin/env bash
module load singularity/3.6.4

OUTPUT_DIR="$(find output -type d -name "example-output*")"

singularity exec --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif bash -c "cd /cc/corpus-cleaner && python3 resume.py ${OUTPUT_DIR}"
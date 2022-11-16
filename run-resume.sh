#!/usr/bin/env bash
OUTPUT_DIR=$(find output -type d -name "example-output*")
python resume.py $OUTPUT_DIR
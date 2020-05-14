#!/usr/bin/env bash

sudo singularity run --writable-tmpfs --bind $(realpath data):/scratch/data --bind $(realpath output):/scratch/output *.sif $*

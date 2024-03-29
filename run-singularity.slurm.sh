#!/usr/bin/env bash
#SBATCH --job-name=corpuscleaner
#SBATCH --output=logs/corpuscleaner_%j.out
#SBATCH --error=logs/corpuscleaner_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=48
#SBATCH --time=2-00:00:00
# Use parallel to run in parallel (1 node)
module load singularity/3.6.4

PARAMETERS="example-output \
        --input-path data/toy_wiki  \
        --input-format wikipedia \
        --output-format fairseq-lm \
        --lang-filter ca \
        --parallel"


bash run-singularity.sh ${PARAMETERS}
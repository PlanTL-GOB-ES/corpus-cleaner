#!/usr/bin/env bash
#BSUB -J   corpuscleaner
#BSUB -W   48:00
#BSUB -cwd "."
#BSUB -oo  "logs/corpuscleaner_%J.out"
#BSUB -eo  "logs/corpuscleaner_%J.err"
#BSUB -n   1
#BSUB -R   "span[ptile=16]"
#BSUB -x

module purge && module load singularity/3.2.0

PARAMETERS="example-output --input-path data/toy_wiki --input-format wikipedia --output-format fairseq-lm --lang-filter ca"

bash run-singularity-legacy.sh ${PARAMETERS}

#!/usr/bin/env bash
#SBATCH --job-name=corpuscleaner
#SBATCH --output=logs/corpuscleaner_%j.out
#SBATCH --error=logs/corpuscleaner_%j.err
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=48
#SBATCH --time=2-00:00:00
#SBATCH --wait
#SBATCH --wait-all-nodes=1



module load singularity/3.5.2
PARAMETERS="example-output --input-path data/toy_wiki --input-format wikipedia --output-format fairseq-lm --parallel --backend ray --lang-filter ca"


hostlist=$(scontrol show hostname $SLURM_JOB_NODELIST)
master=$(echo "${hostlist}" | head -n 1)

yaml_path=$(singularity exec --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif bash -c "cd /cc/corpus-cleaner && python3.6 dist.py ${hostlist}")
singularity exec --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif bash -c "cd /cc/corpus-cleaner && ray up ${yaml_path} && ray attach ${yaml_path} && python3.6 clean.py ${PARAMETERS}"


wait
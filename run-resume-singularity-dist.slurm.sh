#!/usr/bin/env bash
#SBATCH --job-name=corpuscleaner
#SBATCH --output=logs/corpuscleaner_%j.out
#SBATCH --error=logs/corpuscleaner_%j.err
#SBATCH --ntasks=3
#SBATCH --cpus-per-task=48
#SBATCH --time=2-00:00:00
#SBATCH --wait
#SBATCH --wait-all-nodes=1

# --parallel & --backend ray are needed to execute in distributed mode!
OUTPUT_DIR="$(find output -type d -name "example-output*")"

module load singularity/3.6.4

hostlist=$(scontrol show hostname $SLURM_JOB_NODELIST)
master=$(echo "${hostlist}" | head -n 1)

work_dir=$(pwd)

echo ${hostlist}

singularity instance start --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif cc
singularity exec instance://cc bash -c "ray start --head --port=6379"


i=1
while [ $i -lt $SLURM_JOB_NUM_NODES ]
do
  j=$(($i + 1))
  host=$(echo "${hostlist}" | sed "${j}q;d")
  echo $master  ${SLURM_JOB_NUM_NODES} ${i}
  ssh -n "$host" "module load singularity/3.6.4; cd ${work_dir}; singularity instance start --writable-tmpfs --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity.sif cc; singularity exec instance://cc bash -c \"ray start --address=${master}:6379\"" &
  ((i++))
done
sleep 30
singularity exec instance://cc bash -c "cd /cc/corpus-cleaner && RAY_ADDRESS=auto python3 resume.py ${OUTPUT_DIR}"


wait

#!/usr/bin/env bash
#BSUB -J corpuscleaner
#BSUB -cwd "."
#BSUB -oo logs/corpuscleaner_%J.out
#BSUB -eo logs/corpuscleaner_%J.err
#BSUB -n 3
#BSUB -R "span[ptile=1]"
#BSUB -x
#BSUB -W 48:00
#BSUB --wait
#BSUB --wait-all-nodes=1

mkdir -p logs
PARAMETERS="warc --input-path data/cat-warc --input-format warc --output-format fairseq-lm --lang-filter ca --parallel --backend ray"
module purge && module load singularity/3.2.0


hostlist=( $LSB_HOSTS )
master=${hostlist[0]}

length=${#hostlist[@]}

work_dir=$(pwd)

echo $LSB_HOSTS

singularity exec --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity-legacy.sif bash -c "ray start --head --port=6379" &

i=1
while [ $i -lt $length ]
do
  host=${hostlist[i]}
  echo $master ${length} ${i}
  ssh -n "$host" "module purge && module load singularity/3.2.0; cd ${work_dir}; singularity exec --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity-legacy.sif bash -c \"ray start --address=${master}:6379\"" &
  ((i++))
done
sleep 30

singularity exec --bind $(realpath data):/cc/data --bind $(realpath output):/cc/output corpuscleaner-singularity-legacy.sif bash -c "cd /cc/corpus-cleaner && python3.6 clean.py ${PARAMETERS}"

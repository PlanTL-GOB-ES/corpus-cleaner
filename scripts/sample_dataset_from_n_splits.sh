#!/usr/bin/bash
#SBATCH --job-name="generate_data_codiesp"
#SBATCH -D .
#SBATCH --output=../logs/generate_data_%j.out
#SBATCH --error=../logs/generate_data_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=128
#SBATCH --time=2:00:00

module load mkl/2018.4 gcc/10.2.0 rocm/5.1.1 intel/2018.4 python/3.7.4
export LD_LIBRARY_PATH=/gpfs/projects/bsc88/projects/bne/eval_amd/scripts_to_run/external-lib:$LD_LIBRARY_PATH

ENV_DIR="/gpfs/projects/bsc88/projects/bio_eval/env/"
source $ENV_DIR/bin/activate

equal_splits_path="/gpfs/scratch/bsc88/bsc88437/corpora/bne_short/equal_splits"
target_path="/gpfs/scratch/bsc88/bsc88437/corpora/bne_short"
tokenizer="/gpfs/projects/bsc88/BERTs/models/biomedical_and_clinical_models/v2/roberta-base-es-biomedical-clinical-swm-vocab-50k/converted_hf"

num_train_splits=40
num_dev_splits=20
num_test_splits=20

num_dev_documents_per_split=200
num_test_documents_per_split=200


python sample_dataset_from_n_splits.py \
 --splits_path=$equal_splits_path \
 --target_path=$target_path \
 --tokenizer_path=$tokenizer \
 --num_train_splits=$num_train_splits \
 --num_dev_splits=$num_dev_splits \
 --num_test_splits=$num_test_splits \
 --num_dev_documents_per_split=$num_dev_documents_per_split \
 --num_test_documents_per_split=$num_test_documents_per_split

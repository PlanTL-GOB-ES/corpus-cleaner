#!/bin/bash
# Small script to perform a balanced random sampling from multiple corpus
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

data_dirs=${data_dirs}
exclude_names=${exclude_names}
sample_size=${sample_size}
output_file=${output_file}
debug=${debug:-false}
seed=${seed:-42}

# add named arguments from: https://brianchildress.co/named-parameters-in-bash/
while [[ $# -gt 0 ]]; do
   if [[ $1 == *"--"* ]]; then
        param="${1/--/}"
        declare ${param}="$2"
        # echo $1 $2 // Optional to see the parameter:value result
   fi
  shift
done

# Generates random seed for shuffling
get_seeded_random()
{
    seed=$1
    openssl enc -aes-256-ctr -pass pass:"${seed}" -nosalt \
      </dev/zero 2>/dev/null
}

function find_files(){
    data_dir=$1
    exclude_names=$2

#    for data_dir in "${data_dirs}"; do
    if [[ ${exclude_names} == "false" ]]; then
        find ${data_dir} -type f
    else
        # add options dynamically
        command="find ${data_dir} -type f"
        for name in ${exclude_names}; do
            command+=" -not -name \"*${name}\""
        done
        eval ${command}
    fi
#    done
}

function random_files_sample(){
    files=$1
    number_files=$2
    seed=$3

    shuf -e ${files} -n ${number_files} --random-source=<(get_seeded_random ${seed})
}

function random_lines_sample(){
    file=$1
    sample_size=$2
    number_lines=$3
    seed=$4

    cat ${file} | sed '/^$/d' | sort | uniq | shuf -n  ${number_lines} --random-source=<(get_seeded_random ${seed})
}

function count_file_lines(){
    file=$1
    cat ${file} | sed '/^$/d' | wc -l
}


# handle arguments values before to perform the sampling
number_dirs=$(echo ${data_dirs} | wc -w)
if [[ ${sample_size} -lt ${number_dirs} ]]; then
    echo "Set sample_size to a larger number than number_dirs"
    exit 0
fi

if [[ ${sample_size} -lt ${number_files} ]]; then
    echo "Set sample_size to a larger number than number_files"
    exit 0
fi

if [[ -z "${exclude_names}" ]]; then
    exclude_names=false
fi

if [[ -z "${sample_size}" ]]; then
    sample_size=1000
fi

if [[ -z "${output_file}" ]]; then
    output_file=${SCRIPT_DIR}/sample.${sample_size}.txt
    if [[ ${debug} == "true" ]]; then
      output_file=${SCRIPT_DIR}/sample.${sample_size}.debug.txt
    fi
else
    mkdir -p $(dirname ${output_file})
fi

datetime=$(date '+%d-%m-%Y_%H-%M-%S');
log_file=$(dirname ${output_file})/sample_${datetime}.log

# 1: select the directories to extract the lines from from
number_dirs=$(echo ${data_dirs} | wc -w)
number_lines_dir=$(echo "${sample_size}/${number_dirs}" | bc )
# The pipe command is necessary to find and shuffle in the case of huge number of files
echo "Balanced sampling..."
echo -n > ${output_file}
for data_dir in ${data_dirs}; do
    echo "Attempting to sample ${number_lines_dir} lines from files in directory: ${data_dir} ($(cat $(find_files "${data_dir}" "${exclude_names}") | wc -l)) files" | tee -a ${log_file}
    if [[ ${debug} == "true" ]]; then
        echo -e "\nFILE: ${data_dir}" >> ${output_file}
    fi

    cat $(find_files "${data_dir}" "${exclude_names}") | \
    shuf -n ${number_lines_dir} --random-source=<(get_seeded_random ${seed}) | \
    sed '/^$/d' | sort | uniq >> ${output_file}
done

sample_lines=$(count_file_lines ${output_file})
echo "Sampled ${sample_lines} total lines into file: $(realpath ${output_file})" | tee -a ${log_file}

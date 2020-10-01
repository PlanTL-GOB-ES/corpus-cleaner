#!/bin/bash
# Small script to perform a balanced random sampling from multiple corpus
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

data_dirs=${data_dirs}
exclude_names=${exclude_names}
sample_size=${sample_size}
number_files=${number_files}
output_file=${output_file}
check_min_number_lines=${check_min_number_lines:-false}
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
if [[ ${number_files} -lt ${number_dirs} ]]; then
    echo "Set number_files to a larger number than number_dirs"
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
log_file=${SCRIPT_DIR}/sample_${datetime}.log

# 1: select the files to extract from
number_dirs=$(echo ${data_dirs} | wc -w)
number_files_dir=$(echo "${number_files}/${number_dirs}" | bc )
# The pipe command is necessary to find and shuffle in the case of huge number of files
for data_dir in ${data_dirs}; do
    echo "Attempting to sample ${number_files_dir} files from directory: ${data_dir} ($(find_files "${data_dir}" "${exclude_names}" | wc -l)) files" | tee -a ${log_file}
    files_sample+=" "
    files_sample+=$(find_files "${data_dir}" "${exclude_names}" | \
        shuf -n ${number_files_dir} --random-source=<(get_seeded_random ${seed}))
done
number_files_sample=$(echo ${files_sample} | wc -w)
total_lines=$(cat ${files_sample} | sed '/^$/d' | wc -l)
echo -e "Sampled ${number_files_sample} files with total number of lines: ${total_lines}" | tee -a ${log_file}

# 2: Sample number_lines_sample from each files
number_lines_sample=$(echo "${sample_size}/${number_files_sample}" | bc )
# Optionally, check if all files have the minimum number of lines
if [[ ${check_min_number_lines} == "true" ]]; then
    min_lines_number=$(wc -l ${files_sample} | grep -oP "^\s*[0-9]*" | sort | head -n 1)
    echo "minimum number of lines: ${min_lines_number}" | tee -a ${log_file}
    if [[ ${number_lines_sample} -gt ${min_lines_number} ]]; then
       echo "Number of samples lines per files greater than minimum number of lines available." \
            "Set sample_size argument to smaller value"
       exit 0
    fi
fi

echo "Balanced sampling..."
echo -n > ${output_file}
for file in ${files_sample}; do
    echo "Attempting to sample ${number_lines_sample} lines from file: ${file} ($(count_file_lines ${file}) lines)" | tee -a ${log_file}
    if [[ ${debug} == "true" ]]; then
        echo -e "\nFILE: ${file}" >> ${output_file}
    fi
    random_lines_sample ${file} ${sample_size} ${number_lines_sample} ${seed} >> ${output_file}

done

if [[ ${debug} != "true" ]]; then
    echo "Removing duplicates from the final sample" | tee -a ${log_file}
    sort -u ${output_file} -o ${output_file}
fi
sample_lines=$(count_file_lines ${output_file})
echo "Sampled ${sample_lines} total lines into file: $(realpath ${output_file})" | tee -a ${log_file}

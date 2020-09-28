#!/bin/bash
# Small script to perform a balanced random sampling from multiple corpus
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

data_dirs=${data_dirs}
exclude_names=${exclude_names}
sample_size=${sample_size}
number_files=${number_files}
output_file=${output_file}
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
    data_dirs=$1
    exclude_names=$2

    for data_dir in "${data_dirs}"; do
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
    done
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
if [[ -z "${exclude_names}" ]]; then
  exclude_names=false
fi

if [[ -z "${sample_size}" ]]; then
  sample_size=1000
fi

if [[ -z "${output_file}" ]]; then
  output_file=${SCRIPT_DIR}/sample.${sample_size}.txt
fi



total_number_files=$(find_files "${data_dirs}" "${exclude_names}" | wc -l)
if [[ -z "${number_files}" ]]; then
  number_files=${total_number_files}
fi

# 1: select the files to extract from
files=$(find_files "${data_dirs}" "${exclude_names}")
files_sample=$(random_files_sample "${files}" ${number_files} ${seed})
echo -e "Selected ${number_files} files:\n${files_sample}"

# 2: count the total number of lines, the minimum number of lines and the number of lines to extract per files
total_lines=$(cat ${files_sample} | sed '/^$/d' | wc -l)
min_lines_number=$(wc -l ${files_sample} | grep -oP "^\s*[0-9]*" | sort | head -n 1)
number_lines_sample=$(echo "${sample_size}/${number_files}" | bc )
echo "number lines sample: ${number_lines_sample}"
echo "minimum number of lines: ${min_lines_number}"
if [[ ${number_lines_sample} -gt ${min_lines_number} ]]; then
   echo "Number of samples lines per files greater than minimum number of lines available."
        "Set sample_size argument to smaller value"
   exit 0
fi
echo "Total number of lines: ${total_lines}"

# 3: Sample number_lines_sample from each files
echo "Balanced sampling..."
echo -n > ${output_file}

for file in ${files_sample}; do
    echo "Sampling lines per file: ${file} (${number_lines_sample})"
    random_lines_sample ${file} ${sample_size} ${number_lines_sample} ${seed} >> ${output_file}
done

echo "Removing duplicates from the final sample"
sort -u ${output_file} -o ${output_file}
sample_lines=$(count_file_lines ${output_file})
echo "Sampled ${sample_lines} total lines into file: $(realpath ${output_file})"
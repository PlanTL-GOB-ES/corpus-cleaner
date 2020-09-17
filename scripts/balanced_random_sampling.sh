#!/bin/bash
# Small script to perform a balanced random sampling from multiple corpus
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

data_dir=${data_dir}
exclude_names=${exclude_names}
sample_size=${sample_size}
number_files=${number_files}
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

# handle arguments values
total_number_files=$(ls ${data_dir} | wc -l)
if [[ -z "${number_files}" ]]; then
  number_files=${total_number_files}
fi

if [[ -z "${exclude_names}" ]]; then
  exclude_names=false
fi

# Generates random seed for shuffling
get_seeded_random()
{
    seed=$1
    openssl enc -aes-256-ctr -pass pass:"${seed}" -nosalt \
      </dev/zero 2>/dev/null
}

function random_files_sample(){
    data_dir=$1
    number_files=$2
    exclude_names=$3
    seed=$4

    if [[ ${exclude_names} == "false" ]]; then
        find ${data_dir} -type f | \
         shuf -n ${number_files} --random-source=<(get_seeded_random ${seed})
    else
        find ${data_dir} -type f -not -name "*${exclude_names}*" | \
          shuf -n ${number_files} --random-source=<(get_seeded_random ${seed})
    fi
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

# 1: select the files to extract from
files=$(random_files_sample ${data_dir} ${number_files} ${exclude_names})
echo "Selected ${number_files} files"
echo "${files}"

# 2: count the total number of lines, the minimum number of lines and the number of lines to extract per files
total_lines=$(cat ${files} | sed '/^$/d' | wc -l)
min_lines_number=$(wc -l ${files} | grep -o "[0-9]*" | sort | head -n 1)
number_lines_sample=$(echo "${sample_size}/${number_files}" | bc )
echo "number lines sample ${number_lines_sample}"
if [[ ${number_lines_sample} -gt ${min_lines_number} ]]; then
   echo "Number of samples lines per files greater than minimum number of lines available."
        "Set sample_size argument to smaller value"
   exit 0
fi
echo "Total number of lines: ${total_lines}"

# 3: Sample number_lines_sample from each files
echo "Balanced sampling..."
output_file=$(basename ${data_dir})_sample
echo -n > ${output_file}

for file in ${files}; do
    echo "Sampling lines per file: ${file} (${number_lines_sample})"
    random_lines_sample ${file} ${sample_size} ${number_lines_sample} ${seed} >> ${output_file}
done

echo "Removing duplicates from the final sample"
sort -u ${output_file} -o ${output_file}
sample_lines=$(count_file_lines ${output_file})
echo "Sampled ${sample_lines} total lines into file: $(realpath ${output_file})"
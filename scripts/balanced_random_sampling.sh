#!/bin/bash
# Small script to perform a balanced random sampling from multiple corpus
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

data_dir=${data_dir}
exclude_names=${exclude_names}
sample_size=${sample_size}
output_dir=${output_dir}
unit=${unit:-files}
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

function random_docs_in_file_sample(){
     file=$1
     number=$2
     seed=$3
     cat ${file} | sed 's/^$/FAIRSEQLM/g' | tr '\n' ' ' | sed 's/FAIRSEQLM/\n/g' | \
     shuf -n ${number} --random-source=<(get_seeded_random ${seed})
 }

function count_file_lines(){
    file=$1
    cat ${file} | sed '/^$/d' | wc -l
}



if [[ -z "${exclude_names}" ]]; then
    exclude_names=false
fi

if [[ -z "${sample_size}" ]]; then
    sample_size=100
fi

if [[ -z "${output_dir}" ]]; then
    output_dir=${SCRIPT_DIR}
else
    mkdir -p ${output_dir}
fi

datetime=$(date '+%d-%m-%Y_%H-%M-%S');
log_file=${output_dir}/sample_${datetime}.log

# 1: select the directories to extract the lines from from
#number_dirs=$(echo ${data_dirs} | wc -w)
#number_units=$(echo "${sample_size}/${number_dirs}" | bc )
# The pipe command is necessary to find and shuffle in the case of huge number of files
if [[ ${unit} == "lines" ]]; then
    echo "Attempting to sample ${sample_size} ${unit} from directory: ${data_dir} ($(cat $(find_files "${data_dir}" "${exclude_names}") | wc -l) lines)" | tee -a ${log_file}
    if [[ ${debug} == "true" ]]; then
        output_file=${output_dir}/lines.${sample_size}.debug.txt
        echo -e "\nFILE: ${data_dir}" >> ${output_file}
    else
        output_file=${output_dir}/lines.${sample_size}.txt
    fi

    echo -n > ${output_file}

    cat $(find_files "${data_dir}" "${exclude_names}") | \
    sed '/^$/d' | sort | uniq | \
    shuf -n ${sample_size} --random-source=<(get_seeded_random ${seed}) \
    >> ${output_file}

    sample_lines=$(count_file_lines ${output_file})
    echo "Sampled ${sample_lines} total ${unit} into file: $(realpath ${output_file})" | tee -a ${log_file}

elif [[ ${unit} == "fairseq-lm" ]]; then
    echo "Attempting to sample ${sample_size} ${unit} lines from directory: ${data_dir} ($(cat $(find_files "${data_dir}" "${exclude_names}") | wc -l) lines)" | tee -a ${log_file}
    if [[ ${debug} == "true" ]]; then
        output_file=${output_dir}/lines.${sample_size}.debug.txt
        echo -e "\nFILE: ${data_dir}" >> ${output_file}
    else
        output_file=${output_dir}/lines.${sample_size}.txt
    fi

    echo -n > ${output_file}

    sample_files=$(find_files "${data_dir}" "${exclude_names}")
    random_docs_in_file_sample "${sample_files}" ${sample_size} ${seed} \
    >> ${output_file}

    sample_lines=$(count_file_lines ${output_file})
    echo "Sampled ${sample_lines} total ${unit} lines into file: $(realpath ${output_file})" | tee -a ${log_file}

elif [[ ${unit} == "files" ]]; then
    echo "Attempting to sample ${sample_size} ${unit} from directory: ${data_dir} ($(echo $(find_files "${data_dir}" "${exclude_names}") | wc -w) files)" | tee -a ${log_file}
    files_sample+=" "
    files_sample+=$(find_files "${data_dir}" "${exclude_names}" | \
        shuf -n ${sample_size} --random-source=<(get_seeded_random ${seed}))

    for file in ${files_sample}; do
        echo ${output_dir}/$(basename ${file})
        cp ${file} ${output_dir}/$(basename ${file})
    done

    sample_files=$(echo ${files_sample} | wc -w)
    echo "Sampled ${sample_files} total ${unit} into dir: $(realpath ${output_dir})" | tee -a ${log_file}

fi

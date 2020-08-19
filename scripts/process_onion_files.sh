#!/usr/bin/env bash
# This script takes as input a tmp folder containing onion files and finishes cleaning and deduplication

# Specify path to tmp folder
TMP=$1

# Concate all files in tmp to one single file
cat $1/*.onion > $1/1_tmp_complete.txt

# Execute onion on the file
onion -m -n 1 -t 0.5 $1/1_tmp_complete.txt > $1/2_onion.txt

# Keep only lines starting with 0 (non-duplicated documents)
egrep '^0' $1/2_onion.txt |

#Substitute every <doc> tag by a new line to separate documents
sed 's/[<][/]doc[>]$/''/' |

# Remove the beginning 0 with the tab
sed 's/^0\t//' > $1/3_clean_nondedup.txt

# Remove duplicated lines appearing more than 5 times but keep empty lines
awk 'FNR==NR {!NF || seen[$0]++; next} seen[$0]<5' $1/3_clean_nondedup.txt $1/3_clean_nondedup.txt > $1/output.txt

#Remove unnecessary files
rm $1/1_tmp_complete.txt
rm $1/2_onion.txt
rm $1/3_clean_nondedup.txt
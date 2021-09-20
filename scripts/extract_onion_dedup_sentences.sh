#!/usr/bin/env bash
# This script takes as input a file in the format output_deduplicate.onion.dedup.sentences

FILE=$1

# Keep only sentences that start with 0 (non-duplicated documents)
egrep '0	' $FILE | \
#Remove 0 plus tab
sed 's/0	//' |
# Remove the tags <doc>, <p>, <\p>
sed '/<doc>/d' | \
sed '/<p>/d' | \
sed '/<\/p>/d' | \
# Substitute the tag <\doc> by new line
sed 's/<\/doc>/\n/' | \

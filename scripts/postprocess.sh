#!/usr/bin/env bash

# Remove zero width space
sed 's/\xe2\x80\x8b//g' filename.txt | \
# Remove space before punctuation
sed -r "s/(\s)([!',.:;])/\2/g" | \
# Remove mention traces
sed -r 's/\s\_[a-zA-Z\_]+//g' | \
# Remove duplicate lines but keep order and empty new lines
awk '!NF || !seen[$0]++' | \
#Remove http and https remainders
sed -r 's/https?:\/\/(\w|\.|\-|\/)*//g' | \
# Remove sentences containing the word 'cookies'
grep -v "cookies"

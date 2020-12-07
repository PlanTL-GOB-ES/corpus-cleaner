#!/usr/bin/env bash

"Filter sentences without any ASCII letter, and single-sentence documents with less than 5 tokens"

INPUT=corpus.txt
OUTPUT=corpus2.txt

sed -E -e '/[a-zA-Z]|^\s*$/!d' $INPUT |  awk -vRS= 'NF<5 && $0 !~ /\n/ {next} {print; print "\n"}' > $OUTPUT

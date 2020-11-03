#!/usr/bin/env bash

THRESHOLD=3
INPUT="../test/test.dedup.txt"
OUTPUT="../test/test.dedup.out"

gawk "{seen[\$0]++; {if (seen[\$0] <= $THRESHOLD) {print}}}" $INPUT > $OUTPUT
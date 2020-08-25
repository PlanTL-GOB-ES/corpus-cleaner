#!/usr/bin/env bash
# This script takes as input a file in the format output.txt
# It fixes spaces between apostrophes in Catalan

FILE=$1

sed "s/\([LlDdSsMmNn]\)' \([AaÀàEeÈèÉéIiÍíOoÒòÓóUuÚúHh1]\)/\1'\2/g" output.txt |
sed "s/\([LlDdSsMmNn]\) '\([AaÀàEeÈèÉéIiÍíOoÒòÓóUuÚúHh1]\)/\1'\2/g" |
sed "s/\([AaÀàEeÈèÉéIiÍíOoÒòÓóUuÚú]\)' \([lsmn]\)/\1'\2/g" |
sed "s/\([AÀaàEeÈèÉéIiÍíOoÒòÓóUuÚú]\) '\([lsmn]\)/\1'\2/g"
#!/usr/bin/env bash
# https://stackoverflow.com/questions/18204904/fast-way-of-finding-lines-in-one-file-that-are-not-in-another
# This script finds lines from one file (file2) that are not in the other (file1)
# file1 is the big file (ex. colossal corpus)
# file2 is the shorter file of which you want to find lines in the big file (ex. open subtitles catalan)

diff file1 file2 | grep '^>' | sed 's/^>\ //'
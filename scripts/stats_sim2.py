#!/usr/bin/env python3
# From: https://github.com/pytorch/fairseq/blob/master/scripts/count_docs.py
# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
"""
Count the number of documents and average number of lines and tokens per
document in a large file. Documents should be separated by a single empty line.
"""

import argparse
import gzip
import sys
import os
import math

import numpy as np
import logging
#from utils import config_logging, timer, get_output_root_path


#@timer
def stats():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--gzip", action="store_true")
    #parser.add_argument("--output-root", help="Root of output (default: output/)", default=get_output_root_path())
    args = parser.parse_args()

    def gopen():
        if args.gzip:
            return gzip.open(args.input, "r")
        else:
            return open(args.input, "r", encoding="utf-8")

    num_lines = []
    num_toks = []
    num_chars = []
    num_chars_sentence = []
    doc_starts = [0]
    with gopen() as h:
        num_docs = 1
        num_lines_in_doc = 0
        num_toks_in_doc = 0
        num_chars_in_doc = 0
        num_lines_in_sentence = []
        for i, line in enumerate(h):
            if len(line.strip()) == 0:  # empty line indicates new document
                num_docs += 1
                num_lines.append(num_lines_in_doc)
                num_toks.append(num_toks_in_doc)
                num_chars.append(num_chars_in_doc)
                num_chars_sentence.append(num_lines_in_sentence)
                num_lines_in_doc = 0
                num_toks_in_doc = 0
                num_chars_in_doc = 0
                num_lines_in_sentence = []
                doc_starts.append(i+1)
            else:
                num_lines_in_doc += 1
                num_toks_in_doc += len(line.rstrip().split())
                num_chars_in_doc += len(line)
                num_lines_in_sentence.append(len(line))
            if (i+1) % 1000000 == 0:
                print(f'Processed  {i+1} lines', flush=True)# , file=sys.stderr, end="", flush=True)
            # elif (i+1) % 100000 == 0:
            #    print(".", file=sys.stderr, end="", flush=True)
        print(file=sys.stderr, flush=True)
    if num_toks_in_doc > 0:
        num_lines_in_doc += 1
        num_toks_in_doc += len(line.rstrip().split())
        num_chars_in_doc += len(line)
        num_lines_in_sentence.append(len(line))

    print("found {} docs".format(num_docs))
    print("total: {} tokens".format(np.sum(num_toks)))
    print("total: {} lines".format(np.sum(num_lines)))
    print("average num lines per doc: {}".format(np.mean(num_lines)))
    print("average num toks per doc: {}".format(np.mean(num_toks)))
    print("average num chars per doc: {}".format(np.mean(num_chars)))
    print("std num lines per doc: {}".format(np.std(num_lines)))
    print("std num toks per doc: {}".format(np.std(num_toks)))
    print("std num chars per doc: {}".format(np.std(num_chars)))

    c = 0
    c1k = 0
    c10k = 0
    min_ = math.inf
    max_ = -1
    for e in num_lines:
        if e > max_:
            max_ = e
        if e < min_:
            min_ = e
        if e > 100:
            c += 1
        if e > 1000:
            c1k += 1
        if e > 10000:
            c10k += 1

    print("min num lines in a doc: " + str(min_))
    print("max num lines in a doc: " + str(max_))
    print("num docs with more than 100 lines: " + str(c))
    print("num docs with more than 1,000 lines: " + str(c1k))
    print("num docs with more than 10,000 lines: " + str(c10k))
    
    min_lines = 6
    print(f"Suspiciously low char per sentence std (top 10, with min {min_lines} lines)")
    num_chars_sentence = list(map(np.std, num_chars_sentence))
    sorted_idx = np.argsort(num_chars_sentence)
    count = 0
    for e in sorted_idx:
        if num_lines[e] >= min_lines:
            print("std chars per sentence: " + str(num_chars_sentence[e]) + ", doc offset (Starting by): " +
                  str(doc_starts[e]))
            count += 1
        if count > 10:
            break


if __name__ == "__main__":
    stats()

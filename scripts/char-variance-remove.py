import argparse
import gzip
import sys
import os
import math

import numpy as np
import logging
import ftfy

def stats():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("--gzip", action="store_true")
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
    doc_ends = []
    bad_docs = []
    with gopen() as h:
        num_docs = 1
        num_lines_in_doc = 0
        num_toks_in_doc = 0
        num_chars_in_doc = 0
        num_chars_in_sentence = []
        lines_doc = []
        for i, line in enumerate(h):
            if len(line.strip()) == 0:  # empty line indicates new document
                num_docs += 1
                std_char = np.std(num_chars_in_sentence)
                if len(lines_doc) > 4 and std_char < 1:
                    bad_docs.append(i)
                    print('NOT SAVING:\n', ''.join(lines_doc), flush=True, file=sys.stderr)
                else:
                    print(ftfy.fix_text(''.join(lines_doc), normalization='NFKC'), flush=True)
                lines_doc = []
                num_lines.append(num_lines_in_doc)
                num_toks.append(num_toks_in_doc)
                num_chars.append(num_chars_in_doc)
                num_chars_sentence.append(num_chars_in_sentence)
                num_lines_in_doc = 0
                num_toks_in_doc = 0
                num_chars_in_doc = 0
                num_chars_in_sentence = []



                doc_ends.append(i-1)
                doc_starts.append(i+1)
            else:
                lines_doc.append(line)
                num_lines_in_doc += 1
                num_toks_in_doc += len(line.rstrip().split())
                num_chars_in_doc += len(line)
                num_chars_in_sentence.append(len(line))
            if (i+1) % 1000 == 0:
                print(f'Processed  {i+1} lines', flush=True, file=sys.stderr)# , file=sys.stderr, end="", flush=True)
            # elif (i+1) % 100000 == 0:
            #    print(".", file=sys.stderr, end="", flush=True)
        #print(file=sys.stderr, flush=True)
    if num_toks_in_doc > 0:
        num_lines_in_doc += 1
        num_toks_in_doc += len(line.rstrip().split())
        num_chars_in_doc += len(line)
        num_chars_in_sentence.append(len(line))
        doc_ends.append(i - 1)
        std_char = np.std(num_chars_sentence)
        if len(num_chars_sentence) > 4 and std_char < 1:
            print('NOT SAVING:\n', ''.join(lines_doc), flush=True, file=sys.stderr)
        else:
            print(ftfy.fix_text(''.join(lines_doc), normalization='NFKC'), flush=True)

    print("found {} docs".format(num_docs), flush=True, file=sys.stderr)
    print("total: {} tokens".format(np.sum(num_toks)), flush=True, file=sys.stderr)
    print("total: {} lines".format(np.sum(num_lines)), flush=True, file=sys.stderr)
    print("average num lines per doc: {}".format(np.mean(num_lines)), flush=True, file=sys.stderr)
    print("average num toks per doc: {}".format(np.mean(num_toks)), flush=True, file=sys.stderr)
    print("average num chars per doc: {}".format(np.mean(num_chars)), flush=True, file=sys.stderr)
    print("std num lines per doc: {}".format(np.std(num_lines)), flush=True, file=sys.stderr)
    print("std num toks per doc: {}".format(np.std(num_toks)), flush=True, file=sys.stderr)
    print("std num chars per doc: {}".format(np.std(num_chars)), flush=True, file=sys.stderr)

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

    print("min num lines in a doc: " + str(min_), flush=True, file=sys.stderr)
    print("max num lines in a doc: " + str(max_), flush=True, file=sys.stderr)
    print("num docs with more than 100 lines: " + str(c), flush=True, file=sys.stderr)
    print("num docs with more than 1,000 lines: " + str(c1k), flush=True, file=sys.stderr)
    print("num docs with more than 10,000 lines: " + str(c10k), flush=True, file=sys.stderr)

    min_lines = 6
    print(f"Suspiciously low char per sentence std (top 10, with min {min_lines} lines)", flush=True, file=sys.stderr)
    num_chars_sentence = list(map(np.std, num_chars_sentence))
    sorted_idx = np.argsort(num_chars_sentence)
    count = 0
    with open('suspicious.txt', 'w') as f:
        for e in sorted_idx:
            if num_lines[e] >= min_lines:
                print("std chars per sentence: " + str(num_chars_sentence[e]) + ", doc offset (Starting by): " +
                      str(doc_starts[e]), flush=True, file=sys.stderr)
                count += 1
            if count > 10:
                break


if __name__ == "__main__":
    stats()

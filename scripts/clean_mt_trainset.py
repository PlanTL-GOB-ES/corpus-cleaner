#!/usr/bin/env python
# Author: Ona de Gibert
# This file is used to removes sentences in testsets and validation sets from parallel training sets
# It expects two parallel train files and one or more test sets
# It writes the output in a folder called "clean"
# Usage:
# python3 clean_train.py --train tokenized/train.ca-oc.ca tokenized/train.ca-oc.oc --test tokenized/valid.ca tokenized/test.ca
import argparse
import ntpath

def read_files(train,test):
    read_train_list = [] 
    read_test_list = []
    for file in train:
        read_train = open(file, 'r').read().splitlines()
        read_train_list.append(read_train)
    for file in test:
        read_test = open(file, 'r').read().splitlines()
        read_test_list.extend(read_test)
    return read_train_list, set(read_test_list)

def clean_train(train, test):
    index = 0
    common_lines_indeces = []
    for line in train[0]:
        if line in test: # if a line in test is contained in the train files, remove it
            common_lines_indeces.append(index)
        index += 1
    for file in train:
        for index in sorted(common_lines_indeces, reverse=True):
            del file[index]
    return(train)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", nargs="+", default=['-'],
                        help="expects two parallel train files paths, first one same language as test")
    parser.add_argument("--test", nargs="+", default=['-'],
                        help="test files paths")
    
    args = parser.parse_args()
    train_filenames = [ntpath.basename(file) for file in args.train]

    train, test = read_files(args.train, args.test)
    train_raw_lines = len(train[0])
    train_clean = clean_train(train, test)
    train_clean_lines = len(train[0])
    for index in range(2):
        out = open("clean/"+train_filenames[index],'w')
        out.write('\n'.join(train_clean[index]))

    removed_lines = train_raw_lines - train_clean_lines
    print("Removed {} lines for {}".format(removed_lines,train_filenames[0]))


if __name__ == "__main__":
    main()


# Removed 36 lines for train.ca-oc.ca
# Removed 306 lines for train.ca-ro.ca
# Removed 466 lines for train.ca-it.ca

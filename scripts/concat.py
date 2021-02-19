"""
Concatenates the given subcorpora keeping both document and sentence boundaries
Author: ona.degibert@bsc.es
Usage: python scripts/concat.py -d doc_level_corpus1.txt doc_level_corpus2.txt -s sen_level_corpus.txt -o output_concatenated_corpus.txt
"""

import argparse
import re


def parse_arguments():
    """Read command line parameters."""
    parser = argparse.ArgumentParser(description="Script to concatenate given subcorpora keeping boundaries")
    parser.add_argument('-d', '--doc', nargs='+',
                        help="Corpus at document level")
    parser.add_argument('-s', '--sen', nargs='+',
                        help="Corpus at sentence level")
    parser.add_argument('-o', '--out',
                        help="Output path of concatenated file")
    args = parser.parse_args()
    return args.doc, args.sen, args.out

def process_corpora(corpora_list, level):
    """Process corpora at both document and sentence level"""
    corpora_list_processed = []
    for file in corpora_list:
        with open(file) as fn:
            file_processed = fn.read().splitlines()
            if level == "doc":
                file_processed.append('')
            elif level == "sen":
                file_processed = [re.sub('$','\n',line) for line in file_processed]
            print("Processed",file)
            corpora_list_processed.extend(file_processed)
    return corpora_list_processed

def write_file(corpus_processed,output):
    """Concatenate all corpora and write it to output file"""
    with open(output,'a') as ouput_file:
        for document in corpus_processed: # generator
            ouput_file.write(document+'\n')

if __name__ == "__main__":
    # Obtain arguments
    doc_level, sen_level, output = parse_arguments()
    print(len(doc_level), "corpora at document level.")
    doc_level_processed = process_corpora(doc_level,"doc") # return generator
    print(len(sen_level), "corpora at sentence level.")
    sen_level_processed = process_corpora(sen_level,"sen")
    write_file(doc_level_processed, output)
    write_file(sen_level_processed, output)

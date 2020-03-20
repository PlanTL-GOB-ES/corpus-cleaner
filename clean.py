import argparse
import logging
import time
import os
import json
from cleaner import Cleaner
from components.data_parser import DataParser
from components.document_filter import DocumentFilter
from components.document_organizer import DocumentOrganizer
from components.encoding_fixer import EncodingFixer
from components.normalizer import Normalizer
from components.pre_filterer import PreFilterer
from components.sentence_filter import SentenceFilter
from components.sentence_splitter import SentenceSplitter


def clean(args: argparse.Namespace, output_dir: str, log: logging):
    logging.info(args)
    cleaner = Cleaner(args, output_dir, log)
    cleaner.clean()


def get_output_dir(name: str) -> str:
    timestamp = time.strftime("%Y-%m-%d-%H%M")
    output_dir = os.path.join('output', f'{name}-{timestamp}')
    return output_dir


def check_args(args: argparse.Namespace):
    # TODO: Check arguments (eg. directories exists, valid options...)
    pass


def main():
    parser = argparse.ArgumentParser(description='Clean raw text data.')
    parser.add_argument('name', type=str, help='A name to identify the run')
    parser.add_argument('--input-path', type=str, help='Input data directory')
    parser.add_argument('--input-format', type=str, help='Input data format')
    parser.add_argument('--output-format', type=str, help='Output data format')

    DataParser.add_args(parser)
    DocumentFilter.add_args(parser)
    DocumentOrganizer.add_args(parser)
    EncodingFixer.add_args(parser)
    Normalizer.add_args(parser)
    PreFilterer.add_args(parser)
    SentenceFilter.add_args(parser)
    SentenceSplitter.add_args(parser)

    args = parser.parse_args()

    check_args(args)

    output_dir = get_output_dir(args.name)

    logging.basicConfig(filename=os.path.join(output_dir, 'clean.log'), level=logging.INFO)
    logging.getLogger('').addHandler(logging.StreamHandler())

    with open(os.path.join(output_dir, 'args.json'), 'w') as f:
        json.dump(args.__dict__, f, indent=2)

    logging.info(output_dir)

    clean(args, output_dir, logging)


if __name__ == '__main__':
    main()

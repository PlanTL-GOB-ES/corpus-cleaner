import argparse
import logging
import time
import os
import json
from cleaner import Cleaner
from components.data_parser import DataParser, DataParserFactory
from components.document_filter import DocumentFilter
from components.document_organizer import DocumentOrganizer
from components.encoding_fixer import EncodingFixer
from components.normalizer import Normalizer
from components.output_formatter import OutputFormatter, OutputFormatterFactory
from components.pre_filterer import PreFilterer
from components.sentence_filter import SentenceFilter
from components.sentence_splitter_component import SentenceSplitterComponent
import os


def clean(args: argparse.Namespace, output_dir: str, log: logging):
    logging.info(args)
    cleaner = Cleaner(args, output_dir, log)
    cleaner.clean()


def get_output_dir(name: str, output_path: str) -> str:
    timestamp = time.strftime("%Y-%m-%d-%H%M")
    output_dir = os.path.join(output_path, f'{name}-{timestamp}')
    return output_dir


def check_args(args: argparse.Namespace):
    for path in [args.input_path, args.output_path]:
        if path is None or not os.path.exists(path):
            raise FileNotFoundError(path)
        if not os.path.isdir(args.input_path):
            raise NotADirectoryError(path)
    if args.input_path == args.output_path:
        raise Exception('Input and output paths should be different')
    if args.input_format not in DataParserFactory.VALID_INPUT_FORMATS:
        raise Exception('Invalid input format')
    if args.output_format not in OutputFormatterFactory.VALID_OUTPUT_FORMATS:
        raise Exception('Invalid output format')
    Cleaner.check_args(args)
    DataParser.check_args(args)
    DocumentFilter.check_args(args)
    DocumentOrganizer.check_args(args)
    EncodingFixer.check_args(args)
    Normalizer.check_args(args)
    OutputFormatter.check_args(args)
    PreFilterer.check_args(args)
    SentenceFilter.check_args(args)
    SentenceSplitterComponent.check_args(args)


def main():
    parser = argparse.ArgumentParser(description='Clean raw text data.')
    parser.add_argument('name', type=str, help='A name to identify the run')
    parser.add_argument('--input-path', type=str, help='Input data directory')
    parser.add_argument('--output-path', type=str, help='Output data directory', default='output')
    parser.add_argument('--input-format', type=str, help='Input data format')
    parser.add_argument('--output-format', type=str, help='Output data format')

    Cleaner.add_args(parser)
    DataParser.add_args(parser)
    DocumentFilter.add_args(parser)
    DocumentOrganizer.add_args(parser)
    EncodingFixer.add_args(parser)
    Normalizer.add_args(parser)
    OutputFormatter.add_args(parser)
    PreFilterer.add_args(parser)
    SentenceFilter.add_args(parser)
    SentenceSplitterComponent.add_args(parser)

    args = parser.parse_args()

    check_args(args)

    output_dir = get_output_dir(args.name, args.output_path)

    os.makedirs(output_dir)

    logging.basicConfig(filename=os.path.join(output_dir, 'clean.log'), level=logging.INFO)
    logging.getLogger('').addHandler(logging.StreamHandler())
    # git rev-parse HEAD
    with open(os.path.join(output_dir, 'args.json'), 'w') as f:
        json.dump(args.__dict__, f, indent=2)

    logging.info(output_dir)

    clean(args, output_dir, logging)


if __name__ == '__main__':
    main()

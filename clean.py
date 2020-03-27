import argparse
import logging
import time
import json
from corpus_cleaner.cleaner import Cleaner
import os
import corpus_cleaner
import sys


def clean(args: argparse.Namespace, logger: logging.Logger):
    logger.info(args)
    cleaner = Cleaner(args, logger)
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
    (valid_input_formats, valid_output_formats) = Cleaner.get_valid_input_output_formats()
    if args.input_path == args.output_path:
        raise Exception('Input and output paths should be different')
    if args.input_format not in valid_input_formats:
        raise Exception('Invalid input format')
    if args.output_format not in valid_output_formats:
        raise Exception('Invalid output format')
    Cleaner.check_args(args)
    for component in Cleaner.get_components_classes():
        component.check_args(args)


def init_logger(filename_path: str) -> logging.Logger:
    logging.basicConfig(filename=filename_path, level=logging.INFO)
    logger = logging.getLogger(__name__)
    #logger.addHandler(logging.StreamHandler())

    h = logging.StreamHandler(sys.stderr)
    h.flush = sys.stderr.flush
    logger.addHandler(h)

    return logger


def main():
    parser = argparse.ArgumentParser(description='Clean raw text data.')
    parser.add_argument('name', type=str, help='A name to identify the run')
    parser.add_argument('--input-path', type=str, help='Input data directory')
    parser.add_argument('--output-path', type=str, help='Output data directory', default='output')
    parser.add_argument('--input-format', type=str, help='Input data format')
    parser.add_argument('--output-format', type=str, help='Output data format')

    Cleaner.add_args(parser)
    for component in Cleaner.get_components_classes():
        component.add_args(parser)

    args = parser.parse_args()

    check_args(args)

    args.corpus_cleaner_version = corpus_cleaner.__version__
    output_dir = get_output_dir(args.name, args.output_path)
    args.output_path = output_dir

    os.makedirs(output_dir)

    logger = init_logger(os.path.join(output_dir, 'clean.log'))

    with open(os.path.join(output_dir, 'args.json'), 'w') as f:
        json.dump(args.__dict__, f, indent=2)

    logging.info(output_dir)

    clean(args, logger)


if __name__ == '__main__':
    main()

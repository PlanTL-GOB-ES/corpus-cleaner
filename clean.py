import argparse
import logging
import time
import json
from corpus_cleaner.cleaner import Cleaner
import os
import corpus_cleaner
import sys
import datetime
from corpus_cleaner.checkpoint import Checkpoint


def clean(args: argparse.Namespace, logger: logging.Logger, checkpoint: Checkpoint):
    logger.info(args)
    t0 = datetime.datetime.now().timestamp()
    cleaner = Cleaner(args, logger, checkpoint)
    cleaner.clean()
    checkpoint.declare_as_cleaned()
    t1 = datetime.datetime.now().timestamp()
    logger.info(f'Elapsed {t1-t0}s')


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


def main():
    parser = argparse.ArgumentParser(description='Clean raw text data.')
    parser.add_argument('name', type=str, help='A name to identify the run')
    parser.add_argument('--input-path', type=str, help='Input data directory')
    parser.add_argument('--output-path', type=str, help='Output data directory', default='output')
    parser.add_argument('--input-format', type=str, help='Input data format')
    parser.add_argument('--output-format', type=str, help='Output data format')
    parser.add_argument('--checkpoint-backend', choices=['shelve', 'file'], default='shelve',
                        help='Shelve is more convenient but file is more robust. For distributed executions,'
                             'we recommend file.')

    Cleaner.add_args(parser)
    for component in Cleaner.get_components_classes():
        component.add_args(parser)

    args = parser.parse_args()

    check_args(args)

    args.corpus_cleaner_version = corpus_cleaner.__version__
    output_dir = get_output_dir(args.name, args.output_path)
    args.output_path = output_dir

    if os.path.exists(output_dir):
        raise OSError(f'{output_dir} already exists!')
    os.makedirs(output_dir, exist_ok=True)

    checkpoint = Checkpoint(output_dir, args)
    logger = checkpoint.logger

    logging.info(output_dir)

    clean(args, logger, checkpoint)

    print()


if __name__ == '__main__':
    main()

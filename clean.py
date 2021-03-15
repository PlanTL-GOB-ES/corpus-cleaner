import argparse
import logging
import time
from corpus_cleaner.cleaner import Cleaner
import os
import corpus_cleaner
import datetime
from corpus_cleaner.checkpoint import Checkpoint
from corpus_cleaner.cleaner import CleanerConfig
from simple_parsing import ArgumentParser


def clean(config: CleanerConfig, logger: logging.Logger, checkpoint: Checkpoint):
    logger.info(config)
    t0 = datetime.datetime.now().timestamp()
    cleaner = Cleaner(config, logger, checkpoint)
    cleaner.clean()
    checkpoint.declare_as_cleaned()
    t1 = datetime.datetime.now().timestamp()
    logger.info(f'Elapsed {t1 - t0}s')


def get_output_dir(name: str, output_path: str) -> str:
    timestamp = time.strftime("%Y-%m-%d-%H%M")
    output_dir = os.path.join(output_path, f'{name}-{timestamp}')
    return output_dir


# TODO: check args with __post_init_() method in each Config class
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
    parser = ArgumentParser(description='Clean raw text data.')

    parser.add_argument(CleanerConfig, dest='config')

    args = parser.parse_args()

    # check_args(args)

    args.corpus_cleaner_version = corpus_cleaner.__version__
    output_dir = get_output_dir(args.config.global_config.name, args.config.global_config.output_path)
    args.output_path = output_dir

    if os.path.exists(output_dir):
        raise OSError(f'{output_dir} already exists!')
    os.makedirs(output_dir, exist_ok=True)

    checkpoint = Checkpoint(args.config.global_config.output_path, args)
    logger = checkpoint.logger

    logging.info(output_dir)

    clean(args.config, logger, checkpoint)

    print()


if __name__ == '__main__':
    main()

import argparse
import logging
import time
import os
import json
from cleaner import Cleaner


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
    # TODO: Add required options

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

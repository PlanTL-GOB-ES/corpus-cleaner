import argparse
from corpus_cleaner.checkpoint import Checkpoint
from clean import clean


def resume(output_path: str):
    checkpoint = Checkpoint(output_path)
    args = checkpoint.args
    logger = checkpoint.logger
    logger.info(f'Restoring clean from {output_path}')
    clean(args, logger, checkpoint)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Resume cleaning.')
    parser.add_argument('output_path', type=str, help='Output path of the previous execution.')
    resume_args = parser.parse_args()
    resume(resume_args.output_path)

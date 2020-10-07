import os
import json
import argparse
import logging
import sys
from typing import Optional


class GlobalCheckpoint:
    def __init__(self, output_path: str, args: Optional[argparse.Namespace]):
        self.output_path = output_path
        checkpoint_path = os.path.join(output_path, 'checkpoint.json')
        if os.path.exists(checkpoint_path):
            assert args is None
            with open(os.path.join(output_path, 'args.json'), 'w') as f:
                self.args = json.loads(f.read())
            self.resume = True
            self.checkpoint_fd = open(checkpoint_path, 'r+')
            self.state = json.loads(self.checkpoint_fd.read())
        else:
            assert args is not None
            self.args = args
            self.resume = False
            self.checkpoint_fd = open(checkpoint_path, 'w')

    def init(self):
        def init_logger(filename_path: str) -> logging.Logger:
            logging.basicConfig(filename=filename_path, level=logging.INFO)
            logger = logging.getLogger(__name__)
            h = logging.StreamHandler(sys.stderr)
            h.flush = sys.stderr.flush
            logger.addHandler(h)
            return logger
        if not args.only_reduce:
            logger = init_logger(os.path.join(output_dir, 'clean.log'))
            with open(os.path.join(output_dir, 'args.json'), 'w') as f:
                json.dump(args.__dict__, f, indent=2)
        else:
            logger = init_logger(os.path.join(output_dir, 'clean_reduce.log'))
            with open(os.path.join(output_dir, 'args_reduce.json'), 'w') as f:
                json.dump(args.__dict__, f, indent=2)
        return logger

    def save_args(self, args: argparse.Namespace, filename_path: str):
        if not args.only_reduce:
            logger = init_logger(os.path.join(output_dir, 'clean.log'))
            with open(os.path.join(output_dir, 'args.json'), 'w') as f:
                json.dump(args.__dict__, f, indent=2)
        else:
            logger = init_logger(os.path.join(output_dir, 'clean_reduce.log'))
            with open(os.path.join(output_dir, 'args_reduce.json'), 'w') as f:
                json.dump(args.__dict__, f, indent=2)

    def restore_args(self) -> argparse.Namespace:
        pass

    def restore_logging(self):
        pass

    def check_file_done(self, filename: str) -> bool:
        pass

    def check_doc_done(self, filename: str, id_or_url: str) -> bool:
        pass

    def register_file_done(self, filename: str):
        pass

    def register_doc_done(self, filename: str, id_or_url: str) -> bool:
        pass

    @property
    def done(self) -> bool:
        return self._done


class LocalCheckpoint:
    def __init__(self, process_id):
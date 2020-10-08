import os
import json
import argparse
import logging
import sys
from typing import Optional


class Checkpoint:
    def __init__(self, output_path: str, args: Optional[argparse.Namespace] = None):
        self.output_path = output_path
        checkpoint_path = os.path.join(output_path, 'checkpoint.json')
        if os.path.exists(checkpoint_path):
            assert args is None
            with open(os.path.join(output_path, 'args.json'), 'w') as f:
                self.args = argparse.Namespace(**json.loads(f.read()))
            self.resume = True
            self.checkpoint_fd = open(checkpoint_path, 'r+')
            self.state = json.loads(self.checkpoint_fd.read())
            if not self.args.only_reduce:
                self.logger = self.init_logger(os.path.join(self.output_path, 'clean.log'))
                with open(os.path.join(self.output_path, 'args.json'), 'w') as f:
                    json.dump(self.args.__dict__, f, indent=2)
            else:
                self.logger = self.init_logger(os.path.join(self.output_path, 'clean_reduce.log'))
                with open(os.path.join(self.output_path, 'args_reduce.json'), 'w') as f:
                    json.dump(self.args.__dict__, f, indent=2)
            if self.args.done:
                self.logger.info('Already cleaned!')
        else:
            assert args is not None
            self.args = args
            self.resume = False
            self.args.done = False
            if not self.args.only_reduce:
                self.logger = self.init_logger(os.path.join(self.output_path, 'clean.log'))
                with open(os.path.join(self.output_path, 'args.json'), 'w') as f:
                    json.dump(self.args.__dict__, f, indent=2)
            else:
                self.logger = self.init_logger(os.path.join(self.output_path, 'clean_reduce.log'))
                with open(os.path.join(self.output_path, 'args_reduce.json'), 'w') as f:
                    json.dump(self.args.__dict__, f, indent=2)
            self.checkpoint_fd = open(checkpoint_path, 'w')
        self.done_files_path = os.path.join(self.output_path, 'checkpoint.json')

    @staticmethod
    def init_logger(filename_path: str) -> logging.Logger:
        logging.basicConfig(filename=filename_path, level=logging.INFO)
        logger = logging.getLogger(__name__)
        h = logging.StreamHandler(sys.stderr)
        h.flush = sys.stderr.flush
        logger.addHandler(h)
        return logger

    def declare_as_cleaned(self):
        self.args.done = True
        if not self.args.only_reduce:
            with open(os.path.join(self.output_path, 'args.json'), 'w') as f:
                json.dump(self.args.__dict__, f, indent=2)
        else:
            with open(os.path.join(self.output_path, 'args_reduce.json'), 'w') as f:
                json.dump(self.args.__dict__, f, indent=2)

    def get_done_paths(self):
        with open(self.done_files_path, 'r') as f:
            done_paths = json.loads(f.read())
        return done_paths['done_paths']

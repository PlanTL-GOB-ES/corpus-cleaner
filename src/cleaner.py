from document import Document
from typing import Iterable
import argparse
import logging


class Cleaner:
    def __init__(self, args: argparse.Namespace, output_dir: str, logger: logging):
        self.args = args
        self.output_dir = output_dir
        self.logger = logger
        self.component_names = []
        self.pipeline = []

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--no-component', type=str, help='remove a given component from the pipeline')

    def _create_pipeline(self):
        raise NotImplementedError

    def clean(self) -> Iterable[Document]:
        raise NotImplementedError

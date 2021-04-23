from . import DataParser
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
from typing import Iterable, Tuple
import argparse


class DataParserMapper(CleanerComponent):
    def __init__(self, args: argparse.Namespace, data_parser: DataParser):
        super().__init__(args)
        self.data_parser = data_parser

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        pass

    def __call__(self, path: Tuple[int, str]) -> Iterable[Document]:
        idx, path = path
        return self.data_parser.treat_file(idx, path)


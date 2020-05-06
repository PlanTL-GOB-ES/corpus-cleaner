import argparse
from corpus_cleaner.document import Document
from typing import Optional
from . import CleanerComponent
from .a_data_parser import DataParser
from .i_output_formatter import OutputFormatter
from typing import List


class CleanerComponentReducer(CleanerComponent):

    def __init__(self, args: argparse.Namespace, output_formatter: OutputFormatter, data_parser: DataParser):
        super().__init__(args)
        self.output_formatter = output_formatter
        self.data_parser = data_parser

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def _reduce(self):
        raise NotImplementedError()

    def reduce(self):
        del self.output_formatter
        self._reduce()

    def get_documents(self):
        return self.data_parser.parse()

    def output(self, documents: List[Document]):
        # self.logger.info('Outputting...')
        self.output_formatter.apply(documents)

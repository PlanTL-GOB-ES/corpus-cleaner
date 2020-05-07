import argparse
from corpus_cleaner.document import Document
from typing import Optional
from . import CleanerComponent
from .a_data_parser import DataParser
from .i_output_formatter import OutputFormatterFactory
from .a_data_parser import DataParserFactory
from typing import List
import os


class CleanerComponentReducer(CleanerComponent):

    def __init__(self, args: argparse.Namespace, format_: str, tmp_file: str, final_path: str):
        super().__init__(args)
        self.format = format_
        self.tmp_file = tmp_file
        self.final_path = final_path
        self.data_parser = DataParserFactory.get_parser(args, input_format=self.format)

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def _reduce(self):
        raise NotImplementedError()

    def reduce(self):
        self._reduce()

    def get_documents(self):
        return self.data_parser.parse()

    def output(self, documents: List[Document]):
        # self.logger.info('Outputting...')
        output_formatter = OutputFormatterFactory.get_output_formatter(self.args, self.format, self.tmp_file)
        output_formatter.apply(documents)

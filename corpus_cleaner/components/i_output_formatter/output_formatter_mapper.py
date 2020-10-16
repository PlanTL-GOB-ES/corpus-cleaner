from . import OutputFormatter
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
import argparse
from typing import Iterable
from typing import Tuple, Optional


class OutputFormatterMapper(CleanerComponent):
    def __init__(self, args: argparse.Namespace, output_formatter: OutputFormatter):
        super().__init__(args)
        self.output_formatter = output_formatter

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        pass

    def __call__(self, documents: Iterable[Document]) -> Tuple[int, Optional[Tuple], Optional[str]]:
        self.output_formatter.init_writing()
        filename = None
        for document in documents:
            self.output_formatter._write_document(document)
            filename = document.filename
        self.output_formatter.end_writing()
        return filename


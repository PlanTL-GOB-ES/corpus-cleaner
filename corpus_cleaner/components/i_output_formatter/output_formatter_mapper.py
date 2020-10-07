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
        idx = -1
        id_ = None
        filename = None
        for document in documents:
            self.output_formatter._write_document(document)
            if document.url and document.id:
                id_ = (document.filename, document.id, document.url)
            elif document.id:
                id_ = (document.filename, document.id)
            else:
                id_ = (document.filename,)
            idx = document.idx
            filename = document.filename
        self.output_formatter.end_writing()
        return idx, id_, filename


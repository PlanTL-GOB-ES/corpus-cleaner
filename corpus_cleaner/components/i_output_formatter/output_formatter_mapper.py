from . import OutputFormatter
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
import argparse
from typing import Iterable
from typing import Tuple, Optional
import os


class OutputFormatterMapper(CleanerComponent):
    def __init__(self, args: argparse.Namespace, output_formatter: OutputFormatter,
                 write_checkpoint_path: Optional[str] = None):
        super().__init__(args)
        self.output_formatter = output_formatter
        self.write_checkpoint_path = write_checkpoint_path

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        pass

    def _write_checkpoint(self, e: str):
        with open(os.path.join(self.write_checkpoint_path, e.replace('/', '!')), 'w') as f:
            pass

    def __call__(self, documents: Iterable[Document]) -> Tuple[int, Optional[Tuple], Optional[str]]:
        self.output_formatter.init_writing()
        filename = None
        for document in documents:
            self.output_formatter._write_document(document)
            filename = document.filename
        self.output_formatter.end_writing()

        if self.write_checkpoint_path:
            self._write_checkpoint(filename)

        return filename


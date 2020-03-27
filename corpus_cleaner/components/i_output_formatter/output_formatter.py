from corpus_cleaner.document import Document
from typing import Iterable, Union
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse
import logging
from tqdm import tqdm
from typing import TextIO


class OutputFormatter(CleanerComponent):
    def __init__(self, args: argparse.Namespace, output_path: str = None):
        super().__init__(args)
        self.path = args.output_path if args.output_path is not None else output_path
        self.fd: Union[TextIO, None] = None

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _init_writing(self):
        raise NotImplementedError()

    def _write_document(self, document: Document):
        raise NotImplementedError()

    def _end_writing(self):
        raise NotImplementedError()

    def _output_format(self, documents: Iterable[Document]):
        self._init_writing()
        for document in tqdm(documents):
            self._write_document(document)

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._output_format(documents)

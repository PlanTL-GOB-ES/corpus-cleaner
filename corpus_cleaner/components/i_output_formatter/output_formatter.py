from corpus_cleaner.document import Document
from typing import Iterable, Union
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse
from typing import TextIO
from typing import Optional

SEPARATOR = "|"


class OutputFormatter(CleanerComponent):
    def __init__(self, args: argparse.Namespace, output_path: Optional[str] = None):
        super().__init__(args)
        self.path = output_path if output_path is not None else args.output_path
        self.fd: Union[TextIO, None] = None
        self.separator = SEPARATOR

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
        if self.fd is None:
            self._init_writing()
        for document in documents:
            if document is None:
                continue
            self._write_document(document)
        self._end_writing()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._output_format(documents)

    #def __del__(self):
    #    self._end_writing()

    def init_writing(self):
        self._init_writing()

    def end_writing(self):
        self._end_writing()

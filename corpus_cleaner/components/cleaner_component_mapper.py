import argparse
from corpus_cleaner.document import Document
from typing import Optional
from . import CleanerComponent


class CleanerComponentMapper(CleanerComponent):

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        raise NotImplementedError()

    def __call__(self, document: Optional[Document]) -> Optional[Document]:
        if document is None:
            return None
        return self.apply(document)

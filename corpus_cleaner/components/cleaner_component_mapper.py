import argparse
from corpus_cleaner.document import Document
from typing import Optional, Iterable
from . import CleanerComponent


class CleanerComponentMapper(CleanerComponent):

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def apply(self, document: Document) -> Optional[Document]:
        raise NotImplementedError()

    def __call__(self, documents: Iterable[Optional[Document]]) -> Iterable[Optional[Document]]:
        for document in documents:
            if document is not None:
                yield self.apply(document)

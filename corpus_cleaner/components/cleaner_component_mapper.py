import argparse
from abc import ABC

from corpus_cleaner.document import Document
from typing import Optional, Iterable
from . import CleanerComponent
from corpus_cleaner.components.cleaner_component import LegacyCleanerComponent


class CleanerComponentMapper(CleanerComponent, ABC):

    def apply(self, document: Document) -> Optional[Document]:
        raise NotImplementedError()

    def __call__(self, documents: Iterable[Optional[Document]]) -> Iterable[Document]:
        for document in documents:
            if document is not None:
                yield self.apply(document)


class LegacyCleanerComponentMapper(LegacyCleanerComponent):

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        raise NotImplementedError()

    def _one_call(self, document: Optional[Document]) -> Optional[Document]:
        if document is None:
            return None
        return self.apply(document)

    def __call__(self, documents: Iterable[Optional[Document]]) -> Iterable[Document]:
        for document in documents:
            if document is not None:
                yield self.apply(document)

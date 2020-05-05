from corpus_cleaner.document import Document
from typing import Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import argparse
from ordered_set import OrderedSet


class DocumentFilter(CleanerComponentMapper):  # TODO: Should be a reducer

    def _deduplicate(self, document: Document) -> Document:
        sentences_deduplicate = OrderedSet(document.sentences).items
        return sentences_deduplicate

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _filter(self, document: Optional[Document]) -> Optional[Document]:
        document.sentences = self._deduplicate(document)
        return document

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._filter(document)

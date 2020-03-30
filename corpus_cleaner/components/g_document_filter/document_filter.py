from corpus_cleaner.document import Document
from typing import Iterable, Union
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse
from ordered_set import OrderedSet


class DocumentFilter(CleanerComponent):

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

    def _filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        for doc in documents:
            doc.sentences = self._deduplicate(doc)
            yield doc

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._filter(documents)

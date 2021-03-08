from abc import ABC
from corpus_cleaner.document import Document
from typing import Optional, Iterable
from . import CleanerComponent


class CleanerComponentMapper(CleanerComponent, ABC):

    def apply(self, document: Document) -> Optional[Document]:
        raise NotImplementedError

    def __call__(self, documents: Iterable[Optional[Document]]) -> Iterable[Document]:
        for document in documents:
            if document is not None:
                yield self.apply(document)

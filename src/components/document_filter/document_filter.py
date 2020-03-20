from document import Document
from typing import Iterable


class DocumentFilter:
    def filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        return documents

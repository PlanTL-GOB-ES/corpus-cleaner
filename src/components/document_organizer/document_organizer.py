from document import Document
from typing import Iterable


class DocumentOrganizer:
    def organize_documents(self, documents: Iterable[Document]) -> Iterable[Iterable[Document]]:
        yield documents

    def _find_domains(self):
        raise NotImplementedError()

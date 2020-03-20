from document import Document
from typing import Iterable


class DocumentFilter:
    @staticmethod
    def deduplicate(document: Iterable[Document]) -> Iterable[Document]:
        for doc in document:
            doc.sentences = list(set(doc.sentences))
            yield doc


# TODO: implement test here
def test():
    pass


if __name__ == '__main__':
    test()

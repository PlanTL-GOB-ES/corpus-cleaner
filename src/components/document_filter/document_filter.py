from document import Document
from typing import Iterable, Union
from components.cleaner_component import CleanerComponent
import argparse


class DocumentFilter(CleanerComponent):

    def __init__(self, **kwargs):
        pass

    @staticmethod
    def deduplicate(document: Iterable[Document]) -> Iterable[Document]:
        for doc in document:
            doc.sentences = list(set(doc.sentences))
            yield doc

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        return documents

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document],
                                                                         Iterable[Iterable[Document], None]]:
        return self.filter(documents)


# TODO: implement test here
def test():
    pass


if __name__ == '__main__':
    test()

from document import Document
from typing import Iterable, Union
from components.cleaner_component import CleanerComponent
import argparse


class DocumentFilter(CleanerComponent):

    def __init__(self, args: argparse.Namespace):
        pass

    def _deduplicate(self, documents: Iterable[Document]) -> Iterable[Document]:
        for doc in documents:
            doc.sentences = list(set(doc.sentences))
            yield doc

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        return documents

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._filter(documents)


# TODO: implement test here
def test():
    pass


if __name__ == '__main__':
    test()

import argparse
from corpus_cleaner.document import Document
from typing import Iterable, Union, List


class CleanerComponent:

    def __init__(self, args: argparse.Namespace):
        self.args = args

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        raise NotImplementedError()

    def get_stats(self) -> List:
        return []

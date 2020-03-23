import argparse
from document import Document
from typing import Iterable, Union


class CleanerComponent:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document, None]]:
        raise NotImplementedError()

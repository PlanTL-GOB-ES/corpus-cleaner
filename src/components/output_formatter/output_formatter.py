from document import Document
from typing import Iterable, Union
from components.cleaner_component import CleanerComponent
import argparse


class OutputFormatter(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def output_format(self, path: str, documents: Iterable[Document]):
        raise NotImplementedError()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self.output_format(documents)

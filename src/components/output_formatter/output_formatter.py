from document import Document
from typing import Iterable, Union
from components.cleaner_component import CleanerComponent
import argparse


class OutputFormatter(CleanerComponent):
    def __init__(self, output_path: str = None, **kwargs):
        self.path = output_path

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _output_format(self, documents: Iterable[Document]):
        raise NotImplementedError()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._output_format(documents)

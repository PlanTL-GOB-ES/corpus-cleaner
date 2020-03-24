from document import Document
from typing import Iterable, Union
from components.cleaner_component import CleanerComponent
import argparse
import logging


class OutputFormatter(CleanerComponent):
    def __init__(self, args: argparse.Namespace, logger: logging.Logger, output_path: str = None):
        super().__init__(args, logger)
        self.path = args.output_path if args.output_path is not None else output_path

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

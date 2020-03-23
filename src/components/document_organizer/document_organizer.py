from document import Document
from typing import Iterable
from components.cleaner_component import CleanerComponent
import argparse


class DocumentOrganizer(CleanerComponent):
    def __init__(self, **kwargs):
        pass

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def organize_documents(self, documents: Iterable[Document]) -> Iterable[Iterable[Document]]:
        yield documents

    def _find_domains(self):
        raise NotImplementedError()

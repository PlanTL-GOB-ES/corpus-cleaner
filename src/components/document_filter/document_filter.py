from document import Document
from typing import Iterable
from components.cleaner_component import CleanerComponent
import argparse


class DocumentFilter(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    def filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        return documents

from document import Document
from typing import Iterable
from components.cleaner_component import CleanerComponent
import argparse


class DocumentFilter(CleanerComponent):

    def __init__(self, **kwargs):
        pass

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    def filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        return documents

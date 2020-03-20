from document import Document
from typing import Iterable
from components.cleaner_component import CleanerComponent
import argparse


class DocumentOrganizer(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    def organize_documents(self, documents: Iterable[Document]) -> Iterable[Iterable[Document]]:
        yield documents

    def _find_domains(self):
        raise NotImplementedError()

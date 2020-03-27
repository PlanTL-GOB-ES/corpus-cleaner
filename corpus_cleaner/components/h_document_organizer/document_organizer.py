from corpus_cleaner.document import Document
from typing import Iterable, Union
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse


class DocumentOrganizer(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def organize_documents(self, documents: Iterable[Document]) -> Iterable[Document]:
        # TODO add keywords/labels
        return documents

    def _find_domains(self):
        raise NotImplementedError()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self.organize_documents(documents)

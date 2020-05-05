from corpus_cleaner.document import Document
from typing import Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import argparse


class DocumentOrganizer(CleanerComponentMapper):  # TODO: Unclear whether it should be a mapper
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def organize_documents(self, document: Optional[Document]) -> Optional[Document]:
        # TODO add keywords/labels
        return document

    def _find_domains(self):
        raise NotImplementedError()

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self.organize_documents(document)

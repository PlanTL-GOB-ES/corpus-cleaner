from corpus_cleaner.document import Document
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import argparse
from typing import Optional
from corpus_cleaner.transforms import FixEncodingStringTransform


class EncodingFixer(CleanerComponentMapper):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self._fix_encoding_transform = FixEncodingTransform()

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _fix_encoding(self, document: Optional[Document]) -> Optional[Document]:
        # TODO: initialize the attribute operations in the Document class
        document.operations = []
        document.content = self._fix_encoding_transform(document.content)
        if document.content_orig != document.content:
            document.operations.append(f'{self.__class__.__name__}-_fix_encoding')
        return document

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._fix_encoding(document)


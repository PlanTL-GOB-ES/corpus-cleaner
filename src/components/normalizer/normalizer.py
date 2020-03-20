from document import Document
from typing import Iterable, Union, Dict
from components.cleaner_component import CleanerComponent
import argparse


class Normalizer:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    def __init__(self, spell_check: bool = False, terminology_norm: Union[None, Dict[str, str]] = None,
                 punctuation_norm: bool = False):
        self.spell_check = spell_check
        self.terminology_norm = terminology_norm
        self.punctuation_norm = punctuation_norm

    def normalize(self, documents: Iterable[Document]) -> Iterable[Document]:
        return documents

    def _spell_checking(self):
        raise NotImplementedError()

    def _terminology_normalization(self):
        raise NotImplementedError()

    def _punctuation_normalization(self):
        raise NotImplementedError()

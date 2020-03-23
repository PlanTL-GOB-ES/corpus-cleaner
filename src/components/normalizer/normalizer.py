from document import Document
from typing import Iterable, Union, Dict
from components.cleaner_component import CleanerComponent
import argparse


class Normalizer:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--spell-check', action='store_true', help='Apply spell checking.')
        parser.add_argument('--term-norm', type=str, help='Path to a terminology dictionary to appliy normalization',
                            default=None)
        parser.add_argument('--punctuation-norm', action='store_true', help='Apply punctuation normalization.')

    def __init__(self, spell_check: bool = False, terminology_norm: Union[None, Dict[str, str]] = None,
                 punctuation_norm: bool = False, **kwargs):
        self.spell_check = spell_check
        self.terminology_norm = terminology_norm
        self.punctuation_norm = punctuation_norm

    def normalize(self, documents: Iterable[Document]) -> Iterable[Document]:
        if self.spell_check:
            self._spell_checking()
        if self.terminology_norm is not None:
            self._terminology_normalization()
        if self.punctuation_norm:
            self._punctuation_normalization()
        return documents

    def _spell_checking(self):
        raise NotImplementedError()

    def _terminology_normalization(self):
        raise NotImplementedError()

    def _punctuation_normalization(self):
        raise NotImplementedError()

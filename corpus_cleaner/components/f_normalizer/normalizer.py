from corpus_cleaner.document import Document
from typing import Iterable, Union, Dict
from corpus_cleaner.components.cleaner_component import CleanerComponent
from mosestokenizer import MosesPunctuationNormalizer
import argparse


class Normalizer(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--spell-check', action='store_true', help='Apply spell checking.')
        parser.add_argument('--terminology-norm', type=str, help='Path to a terminology dictionary to appliy'
                                                                 'normalization',
                            default=None)
        parser.add_argument('--punctuation-norm', action='store_true', help='Apply punctuation normalization.')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, args: argparse.Namespace, spell_check: bool = False,
                 terminology_norm: Union[None, Dict[str, str]] = None, punctuation_norm: bool = False):
        super().__init__(args)
        self.spell_check = args.spell_check if args.spell_check is not None else spell_check
        self.terminology_norm = args.terminology_norm if args.terminology_norm is not None else terminology_norm
        self.punctuation_norm = args.punctuation_norm if args.punctuation_norm is not None else punctuation_norm
        self.language = args.lang_filter
        self.normalizers = []
        self._build_normalizers()

    def _normalize(self, documents: Iterable[Document]) -> Iterable[Document]:
        for doc in documents:
            sent_norms = []
            for sent in doc.sentences:
                sent_norm = sent
                for normalizer in self.normalizers:
                    sent_norm = normalizer(sent_norm)
                sent_norms.append(sent_norm)
            doc.sentences = sent_norms
            yield doc

    def _build_normalizers(self):
        if self.punctuation_norm:
            self.normalizers.append(self._punctuation_normalization())
        if self.spell_check:
            pass
        if self.terminology_norm is not None:
            pass

    def _spell_checking(self):
        raise NotImplementedError()

    def _terminology_normalization(self):
        raise NotImplementedError()

    def _punctuation_normalization(self):
        return MosesPunctuationNormalizer(self.language[0])

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._normalize(documents)

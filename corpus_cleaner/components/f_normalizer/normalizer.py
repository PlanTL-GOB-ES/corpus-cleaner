from corpus_cleaner.document import Document
from typing import Union, Dict, Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from sacremoses import MosesPunctNormalizer
import argparse


class Normalizer(CleanerComponentMapper):
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

    def _normalize(self, document: Optional[Document]) -> Optional[Document]:
        sent_norms = []
        for idx_sent, sent in enumerate(document.sentences):
            sent_norm = sent
            for normalizer in self.normalizers:
                sent_norm = normalizer(sent_norm)
                if self.debug and sent_norm:
                    if sent_norm != sent:
                        class_name = self.__class__.__name__
                        document.operations[idx_sent].append(f"{class_name}-{normalizer.__name__}")
            sent_norms.append(sent_norm)
        document.sentences = sent_norms
        return document

    def _build_normalizers(self):
        if self.punctuation_norm:
            self.normalizers.append(self._punctuation_normalization)
        if self.spell_check:
            raise NotImplementedError()
        if self.terminology_norm is not None:
            raise NotImplementedError()

    def _spell_checking(self):
        raise NotImplementedError()

    def _terminology_normalization(self):
        raise NotImplementedError()

    def _punctuation_normalization(self, sentence: str):
        return MosesPunctNormalizer(self.language[0]).normalize(sentence)

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._normalize(document)

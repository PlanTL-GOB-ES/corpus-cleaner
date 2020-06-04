from corpus_cleaner.document import Document
from typing import Union, Tuple, Optional, List
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from langid.langid import LanguageIdentifier, model
from ordered_set import OrderedSet
import argparse
import fasttext
import os
import re


class SentenceFilter(CleanerComponentMapper):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--char-length-filter-sentence', type=int, default=30,
                            help='filter sentences shorter than a given minimum character length')
        parser.add_argument('--profanity-check', action='store_true',
                            help='filter sentences with sensible content')
        parser.add_argument('--fast-lang-filter-threshold', type=float, help='If --lang-filter is set, minimum'
                                                                             'threshold for the faster lang identifier',
                            default=0.3)
        parser.add_argument('--slow-lang-filter-threshold', type=float, help='If --lang-filter is set, minimum'
                                                                             'threshold for the slower lang identifier',
                            default=0.9)
        parser.add_argument('--dictionary-filter-sen', type=str, help='Path to dictionary (plain text, one term per'
                                                                      'line of terms that should not appear in a'
                                                                      'sentence',
                            default=None)

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, args: argparse.Namespace, char_length_filter_sentence: int = 30, 
                 lang_filter: Union[Tuple[str], None] = None, slow_lang_filter_threshold: float = 0.90,
                 profanity_check: bool = True, dictionary_filter: Optional[str] = None):
        super().__init__(args)
        self.char_length_filter_sentence = args.char_length_filter_sentence if args.char_length_filter_sentence is not \
            None else char_length_filter_sentence
        self.profanity_check = args.profanity_check if args.profanity_check is not None else profanity_check
        self.lang_filter = args.lang_filter if args.lang_filter is not None else lang_filter
        self.lang_id = None
        self.fasttext_lid = None
        self.slow_lang_filter_threshold = args.slow_lang_filter_threshold if args.slow_lang_filter_threshold is not \
            None else slow_lang_filter_threshold
        self.dictionary_filter = \
            args.dictionary_filter_sen if args.dictionary_filter_sen is not None else dictionary_filter
        if self.dictionary_filter is not None:
            with open(self.dictionary_filter, 'r') as f:
                self.dictionary_filter = [line.strip() for line in f.readlines()]
        self.dictionary_filter_pattern = None
        self.filters = []
        self._get_filters()

    def _filter(self, document: Optional[Document]) -> Optional[Document]:
        sentences_filtered = []
        # first, de-duplicate sentences
        sentences_deduplicate = OrderedSet(document.sentences).items
        for sent in sentences_deduplicate:
            # keep only sentences that are not filtered out by all the filters
            if all(_filter(sent) for _filter in self.filters):
                sentences_filtered.append(sent)
        # return the document if contains at least one sentence
        if sentences_filtered:
            document.sentences = sentences_filtered
            return document
        else:
            return None

    def _get_filters(self):
        if self.char_length_filter_sentence is not None:
            self.filters.append(self._filter_by_char_len)
        if self.lang_filter is not None:
            self.fasttext_lid = fasttext.load_model(os.path.join('lib', 'lid.176.bin'))
            self.lang_id = LanguageIdentifier.from_modelstring(model, norm_probs=True)
            _ = self.lang_id.classify('')  # force init
            self.filters.append(self._filter_by_lang)
        if self.dictionary_filter is not None:
            self.dictionary_filter_pattern = re.compile("|".join(self.dictionary_filter))
            self.filters.append(self._filter_by_dict)

    def _filter_by_char_len(self, sentence: str) -> bool:
        if len(sentence) > self.char_length_filter_sentence:
            return True
        return False
        
    def _filter_by_lang(self, sentence: str) -> bool:
        res = self.fasttext_lid.predict(sentence.lower())
        lang = res[0][0][-2:]
        conf = res[1][0]
        if lang in self.lang_filter and conf > self.slow_lang_filter_threshold - 0.1:
            return True
        elif lang in self.lang_filter:
            res = self.lang_id.classify(sentence)
            if res[0] in self.lang_filter and res[1] > self.slow_lang_filter_threshold:
                return True
        return False

    def _filter_by_dict(self, sentence: str):
        if self.dictionary_filter_pattern.search(sentence):
            return False
        return True

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._filter(document)

# TODO: UDP. homoglyphs in prefilterer

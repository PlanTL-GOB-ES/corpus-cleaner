from corpus_cleaner.document import Document
from typing import Union, Tuple, Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from langid.langid import LanguageIdentifier, model
from dataclass import dataclass
from ordered_set import OrderedSet
from corpus_cleaner.filters import *
from filters import CascadeLangStringFilter
import fasttext
import os
import re


@dataclass
class SentenceFilterConfig:
    char_length_threshold: int = 20  # minimum character length

    word_length_threshold: int = 3  # minimum number of words

    length_filter: bool = True  # filter sentences shorter than a given minimum number of words AND
    # a minimum number of chars

    digits_percentage_threshold: float = 0.1  # maximum percentange of allowed digit characters

    profanity_check: bool = True  # filter sentences with sensible content

    fast_lang_filter_threshold: float = 0.3  # If --lang-filter is set, minimum threshold for the faster lang identifier

    slow_lang_filter_threshold: float = 0.9  # If --lang-filter is set, minimum threshold for the slower lang identifier

    lang_filter: str  # Apply language identifier for a given language

    lang_filter_src_tgt: bool = True  # Apply language filter on sentences with "src=" pattern

    code_threshold: float = 0.25  # Threshold (percentage) of code-like chars and tokens to filter
    # a sentence (-1 to deactivate)

    dictionary_filter: str  # Path to dictionary (plain text, one term per line of terms that
    # should not appear in a sentence

    dedup_same_doc_sentences: bool = True  # Deduplicate sentences in the same document

    src_tag_filter: bool = True  # Remove sentences with the pattern "src=".


class SentenceFilter(CleanerComponentMapper):

    def __init__(self, config: SentenceFilterConfig):
        super().__init__()
        self._config = config
        self._string_filters = self._build_string_filters()

    def _build_string_filters(self):
        filters = []

        if self._config.length_filter is not None:
            filters.append(LenStringFilter(char_length_threshold=self._config.char_length_threshold,
                                           word_length_threshold=self._config.word_length_threshold))

        if self._config.code_threshold != -1:
            filters.append(CodeStringFilter(code_threshold=self._config.code_threshold))

        if self._config.digits_percentage_threshold > 0:
            filters.append(DigitsStringFilter(digits_percentage_threshold=self._config.digits_percentage_threshold))

        if self._config.lang_filter:
            filters.append(self._config.CascadeLangStringFilter(
                lang_filter=self._config.lang_filter,
                fast_lang_filter_threshold=self._config.fast_lang_filter_threshold,
                slow_lang_filter_threshold=self._config.slow_lang_filter_threshold))

        if self._config.dictionary_filter is not None:
            with open(self._config.dictionary_filter) as df:
                dictionary_terms = [t.strip('\n') for t in df.readlines()]
            filters.append(DictStringFilter(dictionary_terms=dictionary_terms))

        if self._config.lang_filter_sentence_src_tgt:
            self._config.src_tag_pattern = re.compile('src=')
            filters.append(SrcTgtStringFilter())

        return filters

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        sentences = []
        # For each document, get the set of duplicate sentences to remove
        if self._config.dedup_same_doc_sentences:
            document.sentences = list(OrderedSet(document.sentences))

        for sentence_idx, sentence in enumerate(document.sentences):
            for string_filter in self._string_filters:
                keep, reason = string_filter(sentence)
                if not keep:
                    if sentence:
                        class_name = self.__class__.__name__
                        filter_name = string_filter.__class__.__name__
                        document.operations[sentence_idx].append(f"{class_name}-{filter_name}:{reason}")
                    sentences.append('')
                    break
                else:
                    sentences.append(sentence)

        # In normal model, return the document only when all the sentences are not empty
        if not '' in sentences and len(sentences) > 0:
            document.sentences = sentences
            return document
        else:
            # if debug mode is on, return also document with
            # TOFIX: implement the debug attribute for this component
            if self.debug:
                document.sentences = sentences
                return document
        return None

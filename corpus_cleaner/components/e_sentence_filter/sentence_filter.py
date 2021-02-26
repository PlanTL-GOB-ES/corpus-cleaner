from corpus_cleaner.document import Document
from typing import Union, Tuple, Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from langid.langid import LanguageIdentifier, model
from dataclass import dataclass
from corpus_cleaner.filters import *
import fasttext
import os
import re


@dataclass
class SentenceFilterConfig:
    char_length_threshold: int = 20  # minimum character length

    word_length_threshold: int = 3  # minimum number of words

    length_filter: bool = True  # filter sentences shorter than a given minimum number of words AND
    # a minumum number of chars

    digits_percentage_threshold: float = 0.1  # maximum percentange of allowed digit characters

    profanity_check: bool = True  # filter sentences with sensible content

    fast_lang_filter_threshold: float = 0.3  # If --lang-filter is set, minimum threshold for the faster lang identifier

    slow_lang_filter_threshold: float = 0.9  # If --lang-filter is set, minimum threshold for the slower lang identifier

    lang_filter: bool = True  # Apply language filter on sentences

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

        # TODO: import class from?
        if self._config.lang_filter is not None and self._config.lang_filter_sentence:
            self._config.fasttext_lid = fasttext.load_model(os.path.join('lib', 'lid.176.bin'))
            self._config.lang_id = LanguageIdentifier.from_modelstring(model, norm_probs=True)
            _ = self._config.lang_id.classify('')  # force init
            filters.append(self._config._filter_by_lang)

        if self._config.dictionary_filter is not None:
            with open(self._config.dictionary_filter) as df:
                dictionary_terms = [t.strip('\n') for t in df.readlines()]
            filters.append(DictStringFilter(dictionary_terms=dictionary_terms))

        # TODO: figure out which filter class is appropriate for sentences deduplication
        if self._config.dedup_same_doc_sentences:
            filters.append()

        if self._config.lang_filter_sentence_src_tgt:
            self._config.src_tag_pattern = re.compile('src=')
            filters.append(SrcTgtStringFilter())

        return filters

    # TODO: implement apply
    def apply(self, document: Optional[Document]) -> Optional[Document]:
        sentences = []
        # For each document, get the set of duplicate sentences to remove
        self.sentences_duplicate = set(sentence for sentence in document.sentences
                                       if document.sentences.count(sentence) > 1)
        for sentence_idx, sentence in enumerate(document.sentences):
            keep = True
            for filter_ in self.filters:
                keep, value = filter_(sentence)
                if not keep:
                    # if debug, keep an empty sentence as cleaned
                    if self.debug:
                        # register operation only if the sentence is not empty
                        if sentence:
                            class_name = self.__class__.__name__
                            filter_name = filter_.__name__
                            document.operations[sentence_idx].append(f"{class_name}-{filter_name}:{value}")
                        sentences.append('')
                    break
            if keep:
                sentences.append(sentence)
        # In normal model, return the document only when all the sentences are not empty
        if not '' in sentences and len(sentences) > 0:
            document.sentences = sentences
            return document
        else:
            # if debug mode is on, return also document with
            if self.debug:
                document.sentences = sentences
                return document
        return None

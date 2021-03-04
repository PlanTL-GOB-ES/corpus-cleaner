from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from corpus_cleaner import DiscardedDocument
from dataclasses import dataclass
from ordered_set import OrderedSet
from corpus_cleaner.filters import *
from typing import Dict
from corpus_cleaner.transforms import *


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

    lang_filter: bool = True  # Apply language filter on documents. PREVIOUSLY: Don't write --no-lang-filter-document.

    lang_filter_src_tgt: bool = True  # Apply language filter on sentences with "src=" pattern

    target_langs: Optional[Tuple[str]] = None  # Target languages. PREVIOUSLY: --lang-

    code_threshold: float = 0.25  # Threshold (percentage) of code-like chars and tokens to filter
    # a sentence (-1 to deactivate)

    dictionary_filter: Optional[str] = None  # Path to dictionary (plain text, one term per line of terms that
    # should not appear in a sentence

    dedup_same_within_sentences: bool = True  # Deduplicate sentences within the same document

    src_tag_filter: bool = True  # Remove sentences with the pattern "src=".

    punctuation_norm: bool = False  # Apply punctuation normalization

    spell_check: bool = False  # Apply spell checking (not implemented)

    terminology_norm: Optional[Dict[str, str]] = None  # Apply terminology normalization (not implemented)


class SentenceFilter(CleanerComponentMapper):

    def __init__(self, config: SentenceFilterConfig):
        super().__init__()
        self._config = config
        self._string_filters = self._build_string_filters()
        self._string_transforms = self._build_string_transforms()

    def _build_string_filters(self) -> List[StringFilter]:
        filters = []

        if self._config.length_filter is not None:
            filters.append(LenStringFilter(char_length_threshold=self._config.char_length_threshold,
                                           word_length_threshold=self._config.word_length_threshold))

        if self._config.code_threshold != -1:
            filters.append(CodeStringFilter(code_threshold=self._config.code_threshold))

        if self._config.digits_percentage_threshold > 0:
            filters.append(DigitsStringFilter(digits_percentage_threshold=self._config.digits_percentage_threshold))

        if self._config.lang_filter:
            filters.append(CascadeLangStringFilter(
                languages=set(self._config.target_langs),
                fast_lang_filter_threshold=self._config.fast_lang_filter_threshold,
                slow_lang_filter_threshold=self._config.slow_lang_filter_threshold,
                replace_urls=True
            ))

        if self._config.dictionary_filter is not None:
            with open(self._config.dictionary_filter) as df:
                dictionary_terms = [t.strip('\n') for t in df.readlines()]
            filters.append(DictStringFilter(dictionary_terms=dictionary_terms))

        if self._config.lang_filter_src_tgt:
            filters.append(SrcTgtStringFilter())

        return filters

    def _build_string_transforms(self) -> List[StringTransform]:
        transforms = []
        if self._config.punctuation_norm:
            transforms.append(PunctuationNormalizationStringTransform(self._config.target_langs[0]))
        if self._config.spell_check:
            raise NotImplementedError
        if self._config.terminology_norm is not None:
            raise NotImplementedError
        return transforms

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        if not isinstance(document, DiscardedDocument):
            # For each document, get the set of duplicate sentences to remove
            if self._config.dedup_same_within_sentences:
                document.sentences_cleaned = list(OrderedSet(document.sentences_cleaned))

            # Sentence-level filters
            for sentence_idx, sentence in enumerate(document.sentences_cleaned):
                for string_filter in self._string_filters:
                    keep, reason = string_filter(sentence)
                    if not keep:
                        class_name = self.__class__.__name__
                        filter_name = string_filter.__class__.__name__
                        document.register_operation(operation=f"{class_name}-{filter_name}:{reason}",
                                                        sublist_index=sentence_idx)
                        document.sentences_cleaned[sentence_idx] = None
                        break

            # Sentence-level string transforms. Here, we apply them AFTER filtering, not before (unlike in PreFilterer)
            # because they are normalizations, so we don't really need to apply them unless we are sure that we are
            # going to keep the sentence. In previous implementations, this was within Normalizer
            for sentence_idx, sentence in enumerate(document.sentences_cleaned):
                for string_transform in self._string_transforms:
                    sentence_norm = string_transform(sentence)
                    if sentence_norm != sentence:
                        class_name = self.__class__.__name__
                        document.register_operation(operation=f"{class_name}-{string_transform.__name__}",
                                                    sublist_index=sentence_idx)
                        document.sentences_cleaned[sentence_idx] = sentence_norm

        return document

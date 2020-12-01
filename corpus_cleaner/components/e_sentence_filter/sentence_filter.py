from corpus_cleaner.document import Document
from typing import Union, Tuple, Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from langid.langid import LanguageIdentifier, model
import argparse
import fasttext
import os
import re


class SentenceFilter(CleanerComponentMapper):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--char-length-filter-sentence', type=int, default=20,
                            help='filter sentences shorter than a given minimum character length')
        parser.add_argument('--word-length-filter-sentence', type=int, default=3,
                            help='filter sentences shorter than a given minimum word length')
        parser.add_argument('--digits-filter-sentence', type=float,
                            help='Maximum allowed proportion of digit characters in the sentence',
                            default=0.1)
        parser.add_argument('--profanity-check', action='store_true',
                            help='filter sentences with sensible content')
        parser.add_argument('--fast-lang-filter-threshold', type=float, help='If --lang-filter is set, minimum'
                                                                             'threshold for the faster lang identifier',
                            default=0.3)
        parser.add_argument('--slow-lang-filter-threshold', type=float, help='If --lang-filter is set, minimum'
                                                                             'threshold for the slower lang identifier',
                            default=0.9)
        parser.add_argument('--no-lang-filter-sentence', action='store_true',
                            help='Avoid applying language filter on sentences')
        parser.add_argument('--no-lang-filter-sentence_src_tgt', action='store_true',
                            help='Avoid applying language filter on sentences with "src=" pattern')

        parser.add_argument('--code-threshold', type=float, help='Threshold (percentage) of code-like chars and tokens'
                                                                 'to filter a sentence (-1 to deactivate)',
                            default=0.25)
        parser.add_argument('--dictionary-filter-sen', type=str, help='Path to dictionary (plain text, one term per'
                                                                      'line of terms that should not appear in a'
                                                                      'sentence',
                            default=None)
        parser.add_argument('--no-dedup-same-doc-sentences', action='store_true',
                            help='Do not deduplicate sentences in the same document.')
        parser.add_argument('--no-src-tag-filter', action='store_true',
                            help='Do not remvoe sentences with the pattern "src=".')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, args: argparse.Namespace, char_length_filter_sentence: int = 30,
                 word_length_filter_sentence: int = 3,
                 digits_filter_sentence: float = 0.1,
                 lang_filter: Union[Tuple[str], None] = None, slow_lang_filter_threshold: float = 0.90,
                 fast_lang_filter_threshold: float = 0.9,
                 no_lang_filter_sentence: bool = False,
                 code_threshold: float = 0.25,
                 profanity_check: bool = False, dictionary_filter: Optional[str] = None,
                 dedup_same_doc_sentences: bool = True,
                 src_tag_filter: bool = True):
        # TODO: Review way of setting defaults, thresholds will never be None!
        super().__init__(args)
        self.char_length_filter_sentence = args.char_length_filter_sentence if args.char_length_filter_sentence is not \
                                                                               None else char_length_filter_sentence
        self.word_length_filter_sentence = args.word_length_filter_sentence if args.word_length_filter_sentence is not \
                                                                               None else word_length_filter_sentence
        self.digits_filter_sentence = args.digits_filter_sentence if args.digits_filter_sentence is not None else digits_filter_sentence
        self.profanity_check = args.profanity_check if args.profanity_check is not None else profanity_check
        self.lang_filter = args.lang_filter if args.lang_filter is not None else lang_filter
        self.lang_id = None
        self.fasttext_lid = None
        self.slow_lang_filter_threshold = args.slow_lang_filter_threshold if args.slow_lang_filter_threshold is not \
                                                                             None else slow_lang_filter_threshold
        self.fast_lang_filter_threshold = args.fast_lang_filter_threshold if args.fast_lang_filter_threshold is not \
                                                                             None else fast_lang_filter_threshold
        self.lang_filter_sentence = not args.no_lang_filter_sentence \
            if args.no_lang_filter_sentence is not None else not no_lang_filter_sentence
        self.lang_filter_sentence_src_tgt = not args.no_lang_filter_sentence_src_tgt \
            if args.no_lang_filter_sentence_src_tgt is not None else not no_lang_filter_sentence_src_tgt

        self.code_threshold = args.code_threshold if args.code_threshold is not None else code_threshold
        self.dictionary_filter = \
            args.dictionary_filter_sen if args.dictionary_filter_sen is not None else dictionary_filter
        if self.dictionary_filter is not None:
            with open(self.dictionary_filter, 'r') as f:
                self.dictionary_filter = [line.strip() for line in f.readlines()]
        self.dictionary_filter_pattern = None
        self.filters = []
        self.code_keywords_pattern = re.compile('\\b(var|function|const|if|else|script)\\b')
        self.code_chars_pattern = re.compile('[;=&\[\](){}/\\\\]')
        self.dedup_same_doc_sentences = \
            not args.no_dedup_same_doc_sentences if args.no_dedup_same_doc_sentences is not None else dedup_same_doc_sentences
        self.debug = args.debug
        self.sentences_duplicate = None
        self.lang_filter_sentence_src_tgt = not args.no_src_tag_filter if args.no_lang_filter_sentence is not None else src_tag_filter
        self.src_tag_pattern = None

        self._get_filters()

    def _get_filters(self):
        if self.char_length_filter_sentence is not None:
            self.filters.append(self._filter_by_len)
        if self.code_threshold != -1:
            self.filters.append(self._filter_by_code)
        if self.digits_filter_sentence > 0:
            self.filters.append(self._filter_by_digits)
        if self.lang_filter is not None and self.lang_filter_sentence:
            self.fasttext_lid = fasttext.load_model(os.path.join('lib', 'lid.176.bin'))
            self.lang_id = LanguageIdentifier.from_modelstring(model, norm_probs=True)
            _ = self.lang_id.classify('')  # force init
            self.filters.append(self._filter_by_lang)
        if self.dictionary_filter is not None:
            self.dictionary_filter_pattern = re.compile("|".join(self.dictionary_filter))
            self.filters.append(self._filter_by_dict)
        if self.dedup_same_doc_sentences:
            self.filters.append(self._filter_by_duplicate)
        if self.lang_filter_sentence_src_tgt:
            self.src_tag_pattern = re.compile('src=')
            self.filters.append(self._filter_by_src_tag)

    def _filter_by_len(self, sentence: str):
        len_sentence = len(sentence)
        len_words = len(sentence.split(' '))
        if len_sentence > self.char_length_filter_sentence and len_words > self.word_length_filter_sentence:
            return True, None
        value = f"({round(len_sentence)} chars, {len_words} words)"
        return False, value

    def _filter_by_code(self, sentence: str):
        value = (len(re.findall(self.code_keywords_pattern, sentence)) / len(sentence.split())) \
                + len(re.findall(self.code_chars_pattern, sentence)) / len(sentence)
        if value > self.code_threshold:
            return False, round(value, 2)
        return True, None

    def _filter_by_digits(self, sentence):
        sentence_chars = ''.join(sentence.split())
        value = sum(c.isdigit() for c in sentence_chars) / len(sentence_chars)
        if value >= self.digits_filter_sentence:
            return False, round(value, 2)
        return True, None

    def _filter_by_src_tag(self, sentence):
        found = self.src_tag_pattern.search(sentence)
        if found is None:
            return True, None
        return False, found.span()

    def _filter_by_lang(self, sentence: str):
        res = self.fasttext_lid.predict(sentence.lower())
        lang = res[0][0][-2:]
        conf = res[1][0]
        if lang in self.lang_filter and conf > self.fast_lang_filter_threshold:
            return True, None
        elif lang in self.lang_filter:
            res = self.lang_id.classify(sentence)
            lang = res[0]
            conf = res[1]
            if lang in self.lang_filter and conf > self.slow_lang_filter_threshold:
                return True, None
            else:
                value = f"({round(conf, 2)}, {lang})"
                return False, value
        value = f"({round(conf, 2)}, {lang})"
        return False, value

    def _filter_by_dict(self, sentence: str):
        if self.dictionary_filter_pattern.search(sentence):
            return False, None
        return True, None

    def _filter_by_duplicate(self, sentence: str):
        if sentence in self.sentences_duplicate:
            return False, None
        return True, None

    # TODO: add decorators to register the filters
    def _filter(self, document: Optional[Document]) -> Optional[Document]:
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

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._filter(document)

# TODO: UDP. homoglyphs in prefilterer

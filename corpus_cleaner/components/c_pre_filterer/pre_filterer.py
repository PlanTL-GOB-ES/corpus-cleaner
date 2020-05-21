from typing import Union, Tuple, List, Optional
from corpus_cleaner.document import Document
from alphabet_detector import AlphabetDetector
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import re
import argparse
import fasttext
import os


class PreFilterer(CleanerComponentMapper):

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--no-remove-tags', action='store_true', help='Avoid removing XML/HTML tags')
        parser.add_argument('--no-remove-extra-spaces', action='store_true', help='Avoid removing XML/HTML tags')
        parser.add_argument('--no-replace-urls', action='store_true', help='Avoid replacing URLs with "[URL]"')
        parser.add_argument('--char-length-filter', type=int, help='Minimum char length per document. Set to 0 not'
                                                                   'to apply any filter.', default=40)
        parser.add_argument('--no-head-filter', action='store_true', help='Avoid filtering documents coming from'
                                                                          'a crawler (having a "heads" attribute) with'
                                                                          'common HTTP errors.')
        parser.add_argument('--digits_filter', type=float, help='Maximum allowed proportion of digit characters',
                            default=0.1)
        parser.add_argument('--alphanum_filter', type=float, help='Maximum allowed proportion of non-alphanumeric'
                                                                  'characters', default=0.1)
        parser.add_argument('--uppercase_filter', type=float, help='Maximum allowed proportion of uppercase characters',
                            default=0.4)
        parser.add_argument('--alphabet-filter', type=str, help='Alphabets that should be present (eg. LATIN)',
                            nargs='+', default=['LATIN'])
        parser.add_argument('--lang-filter', type=str, help='List of languages that should allowed when filtering by'
                                                            'lang. If not set, no filtering is applied.',
                            nargs='+')
        parser.add_argument('--fast-lang-filter-threshold', type=float, help='If --lang-filter is set, minimum'
                                                                             'threshold for the faster lang identifier',
                            default=0.3)
        parser.add_argument('--dictionary-filter-doc', type=str, help='Path to dictionary (plain text, one term per'
                                                                      'line of terms that should not appear in a'
                                                                      'document',
                            default=None)

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, args: argparse.Namespace, no_remove_tags: bool = False, no_remove_extra_spaces: bool = False,
                 no_replace_urls: bool = False,
                 char_length_filter: int = 40, no_head_filter: bool = False, digits_filter: float = 0.1,
                 alphanum_filter: float = 0.1, uppercase_filter: float = 0.4,
                 alphabet_filter: Union[Tuple[str], None] = ('LATIN',), lang_filter: Union[Tuple[str], None] = None,
                 fast_lang_filter_threshold: float = 0.3,
                 dictionary_filter: Optional[str] = None):
        super().__init__(args)
        self.remove_tags = not args.no_remove_tags if args.no_remove_tags is not None else not no_remove_tags
        self.tags_pattern = None
        self.remove_extra_spaces = not args.no_remove_extra_spaces if args.no_remove_extra_spaces is not None else not \
            no_remove_extra_spaces
        self.extra_spaces_pattern = None
        self.replace_urls = not args.no_replace_urls if args.no_replace_urls is not None else not no_replace_urls
        self.urls_pattern = None
        self.char_length_filter = args.char_length_filter if args.char_length_filter is not None else char_length_filter
        self.head_filter = not args.no_head_filter if args.no_head_filter is not None else not no_head_filter
        self.digits_filter = args.digits_filter if args.digits_filter is not None else digits_filter
        self.alphanum_filter = args.alphanum_filter if args.alphanum_filter is not None else alphanum_filter
        self.uppercase_filter = args.uppercase_filter if args.uppercase_filter is not None else uppercase_filter
        self.alphabet_filter = args.alphabet_filter if args.alphabet_filter is not None else alphabet_filter
        self.lang_filter = args.lang_filter if args.lang_filter is not None else lang_filter
        self.fasttext_lid = None
        self.fast_lang_filter_threshold = args.fast_lang_filter_threshold if args.fast_lang_filter_threshold is not \
                                                                             None else fast_lang_filter_threshold
        self.dictionary_filter =\
            args.dictionary_filter_doc if args.dictionary_filter_doc is not None else dictionary_filter
        if self.dictionary_filter is not None:
            with open(self.dictionary_filter, 'r') as f:
                self.dictionary_filter = f.readlines()

        self.dictionary_filter_pattern = None
        self.input_format = args.input_format
        self.filters = []
        self._build_filters()

    # TODO: move the remove operations to a new component called CharFilter
    def _remove_tags(self, text):
        return self.tags_pattern.sub(' ', self.p_tags_pattern.sub('. ', text))

    def _remove_extra_spaces(self, text):
        replace = ' '
        return self.extra_spaces_pattern.sub(replace, text).strip()

    def _replace_urls(self, text):
        replace = '[URL]'
        return self.urls_pattern.sub(replace, text)

    def _build_filters(self):
        if self.remove_tags:
            self.tags_pattern = re.compile(' *(<.*?> ?)+ *')
            self.p_tags_pattern = re.compile('([.|?]*\s*)(<p>)+')
        if self.remove_extra_spaces:
            self.extra_spaces_pattern = re.compile(r'\s+')
        if self.replace_urls:
            # slightly modified from: https://stackoverflow.com/questions/6718633/python-regular-expression-again-match-url
            # to account for: 1) words attached at the beginning and the end of the url
            #                 2) mantaining period at the end to improve sentence splitter
            # TODO: use a list of all the alphabet for each language instead of hard-coded accented characters
            self.urls_pattern = re.compile(
                '([áéóüñúí\w]+)?((http|https)://)?[a-zA-Z0-9./?:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9&/?:@\-_=#])*([áéóüñúí\w]+)?')
        if self.char_length_filter > 0:
            self.filters.append(self._filter_by_length)
        if self.head_filter:
            self.filters.append(self._filter_by_heads)
        if self.digits_filter > 0:
            self.filters.append(self._filter_by_digits)
        if self.alphanum_filter > 0:
            self.filters.append(self._filter_by_alphanum)
        if self.uppercase_filter > 0:
            self.filters.append(self._filter_by_alphanum)
        if self.alphabet_filter is not None:
            self.ad = AlphabetDetector()
            self.filters.append(self._filter_by_alphabet)
        if self.lang_filter is not None:
            if self.replace_urls:
                self.url_placeholder_pattern = re.compile('\s+\[URL\]')
            else:
                self.url_placeholder_pattern = re.compile(
                    "((\w+):\/\/)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
                )
            self.no_eols_pattern = re.compile('\n')
            self.fasttext_lid = fasttext.load_model(os.path.join('lib', 'lid.176.bin'))
            self.filters.append(self._filter_by_lang)
        if self.dictionary_filter is not None:
            self.dictionary_filter_pattern = re.compile("|".join(self.dictionary_filter))
            self.filters.append(self._filter_by_dict)

    def _filter_by_length(self, doc: Document):
        if len(doc.content) < self.char_length_filter:
            return False
        return True

    @staticmethod
    def _filter_by_heads(doc: Document):
        if doc.heads is not None:
            for token in ['found', '404', 'robots.txt', 'error', 'trouvée']:
                if re.search(token, doc.heads, re.IGNORECASE):
                    return False
        return True

    def _filter_by_digits(self, doc: Document):
        if sum(c.isdigit() for c in doc.content) / len(doc.content) > self.digits_filter:
            return False
        return True

    def _filter_by_alphanum(self, doc: Document):
        concat_content = ''.join(doc.content.split())
        if (1 - (sum(c.isalnum() for c in concat_content) / len(concat_content))) > self.alphanum_filter:
            return False
        return True

    def _filter_by_uppercase(self, doc: Document):
        if sum(c.isupper() for c in doc.content) / len(doc.content) > self.uppercase_filter:
            return False
        return True

    def _filter_by_alphabet(self, doc: Document):
        # TODO: Check thresholds?
        if len(self.ad.detect_alphabet(doc.content).intersection(set(self.alphabet_filter))) == 0:
            return False
        return True

    def _filter_by_lang(self, doc: Document):
        content = self.url_placeholder_pattern.sub('', doc.content)
        content = self.no_eols_pattern.sub('. ', content)
        res = self.fasttext_lid.predict(content)
        lang = res[0][0][-2:]
        conf = res[1][0]
        if lang in self.lang_filter and conf > self.fast_lang_filter_threshold:
            doc.language = lang
            return True
        return False

    def _filter_by_dict(self, doc: Document):
        if self.dictionary_filter_pattern.search(doc.content):
            return False
        return True

    def _filter(self, document: Optional[Document]) -> Optional[Document]:
        if self.remove_tags:
            document.content = self._remove_tags(document.content)
        if self.remove_extra_spaces:
            document.content = self._remove_extra_spaces(document.content)
        if self.replace_urls:
            document.content = self._replace_urls(document.content)
        keep = True
        for filter_ in self.filters:
            keep = filter_(document)
            if not keep:
                break
        if keep:
            return document
        return None

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._filter(document)

from typing import Union, Tuple, Optional
from corpus_cleaner.document import Document
from alphabet_detector import AlphabetDetector
from textnorm import normalize_space
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import re
import argparse
import fasttext
import os
from corpus_cleaner.configs.langs import langs
import regex


# TODO: implement decorator that register the name of the operation (replace/filter) applied to each sentence
#       That information will be used to list the operations applied to the sentences during the cleaning process
def debug_filter(func):
    def debug(self, doc):
        if self.debug:
            keep, value = func(self, doc)
            if not keep:
                class_name = self.__class__.__name__
                filter_name = func.__name__
                doc.operations.append(f"{class_name}-{filter_name}:{value}")
                doc.content = ''
            return keep, value
        else:
            return func(self, doc)

    return debug


class PreFilterer(CleanerComponentMapper):

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--none_filter', action='store_true', help='Apply no filters')
        parser.add_argument('--no-lang-filter-document', action='store_true',
                            help='Avoid applying language filter on documents')
        parser.add_argument('--no-language-normalization', action='store_true',
                            help='Avoid applying language-specific normalization')
        parser.add_argument('--no-replace-emails', action='store_true',
                            help='Avoid replacing email adresses with "[EMAIL]"')
        parser.add_argument('--no-remove-hashtags-mentions', action='store_true', help='Remove hashtags and mentions.')
        parser.add_argument('--no-remove-tags', action='store_true', help='Avoid removing XML/HTML tags')
        parser.add_argument('--no-space-normalization', action='store_true', help='Avoid normalizing white spaces')
        parser.add_argument('--no-replace-urls', action='store_true', help='Avoid replacing URLs with "[URL]"')
        parser.add_argument('--char-length-filter-document', type=int,
                            help='Minimum char length per document. Set to 0 not to apply any filter.', default=40)
        parser.add_argument('--no-head-filter', action='store_true', help='Avoid filtering documents coming from'
                                                                          'a crawler (having a "heads" attribute) with'
                                                                          'common HTTP errors.')
        parser.add_argument('--digits_filter', type=float, help='Maximum allowed proportion of digit characters',
                            default=0.1)
        parser.add_argument('--remove-citations', action='store_true',
                            help='If used, remove citations in the common square brackets format, e.g [34]')
        parser.add_argument('--lang-chars-filter', type=float, help='Maximum allowed proportion of characters not'
                                                                    'belonging to the alphabet of the language',
                            default=0.1)
        parser.add_argument('--alphanum-filter', type=float, help='Maximum allowed proportion of non-alphanumeric'
                                                                  'characters', default=0.3)
        parser.add_argument('--uppercase-filter', type=float, help='Maximum allowed proportion of uppercase characters',
                            default=0.4)
        parser.add_argument('--alphabet-filter', type=str, help='Alphabets that should be present (eg. LATIN)',
                            nargs='+', default=['LATIN'])
        parser.add_argument('--lang-filter', type=str, help='List of languages that should allowed when filtering by'
                                                            'lang. If not set, no filtering is applied.',
                            nargs='+')
        parser.add_argument('--initial-lang-filter-threshold', type=float, help='If --lang-filter is set, minimum'
                                                                                'threshold for the initial lang'
                                                                                'identifier',
                            default=0.3)
        parser.add_argument('--dictionary-filter-doc', type=str, help='Path to dictionary (plain text, one term per'
                                                                      'line of terms that should not appear in a'
                                                                      'document',
                            default=None)
        parser.add_argument('--seg-sentences', action='store_true', help='Segment wrongfully concatenated sentences.')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, args: argparse.Namespace,
                 no_lang_filter_document: bool = False,
                 no_language_normalization: bool = False,
                 no_replace_emails: bool = False,
                 no_remove_hashtags_mentions: bool = False, no_remove_tags: bool = False,
                 no_space_normalization: bool = False, no_replace_urls: bool = False,
                 char_length_filter_document: int = 40, no_head_filter: bool = False, digits_filter: float = 0.1,
                 remove_citations: bool = False, lang_chars_filter: float = 0.1,
                 alphanum_filter: float = 0.3, uppercase_filter: float = 0.4,
                 alphabet_filter: Union[Tuple[str], None] = ('LATIN',), lang_filter: Union[Tuple[str], None] = None,
                 initial_lang_filter_threshold: float = 0.3,
                 dictionary_filter: Optional[str] = None,
                 seg_sentences: bool = False,
                 none_filter: bool = False):
        super().__init__(args)
        self.lang_filter_document = not args.no_lang_filter_document if args.no_lang_filter_document is not None else not no_lang_filter_document
        self.language_normalization = not args.no_language_normalization if args.no_language_normalization is \
                                                                            not None else not no_language_normalization
        self.replace_emails = not args.no_replace_emails if args.no_replace_emails is not None else not no_replace_emails
        self.emails_pattern = None
        self.remove_hashtags_mentions = not args.no_remove_hashtags_mentions if args.no_remove_hashtags_mentions is \
                                                                                not None else not no_remove_hashtags_mentions
        self.remove_hashtags_pattern = None
        self.remove_tags = not args.no_remove_tags if args.no_remove_tags is not None else not no_remove_tags
        self.tags_pattern = None
        self.space_normalization = not args.no_space_normalization if args.no_space_normalization is not None else not \
            no_space_normalization
        self.extra_spaces_pattern = None
        self.replace_urls = not args.no_replace_urls if args.no_replace_urls is not None else not no_replace_urls
        self.urls_pattern = None
        self.char_length_filter_document = args.char_length_filter_document if args.char_length_filter_document is not None else char_length_filter_document
        self.head_filter = not args.no_head_filter if args.no_head_filter is not None else not no_head_filter
        self.digits_filter = args.digits_filter if args.digits_filter is not None else digits_filter
        self.remove_citations = args.remove_citations if args.remove_citations else remove_citations
        self.alphanum_filter = args.alphanum_filter if args.alphanum_filter is not None else alphanum_filter
        self.lang_chars_filter = args.lang_chars_filter if args.lang_chars_filter is not None else lang_chars_filter
        self.uppercase_filter = args.uppercase_filter if args.uppercase_filter is not None else uppercase_filter
        self.alphabet_filter = args.alphabet_filter if args.alphabet_filter is not None else alphabet_filter
        self.lang_filter = args.lang_filter if args.lang_filter is not None else lang_filter
        self.alphabet = set([])
        for lang in self.lang_filter:
            self.alphabet.update(langs[lang]['alphabet'])
            self.lang_chars = ("".join(char for char in self.alphabet if char.isalpha()))
        self.fasttext_lid = None
        self.initial_lang_filter_threshold = args.fast_lang_filter_threshold if args.initial_lang_filter_threshold is not \
                                                                                None else initial_lang_filter_threshold
        self.dictionary_filter = \
            args.dictionary_filter_doc if args.dictionary_filter_doc is not None else dictionary_filter
        if self.dictionary_filter is not None:
            with open(self.dictionary_filter, 'r') as f:
                self.dictionary_filter = f.readlines()

        self.dictionary_filter_pattern = None
        self.seg_sentences = args.seg_sentences if args.seg_sentences is not None else seg_sentences
        self.input_format = args.input_format
        self.filters = []
        self.do_filter = args.none_filter if args.none_filter is not None else none_filter
        self._build_filters()
        if not self.do_filter:
            self.filters = []

    # TODO: move the remove operations to a new component called CharFilter
    def _language_normalization(self, langs, text):
        if 'ca' in langs:
            text, subs = self.geminate_l_pattern.subn('l·l', text)
            return text, bool(subs)
        else:
            return text, False

    def _remove_citations(self, text):
        text, subs = self.remove_citations_pattern.subn('', text)
        return text, bool(subs)

    def _replace_emails(self, text):
        replace = ' [EMAIL] '
        text, subs = self.emails_pattern.subn(replace, text)
        return text, bool(subs)

    def _remove_hashtags_mentions(self, text):
        text, subs = self.remove_hashtags_pattern.subn(' ', text)
        return text, bool(subs)

    def _remove_tags(self, text):
        text, subs = self.tags_pattern.subn(' ', self.p_tags_pattern.sub('\n', text))
        return text, bool(subs)

    def _space_normalization(self, text):
        text = normalize_space(text, preserve=['\n'])
        subs_all = []
        text, subs = self.punc_space_pattern.subn('\\2', text)
        subs_all.append(subs)
        text = self.zero_width_space_pattern.sub('', text)
        subs_all.append(subs)
        text = self.punc_no_space_pattern.sub('\\1\\2 \\3', text)
        subs_all.append(subs)
        text = self.quote_no_space_pattern1.sub('\\1 \\2\\3\\5', text)
        subs_all.append(subs)
        text = self.quote_no_space_pattern2.sub('\\1\\2\\4 \\5', text)
        subs_all.append(subs)
        return text, any(subs_all)

    def _seg_sentences(self, text):
        subs_all = []
        text, subs = self.final_sentence_pattern1.subfn("{1}{2}{3}\n{4}{5}{6}", text)
        subs_all.append(subs)
        text, subs = self.final_sentence_pattern2.subfn("{1}{2}{3}\n{4}{5}{6}{7}", text)
        subs_all.append(subs)
        return text, any(subs_all)

    def _replace_urls(self, text):
        replace = ' [URL] '
        text, subs = self.urls_pattern2.subn(replace, self.urls_pattern.sub(replace, text))
        return text, bool(subs)

    def _build_filters(self):
        # The regex includes citations placed after periods that may prevent the correct sentence splitting
        if self.remove_citations:
            self.remove_citations_pattern = re.compile(r'[,.]*\[[\d]{,3}\]')
        if self.language_normalization:
            self.geminate_l_pattern = re.compile(r'l\.l')
        # https://www.tutorialspoint.com/Extracting-email-addresses-using-regular-expressions-in-Python
        if self.replace_emails:
            self.emails_pattern = re.compile(
                rf'[{self.lang_chars}0-9_.+-]+@[a-zA-Z0-9-]+\.[a-z0-9-.]+')
            # allows language specific characters in the first part of the email
        # https://stackoverflow.com/questions/8376691/how-to-remove-hashtag-user-link-of-a-tweet-using-regular-expression
        if self.remove_hashtags_mentions:
            self.remove_hashtags_pattern = re.compile('(@[A-Za-z0-9_]+)|(#[\w_]+)')
        if self.remove_tags:
            self.tags_pattern = re.compile(' *(<.*?> ?)+ *')
            self.p_tags_pattern = re.compile('(\s*)(<p>)+')
        if self.replace_urls:
            # slightly modified from:
            # https://stackoverflow.com/questions/6718633/python-regular-expression-again-match-url
            self.urls_pattern = re.compile(
                rf'\((@)?((http|https)://)?([{self.lang_chars}0-9./?\\\\@\-—_=#])+\.[a-z]{{2,6}}([{self.lang_chars}0-9&/\\\\+~*?%:!@—_=#()-])*')
            self.urls_pattern2 = re.compile('(\[URL\]\.?\w*\s*)+')
        if self.char_length_filter_document > 0:
            self.filters.append(self._filter_by_char_len)
        if self.head_filter:
            self.filters.append(self._filter_by_heads)
        if self.digits_filter > 0:
            self.filters.append(self._filter_by_digits)
        if self.alphanum_filter > 0:
            self.filters.append(self._filter_by_alphanum)
        if self.lang_chars_filter > 0:
            self.filters.append(self._filter_by_lang_chars)
        if self.uppercase_filter > 0:
            self.filters.append(self._filter_by_uppercase)
        if self.alphabet_filter is not None:
            self.ad = AlphabetDetector()
            self.filters.append(self._filter_by_alphabet)
        if self.lang_filter is not None and self.lang_filter_document:
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
        if self.space_normalization is not None:
            self.punc_no_space_pattern = re.compile("(\w+|\"|')([!,:;?])([a-zA-Z]\w)")
            if self.lang_filter == ['ca']:
                self.punc_space_pattern = re.compile("(\s)([!,:;?.])")
                self.quote_no_space_pattern1 = re.compile("(\w)([«“\"])(\w+(\s\w+)*)([\"”»])")
                self.quote_no_space_pattern2 = re.compile("([«“\"])(\w+(\s\w+)*)([\"”»])(\w+)")
            else:
                self.punc_space_pattern = re.compile("(\s)([!',:;?.])")
                self.quote_no_space_pattern1 = re.compile("(\w)([«“'\"])(\w+(\s\w+)*)(['\"”»])")
                self.quote_no_space_pattern2 = re.compile("([«“'\"])(\w+(\s\w+)*)(['\"”»])(\w+)")
            self.zero_width_space_pattern = re.compile('\u200b')
        if self.seg_sentences:
            self.final_sentence_pattern1 = regex.compile(r"(\s)(\p{Ll}+)([.!?:]*)(\p{Lu})(\p{Ll}+)([\s.,;:?!])")
            self.final_sentence_pattern2 = regex.compile(r"(\s)(\p{Ll}+)([.!?:]+)('|\")(\p{Lu})(\p{Ll}+)([\s.,;:?!])")

    @debug_filter
    def _filter_by_char_len(self, doc: Document):
        value = len(doc.content)
        if value < self.char_length_filter_document:
            return False, round(value, 2)
        return True, None

    @debug_filter
    def _filter_by_heads(self, doc: Document):
        value = []
        if doc.heads is not None:
            for token in ['found', '404', 'robots.txt', 'error', 'trouvée']:
                if re.search(token, doc.heads, re.IGNORECASE):
                    value.append(token)
                    return False, value
        return True, None

    @debug_filter
    def _filter_by_digits(self, doc: Document):
        value = sum(c.isdigit() for c in doc.content) / len(doc.content)
        if value > self.digits_filter:
            return False, round(value, 2)
        return True, None

    @debug_filter
    def _filter_by_alphanum(self, doc: Document):
        concat_content = ''.join(doc.content.split())
        value = (1 - (sum(c.isalnum() for c in concat_content) / len(concat_content)))
        if value > self.alphanum_filter:
            return False, round(value, 2)
        return True, None

    @debug_filter
    def _filter_by_lang_chars(self, doc: Document):
        concat_content = ''.join(doc.content.split())
        value = (1 - (sum(c in self.alphabet for c in concat_content) / len(concat_content)))
        if value > self.lang_chars_filter:
            return False, round(value, 2)
        return True, None

    @debug_filter
    def _filter_by_uppercase(self, doc: Document):
        value = sum(c.isupper() for c in doc.content) / len(doc.content)
        if value > self.uppercase_filter:
            return False, round(value, 2)
        return True, None

    @debug_filter
    def _filter_by_alphabet(self, doc: Document):
        # TODO: Check thresholds?
        try:
            value = len(self.ad.detect_alphabet(doc.content).intersection(set(self.alphabet_filter)))
            if value == 0:
                return False, value
        except:
            return True, None
        return True, None

    @debug_filter
    def _filter_by_lang(self, doc: Document):
        content = self.url_placeholder_pattern.sub('', doc.content)
        content = self.no_eols_pattern.sub('. ', content)
        res = self.fasttext_lid.predict(content)
        lang = res[0][0][-2:]
        conf = res[1][0]
        if lang in self.lang_filter and conf > self.initial_lang_filter_threshold:
            doc.language = lang
            return True, None
        value = f"({round(conf, 2)}, {lang})"
        return False, value

    @debug_filter
    def _filter_by_dict(self, doc: Document):
        if self.dictionary_filter_pattern.search(doc.content):
            return False, None
        return True, None

    def _filter(self, document: Optional[Document]) -> Optional[Document]:
        # TODO: 1. implement replace functions that receives as input the Document
        #       2. implement a decorator for the replace functions like the decorator for filters
        if self.language_normalization:
            document.content, subs = self._language_normalization(self.lang_filter, document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._language_normalization.__name__}")
        if self.replace_emails:
            document.content, subs = self._replace_emails(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._replace_emails.__name__}")
        if self.remove_hashtags_mentions:
            document.content, subs = self._remove_hashtags_mentions(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._remove_hashtags_mentions.__name__}")
        if self.remove_tags:
            document.content, subs = self._remove_tags(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._remove_tags.__name__}")
        if self.replace_urls:
            document.content, subs = self._replace_urls(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._replace_urls.__name__}")
        if self.space_normalization:
            document.content, subs = self._space_normalization(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._space_normalization.__name__}")
        if self.seg_sentences:
            document.content, subs = self._seg_sentences(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._seg_sentences.__name__}")
        if self.remove_citations:
            document.content, subs = self._remove_citations(document.content)
            if self.debug and subs:
                document.operations.append(f"{self.__class__.__name__}-{self._remove_citations.__name__}")

        if len(document.content.split()) == 0:
            return None

        keep = True
        for filter_ in self.filters:
            keep, _ = filter_(document)
            if not keep:
                break
        if keep or self.debug:
            return document
        return None

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._filter(document)

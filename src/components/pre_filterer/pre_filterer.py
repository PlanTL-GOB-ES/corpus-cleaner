from typing import Union, Tuple, List
from typing import Iterable
from document import Document
import re
from alphabet_detector import AlphabetDetector
from langid.langid import LanguageIdentifier, model
from components.cleaner_component import CleanerComponent
import argparse
# TODO: Check whether in pre-filtering or later on:  from profanity_check import predict, predict_prob


class PreFilterer(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--no-remove-tags', action='store_true', help='Avoid removing XML/HTML tags')
        parser.add_argument('--char-length-filter', type=int, help='Minimum char length per document. Set to 0 not'
                                                                   'to apply any filter.', default=40)
        parser.add_argument('--no-head-filter', action='store_true', help='Avoid filtering documents coming from'
                            'a crawler (having a "heads" attribute) with common HTTP errors.')
        parser.add_argument('--digits_filter', type=float, help='Maximum allowed proportion of digit characters',
                            default=0.1)
        parser.add_argument('--alphanum_filter', type=float, help='Maximum allowed proportion of non-alphanumeric'
                                                                  'characters', default=0.05)
        parser.add_argument('--uppercase_filter', type=float, help='Maximum allowed proportion of uppercase characters',
                            default=0.4)
        parser.add_argument('--alphabet-filter', type=str, help='Alphabets that should be present (eg. LATIN)',
                            nargs='+', default=['LATIN'])
        parser.add_argument('--lang-filter', type=str, help='Languages that should be present (eg. es)',
                            nargs='+', default=['es'])
        parser.add_argument('--lang-filter-threshold', type=float, help='If --lang-filter is set, minimum threshold',
                            default=0.95)
        parser.add_argument('--dictionary_filter', type=str, help='Path to dictionary (plain text, one term per line'
                            'of terms that should not appear', default=None)

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, no_remove_tags: bool = True, char_length_filter: int = 40, no_head_filter: bool = False,
                 digits_filter: float = 0.1, alphanum_filter: float = 0.05, uppercase_filter: float = 0.4,
                 alphabet_filter: Union[Tuple[str], None] = ('LATIN',), lang_filter: Union[Tuple[str], None] = ('es',),
                 lang_filter_threshold: float = 0.95, dictionary_filter: Union[None, List[str]] = None, **kwargs):
        self.remove_tags = not no_remove_tags
        self.tags_pattern = None
        self.char_length_filter = char_length_filter
        self.head_filter = not no_head_filter
        self.digits_filter = digits_filter
        self.alphanum_filter = alphanum_filter
        self.uppercase_filter = uppercase_filter
        self.alphabet_filter = alphabet_filter
        self.lang_filter = lang_filter
        self.lang_id = None
        self.lang_filter_threshold = lang_filter_threshold
        self.dictionary_filter = dictionary_filter
        self.dictionary_filter_pattern = None
        self.filters = []
        self._build_filters()

    def _remove_tags(self, text):
        return re.sub(self.tags_pattern, '', text)

    def _build_filters(self):
        if self.remove_tags:
            self.tags_pattern = re.compile('<.*?>')
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
            self.lang_id = LanguageIdentifier.from_modelstring(model, norm_probs=True)
            self.filters.append(self._filter_by_lang)
        if self.dictionary_filter is not None:
            self.dictionary_filter_pattern = re.compile("|".join(self.dictionary_filter))
            self.filters.append(self._filter_by_dict)

    def _filter_by_length(self, doc: Document):
        if len(doc.content) < self.char_length_filter:
            return False
        return True

    def _filter_by_heads(self, doc: Document):
        if doc.heads is not None:
            for token in ['found', '404', 'robots.txt', 'error']:
                if re.search(token, doc.heads, re.IGNORECASE):
                    return False
        return True

    def _filter_by_digits(self, doc: Document):
        if sum(c.isdigit() for c in doc.content)/len(doc.content) > self.digits_filter:
            return False
        return True

    def _filter_by_alphanum(self, doc: Document):
        if (1 - (sum(c.isalnum() for c in doc.content)/len(doc.content))) > self.alphanum_filter:
            return False
        return True

    def _filter_by_uppercase(self, doc: Document):
        if sum(c.isupper() for c in doc.content)/len(doc.content) > self.uppercase_filter:
            return False
        return True

    def _filter_by_alphabet(self, doc: Document):
        # TODO: Check thresholds?
        if len(self.ad.detect_alphabet(doc.content).intersection(set(self.alphabet_filter))) == 0:
            return False
        return True

    def _filter_by_lang(self, doc: Document):
        res = self.lang_id.classify(doc.content)
        if res[0] in self.lang_filter and res[1] > self.lang_filter_threshold:
            doc.language = res[0]
            return True
        return False

    def _filter_by_dict(self, doc: Document):
        if self.dictionary_filter_pattern.search(doc.content):
            return False
        return True

    def _filter(self, documents: Iterable[Document]):
        i = 0
        for doc in documents:
            print(i)
            i += 1
            keep = True
            for filter_ in self.filters:
                if self.remove_tags:
                    doc.content = self._remove_tags(doc.content)
                keep = filter_(doc)
                if not keep:
                    break
            if keep:
                yield doc

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._filter(documents)


def test():
    from components.data_parser.bsc_crawl_json_parser import BSCCrawlJSONParser
    from components.data_parser.wikipedia_parser import WikipediaParser
    from components.encoding_fixer.encoding_fixer import EncodingFixer
    import os
    # file_dir = os.path.join('..', '..', '..', 'test', 'bne')
    # parser = BSCCrawlJSONParser(file_dir)
    # documents = parser.parse()
    # encoding = EncodingFixer()
    # documents = encoding.fix_encoding(documents)
    # pre_filter = PreFilterer()
    # documents = pre_filter.filter(documents)
    #
    # # Show the first document
    # for idx, doc in enumerate(documents):
    #     print(f'DOC {idx}: {doc.content}\n')
    #     if idx == 1:
    #         break

    file_dir = os.path.join('..', '..', '..', 'test', 'wiki')
    parser = WikipediaParser(file_dir)
    documents = parser.parse()
    for doc in documents:
        documents = [doc]
        break
    #documents = [list(documents)[0]]
    encoding = EncodingFixer()
    documents = encoding.fix_encoding(documents)
    pre_filter = PreFilterer(lang_filter=None)
    documents = pre_filter.filter(documents)

    # Show the first document
    for idx, doc in enumerate(documents):
        print(f'DOC {idx}: {doc.content}\n')
        if idx == 1:
            break


if __name__ == '__main__':
    test()

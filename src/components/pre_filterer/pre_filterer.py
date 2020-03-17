from typing import Union, Tuple, List
from typing import Iterable
from document import Document
import re
from alphabet_detector import AlphabetDetector
from langid.langid import LanguageIdentifier
# TODO: Check whether in pre-filtering or later on:  from profanity_check import predict, predict_prob


class PreFilterer:
    def __init__(self, remove_tags: bool = True, length_filter: int = 40, head_filter: bool = True,
                 digits_filter: float = 0.1, alphanum_filter: float = 0.05, uppercase_filter: float = 0.4,
                 alphabet_filter: Union[Tuple[str], None] = ('LATIN',), lang_filter: Union[Tuple[str], None] = ('es',),
                 lang_filter_threshold: float = 0.95, dictionary_filter: Union[None, List[str]] = None):
        self.remove_tags = remove_tags
        self.tags_pattern = None
        self.length_filter = length_filter
        self.head_filter = head_filter
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
        if self.length_filter > 0:
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
        if len(doc.content < self.length_filter):
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

    def filter(self, documents: Iterable[Document]):
        for doc in documents:
            keep = True
            for filter_ in self.filters:
                if self.remove_tags:
                    doc.content = self._remove_tags(doc.content)
                keep = filter_(doc)
                if not keep:
                    break
            if keep:
                yield doc

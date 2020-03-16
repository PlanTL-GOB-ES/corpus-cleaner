from typing import Union, Set
from typing import Iterable
from document import Document
import re


class PreFilterer:
    def __init__(self, length_filter: int = 10, head_filter: bool = True, lang_filter: Union[Set[str], None] = None,
                 dictionary_filter: Union[None, Set[str]] = None):
        self.length_filter = length_filter
        self.head_filter = head_filter
        self.lang_filter = lang_filter
        self.dictionary_filter = dictionary_filter
        self.filters = []
        self._build_filters()

    def _build_filters(self):
        if self.length_filter > 0:
            self.filters.append(self._filter_by_length)
        if self.head_filter:
            self.filters.append(self._filter_by_heads)
        if self.lang_filter is not None:
            self.filters.append(self._filter_by_lang)
        if self.dictionary_filter is not None:
            self.filters.append(self._filter_by_dict)
            self._compile_dict()

    def _compile_dict(self):
        pass

    def _filter_by_length(self, doc: Document):
        if len(doc.content < self.length_filter):
            return False
        return True

    def _filter_by_heads(self, doc: Document):
        pass

    def _filter_by_lang(self, doc: Document):
        pass

    def _filter_by_dict(self, doc: Document):
        pass

    def filter(self, documents: Iterable[Document]):
        for doc in documents:
            keep = True
            for filter_ in self.filters:
                keep = filter_(doc)
                if not keep:
                    break
            if keep:
                yield doc

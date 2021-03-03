from . import DataParser
from corpus_cleaner.document import Document
from typing import Iterable, Tuple


class DataParserMapper:
    def __init__(self, data_parser: DataParser):
        self._data_parser = data_parser

    def __call__(self, path: Tuple[int, str]) -> Iterable[Document]:
        idx, path = path
        return self._data_parser.treat_file(idx, path)


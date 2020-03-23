from typing import Iterable
from document import Document
from chardet.universaldetector import UniversalDetector  # TODO: Try UnicodeDammit, Magic...?
from typing import TextIO
import os
from typing import List
from pathlib import Path
from components.cleaner_component import CleanerComponent
import argparse
from typing import Union, Iterable

class DataParser(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--extensions', type=str, help='File extensions to work with (eg. json)', nargs='+')
        parser.add_argument('--encoding', type=str, help='Input encoding format (eg. utf-8. If set to auto, the program'
                                                         'tries to guess the encoding', default='auto')
        parser.add_argument('--encoding-threshold', type=float, help='Encoding threshold if --encoding auto (ignored'
                            'otherwise. If the encoding detector is not above this threshold, it assigns utf-8.')
        parser.add_argument('--encoding-error-policy', type=str, help='Encoding error policy (same options as open()',
                            default='ignore')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, path: str, extensions: List[str], encoding: str = 'auto', encoding_threshold: float = 0.9,
                 encoding_error_policy: str = 'ignore', **kwargs):
        self.path = path
        self.extensions = extensions
        self.encoding = encoding
        self.encoding_threshold = encoding_threshold  # TODO: Revisit default*
        self.encoding_error_policy = encoding_error_policy  # TODO: Revisit default

    def _parse(self) -> Iterable[Document]:
        doc_counter = 0
        for idx_filepath, relative_filepath in enumerate(sorted(self._get_relative_filepaths())):
            abs_path = os.path.join(self.path, relative_filepath)
            enc = self._guess_encoding(abs_path) if self.encoding == 'auto' else self.encoding
            with open(abs_path, 'r', encoding=enc, errors=self.encoding_error_policy) as f:
                for doc in self._parse_file(f, relative_filepath, doc_counter):
                    if enc != 'utf-8':
                        pass  # TODO: Check possible problems when the original file was not utf-8
                    yield doc
                    doc_counter += 1

    def _parse_file(self, fd: TextIO, relative_filepath: str, doc_counter: int) -> Iterable[Document]:
        raise NotImplementedError()

    def _get_relative_filepaths(self) -> Iterable[str]:
        relative_paths = []
        for extension in self.extensions:
            for path in Path(self.path).rglob(extension):
                if os.path.isfile(path):
                    relative_paths.append(os.path.join(os.path.relpath(path.parents[0], self.path), path.name))
        return relative_paths

    def _guess_encoding(self, path: str):
        # https://stackoverflow.com/questions/46037058/using-chardet-to-find-encoding-of-very-large-file/49621821
        detector = UniversalDetector()
        detector.reset()
        with open(path, 'rb') as f:
            for row in f:
                detector.feed(row)
                if detector.done:
                    break
        detector.close()
        encoding = detector.result['encoding'] if detector.result['confidence'] > self.encoding_threshold else 'utf-8'
        return encoding

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document],
                                                                         Iterable[Iterable[Document], None]]:
        return self._parse()


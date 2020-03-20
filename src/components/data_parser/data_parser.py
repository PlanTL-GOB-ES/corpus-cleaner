from typing import Iterable
from document import Document
from chardet.universaldetector import UniversalDetector  # TODO: Try UnicodeDammit, Magic...?
from typing import TextIO
import os
from typing import List
from pathlib import Path
from components.cleaner_component import CleanerComponent
import argparse


class DataParser(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError

    def __init__(self, path: str, extensions: List[str], encoding: str = 'auto', encoding_threshold: float = 0.9,
                 error_policy: str = 'ignore'):
        self.path = path
        self.extensions = extensions
        self.encoding = encoding
        self.encoding_threshold = encoding_threshold  # TODO: Revisit default*
        self.error_policy = error_policy  # TODO: Revisit default

    def parse(self) -> Iterable[Document]:
        doc_counter = 0
        for idx_filepath, relative_filepath in enumerate(sorted(self._get_relative_filepaths())):
            abs_path = os.path.join(self.path, relative_filepath)
            enc = self._guess_encoding(abs_path) if self.encoding == 'auto' else self.encoding
            with open(abs_path, 'r', encoding=enc, errors='ignore') as f:
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


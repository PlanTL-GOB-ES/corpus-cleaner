from corpus_cleaner.document import Document
from chardet.universaldetector import UniversalDetector  # TODO: Try UnicodeDammit, Magic...?
from typing import TextIO
import os
from typing import Tuple
from pathlib import Path
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse
from typing import Iterable, List, Optional


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

    def __init__(self, args: argparse.Namespace, input_path: Optional[str] = None,
                 extensions: Optional[Tuple[str]] = None,
                 encoding: str = 'auto', encoding_threshold: float = 0.9, encoding_error_policy: str = 'ignore'):
        # TODO: Revisit defaults
        super().__init__(args)
        self.input_path = input_path if input_path is not None else args.input_path
        self.extensions = extensions if extensions is not None else args.extensions
        self.encoding = args.encoding if args.encoding is not None else encoding
        self.encoding_threshold = args.encoding_threshold if args.encoding_threshold is not None else encoding_threshold
        self.encoding_error_policy = args.encoding_error_policy if args.encoding_error_policy is not None else \
            encoding_error_policy
        self.detector = UniversalDetector() if self.encoding == 'auto' else None
        self.info = []
        self.logger = args.logger

    def _treat_file(self, idx_filepath: int, relative_filepath: str) -> Iterable[Document]:
        abs_path = os.path.join(self.input_path, relative_filepath)
        enc, confidence_ok = self._guess_encoding(abs_path) if self.encoding == 'auto' else (self.encoding, True)
        with open(abs_path, 'r', encoding=enc, errors=self.encoding_error_policy) as f:
            for doc in self._parse_file(f, relative_filepath, idx_filepath):
                if enc != 'utf-8':
                    pass  # TODO: Check possible problems when the original file was not utf-8
                yield doc

    def _parse(self) -> List[Iterable[Document]]:
        parse_iterables = []
        for idx_filepath, relative_filepath in enumerate(sorted(self._get_relative_filepaths())):
            parse_iterables.append(self._treat_file(idx_filepath, relative_filepath))
        return parse_iterables

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) ->\
            List[Iterable[Document]]:
        raise NotImplementedError()

    def _get_relative_filepaths(self) -> Iterable[str]:
        self.logger.logger.info('Getting relative filepaths')
        relative_paths = []
        for extension in self.extensions:
            for path in Path(self.input_path).rglob(f'*{extension}' if '*' not in extension else extension):
                if os.path.isfile(path):
                    relative_paths.append(os.path.join(os.path.relpath(path.parents[0], self.input_path), path.name))
        return relative_paths

    def _guess_encoding(self, path: str):
        # https://stackoverflow.com/questions/46037058/using-chardet-to-find-encoding-of-very-large-file/49621821
        self.detector.reset()
        with open(path, 'rb') as f:
            for row in f:
                self.detector.feed(row)
                if self.detector.done:
                    break
        self.detector.close()
        confidence_ok = self.detector.result['confidence'] > self.encoding_threshold
        encoding = self.detector.result['encoding'] if confidence_ok else 'utf-8'
        return encoding, confidence_ok

    def parse(self) -> List[Iterable[Document]]:
        return self._parse()



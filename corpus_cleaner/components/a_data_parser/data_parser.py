from corpus_cleaner.document import Document
from chardet.universaldetector import UniversalDetector  # TODO: Try UnicodeDammit, Magic...?
from typing import TextIO, BinaryIO
import os
from typing import Tuple
import glob
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse
from typing import Iterable, List, Optional
import gzip
from urllib.parse import urlparse
import re
from typing import Dict
import time

TIMEOUT_ENCODING_GUESSING = 5.0


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
        parser.add_argument('--url-doc', type=str, help='Path to a url list (plain text, one url per line)'
                                                        'that should be filtered and processed', default=None)
        parser.add_argument('--warc-warn', action='store_true', help='Enable warnings of WARC parser')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        if args.url_doc is not None and args.input_format not in ['bsc-crawl-json', 'warc']:
            raise RuntimeError('--url-doc can only be used with --input-format bsc-crawl-json or warc')

    def __init__(self, args: argparse.Namespace, input_path: Optional[str] = None,
                 extensions: Optional[Tuple[str]] = None,
                 encoding: str = 'auto', encoding_threshold: float = 0.9, encoding_error_policy: str = 'ignore',
                 bytes_: bool = False, url_filter: Optional[str] = None, done_paths: Iterable[str] = ()):
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
        self.bytes = bytes_
        self.url_filter = args.url_doc if args.url_doc is not None else url_filter
        if self.url_filter is not None:
            with open(self.url_filter, 'r') as f:
                self.url_filter = [re.sub("www\.", '', line.strip()) for line in f.readlines()]
                for idx, url in enumerate(self.url_filter):
                    if len(re.findall("\w://", url)) == 0:
                        self.url_filter[idx] = 'http://' + url
                self.url_filter = [urlparse(url) for url in self.url_filter]
        self.done_paths = set(done_paths)

    def _check_url(self, url: str) -> bool:
        def url_belongs_to(u1, u2):
            if u1.hostname != u2.hostname:
                return False
            u1_path = u1.path.split('/')
            u2_path = u2.path.split('/')
            if len(u2_path) == 0:
                return True
            i = 0
            while i < len(u2_path):
                if i >= len(u1_path):
                    return False
                if u1_path[i] != u2_path[i]:
                    return False
                i += 1
            return True

        if len(re.findall("\w://", url)) == 0:
            url = 'http://' + url
        url = urlparse(re.sub("www\.", '', url))
        for url_to_keep in self.url_filter:
            if url_belongs_to(url, url_to_keep):
                return True
        return False

    def _treat_file(self, idx_filepath: int, relative_filepath: str) -> Iterable[Document]:
        abs_path = os.path.join(relative_filepath)
        if self.bytes:
            with open(abs_path, 'rb') as f:
                for idx, doc in enumerate(self._parse_binary_file(f, relative_filepath, idx_filepath)):
                    if self.url_filter is not None:
                        url = doc.url
                        if self._check_url(url):
                            yield doc
                    else:
                        yield doc
        else:
            gz = False
            extension = os.path.splitext(relative_filepath)[1][1:].strip()
            if extension == 'gz':
                gz = True
            enc, confidence_ok = self._guess_encoding(abs_path, gz=gz) if self.encoding == 'auto' else (self.encoding,
                                                                                                        True)
            if not gz:
                with open(abs_path, 'r', encoding=enc, errors=self.encoding_error_policy) as f:
                    for idx, doc in enumerate(self._parse_file(f, relative_filepath, idx_filepath)):
                        if enc != 'utf-8':
                            pass  # TODO: Check possible problems when the original file was not utf-8
                        yield doc
            else:
                with gzip.open(abs_path, 'rt', encoding=enc, errors=self.encoding_error_policy) as f:
                    for idx, doc in enumerate(self._parse_file(f, relative_filepath, idx_filepath)):
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

    def _parse_binary_file(self, fd: BinaryIO, relative_filepath: str, idx_filepath: int) ->\
            List[Iterable[Document]]:
        pass

    def _get_relative_filepaths(self) -> Iterable[str]:
        self.logger.logger.info('Getting relative filepaths')
        relative_paths = []
        for extension in self.extensions:
            for path in glob.glob(
                    os.path.join(self.input_path, '**', f'*{extension}' if '*' not in extension else extension),
                    recursive=True):
                if os.path.isfile(path) and path not in self.done_paths:
                    relative_paths.append(path)
        return sorted(relative_paths)

    def _guess_encoding(self, path: str, gz: bool):
        # https://stackoverflow.com/questions/46037058/using-chardet-to-find-encoding-of-very-large-file/49621821
        self.detector.reset()
        t0 = time.process_time()
        timeout = False
        if not gz:
            with open(path, 'rb') as f:
                for row in f:
                    self.detector.feed(row)
                    if self.detector.done :
                        break
                    t1 = time.process_time()
                    if t1 - t0 > TIMEOUT_ENCODING_GUESSING:
                        timeout = True
                        break
        else:
            with gzip.open(path, 'rb') as f:
                for row in f:
                    self.detector.feed(row)
                    if self.detector.done:
                        break
                    t1 = time.process_time()
                    if t1 - t0 > TIMEOUT_ENCODING_GUESSING:
                        timeout = True
                        break
        self.detector.close()
        if timeout:
            encoding = 'utf-8'
            confidence_ok = 0.0
        else:
            confidence_ok = self.detector.result['confidence'] > self.encoding_threshold
            encoding = self.detector.result['encoding'] if confidence_ok else 'utf-8'
        return encoding, confidence_ok

    def parse(self) -> List[Iterable[Document]]:
        return self._parse()

    def treat_file(self, idx_filepath: int, relative_filepath: str) -> Iterable[Document]:
        return self._treat_file(idx_filepath, relative_filepath)

    def get_idx_relative_filepaths(self) -> List[Tuple[int, str]]:
        return list(enumerate(self._get_relative_filepaths()))
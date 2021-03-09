from corpus_cleaner.document import Document
from chardet.universaldetector import UniversalDetector  # TODO: Try UnicodeDammit, Magic...?
from typing import TextIO, BinaryIO
import os
from typing import Tuple
import glob
from typing import Iterable, Optional
import gzip
from urllib.parse import urlparse
import re
import time
from dataclasses import dataclass
from typing import List
from corpus_cleaner.par_utils.par_utils import PipelineLogger


@dataclass
class DataParserConfig:
    input_path: str  # Directory path of the input data.
    input_format: str  # Input data format
    extensions: Tuple[str] = ('*',)  # File extensions to work with (eg. json).
    encoding_threshold: float = 0.9  # Encoding threshold if --encoding auto (ignored otherwise. If the encoding
    # detector is not above this threshold, it assigns utf-8.
    encoding: str = 'auto'  # Input encoding format (eg. utf-8. If set to auto, the program tries to guess the
    # encoding).
    encoding_error_policy: str = 'ignore'  # Encoding error policy (same options as open()).
    url_doc: Optional[str] = None  # Path to a url list (plain text, one url per line) that should be filtered and
    # processed'.
    warc_warn: bool = False  # Enable warnings of WARC parser.
    bytes_: bool = False  # Whether input is compressed (GZIP).
    done_paths: Iterable[str] = ()  # Already preprocessed paths (for checkpointing).
    timeout_encoding_guessing: int = 5.0  # Timeout for encoding guessing (otherwise, UTF-8).
    input_lang: Optional[str] = None  # Assume that input is in a given language (e.g., if we know fore sure that all
    # input is in Spanish).


class DataParser:
    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None):
        self._config = config
        if self._config.url_doc is not None:
            self._url_filter = self._config.url_doc
            with open(self._config.url_doc, 'r') as f:
                self._url_filter = [re.sub("www\.", '', line.strip()) for line in f.readlines()]
                for idx, url in enumerate(self._url_filter):
                    if len(re.findall("\w://", url)) == 0:
                        self._url_filter[idx] = 'http://' + url
                self._url_filter = [urlparse(url) for url in self._url_filter]
        self._done_paths = set(self._config.done_paths)
        self._detector = UniversalDetector() if self._config.encoding == 'auto' else None
        self._logger = logger

    def _log(self, text: str):
        if self._logger is None:
            raise RuntimeError("Logger is not defined in DataParser")
        self._logger.logger.info(text)

    def _warn(self, text: str):
        if self._logger is None:
            raise RuntimeError("Logger is not defined in DataParser")
        self._logger.logger.warning(text)

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
        for url_to_keep in self._url_filter:
            if url_belongs_to(url, url_to_keep):
                return True
        return False

    def _treat_file(self, idx_filepath: int, relative_filepath: str) -> Iterable[Document]:
        abs_path = os.path.join(relative_filepath)
        if self._config.bytes_:
            with open(abs_path, 'rb') as f:
                for idx, doc in enumerate(self._parse_binary_file(f, relative_filepath, idx_filepath)):
                    if self._url_filter is not None:
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
            enc, confidence_ok = self._guess_encoding(abs_path, gz=gz) if self._config.encoding == 'auto' else \
                (self._config.encoding, True)
            if not gz:
                with open(abs_path, 'r', encoding=enc, errors=self._config.encoding_error_policy) as f:
                    for idx, doc in enumerate(self._parse_file(f, relative_filepath, idx_filepath)):
                        if enc != 'utf-8':
                            pass  # TODO: Check possible problems when the original file was not utf-8
                        yield doc
            else:
                with gzip.open(abs_path, 'rt', encoding=enc, errors=self._config.encoding_error_policy) as f:
                    for idx, doc in enumerate(self._parse_file(f, relative_filepath, idx_filepath)):
                        if enc != 'utf-8':
                            pass  # TODO: Check possible problems when the original file was not utf-8
                        yield doc

    def _parse(self) -> List[Iterable[Document]]:
        parse_iterables = []
        for idx_filepath, relative_filepath in enumerate(sorted(self._get_relative_filepaths())):
            parse_iterables.append(self._treat_file(idx_filepath, relative_filepath))
        return parse_iterables

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> \
            List[Iterable[Document]]:
        raise NotImplementedError

    def _parse_binary_file(self, fd: BinaryIO, relative_filepath: str, idx_filepath: int) -> \
            List[Iterable[Document]]:
        raise NotImplementedError

    def _get_relative_filepaths(self) -> Iterable[str]:
        self._log('Getting relative filepaths')
        relative_paths = []
        for extension in self._config.extensions:
            for path in glob.glob(
                    os.path.join(self._config.input_path, '**', f'*{extension}' if '*' not in extension else extension),
                    recursive=True):
                if os.path.isfile(path) and path not in self._config.done_paths:
                    relative_paths.append(path)
        return sorted(relative_paths)

    def _guess_encoding(self, path: str, gz: bool):
        # https://stackoverflow.com/questions/46037058/using-chardet-to-find-encoding-of-very-large-file/49621821
        self._detector.reset()
        t0 = time.process_time()
        timeout = False
        if not gz:
            with open(path, 'rb') as f:
                for row in f:
                    self._detector.feed(row)
                    if self._detector.done:
                        break
                    t1 = time.process_time()
                    if t1 - t0 > self._config.timeout_encoding_guessing:
                        timeout = True
                        break
        else:
            with gzip.open(path, 'rb') as f:
                for row in f:
                    self._detector.feed(row)
                    if self._detector.done:
                        break
                    t1 = time.process_time()
                    if t1 - t0 > self._config.timeout_encoding_guessing:
                        timeout = True
                        break
        self._detector.close()
        if timeout:
            encoding = 'utf-8'
            confidence_ok = 0.0
        else:
            confidence_ok = self._detector.result['confidence'] > self._config.encoding_threshold
            encoding = self._detector.result['encoding'] if confidence_ok else 'utf-8'
        return encoding, confidence_ok

    def parse(self) -> List[Iterable[Document]]:
        return self._parse()

    def treat_file(self, idx_filepath: int, relative_filepath: str) -> Iterable[Document]:
        return self._treat_file(idx_filepath, relative_filepath)

    def get_idx_relative_filepaths(self) -> List[Tuple[int, str]]:
        return list(enumerate(self._get_relative_filepaths()))

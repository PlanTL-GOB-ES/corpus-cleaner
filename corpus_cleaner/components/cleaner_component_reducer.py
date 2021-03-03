import argparse
from abc import ABC

from corpus_cleaner.document import Document
from . import CleanerComponent
from .i_output_formatter import OutputFormatterFactory
from .a_data_parser import DataParserFactory
from .a_data_parser.data_parser import DataParserConfig
from typing import List, Optional
import os
import subprocess
from typing import Tuple
from corpus_cleaner.components.cleaner_component import CleanerComponent, LegacyCleanerComponent, CleanerComponentConfig


class ReduceConfig:
    format_: str
    tmp_file: str
    final_path: str
    input_path: Optional[str]
    extensions: Tuple[str]


class LegacyCleanerComponentReducer(LegacyCleanerComponent):
    def __init__(self, args: argparse.Namespace, format_: str, tmp_file: str, final_path: str,
                 input_path: Optional[str], extensions: Tuple[str]):
        super().__init__(args)
        self.format = format_
        self.tmp_file = tmp_file
        self.final_path = final_path

        self.data_parser = DataParserFactory.get_parser(args, input_format=self.format, input_path=input_path,
                                                        extensions=extensions)

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

    def _reduce(self):
        raise NotImplementedError()

    def reduce(self):
        self._reduce()

    def get_documents(self):
        return self.data_parser.parse()

    def output(self, documents: List[Document]):
        # self.logger.info('Outputting...')
        output_formatter = OutputFormatterFactory.get_output_formatter(self.args, self.format, self.tmp_file)
        output_formatter.apply(documents)


class CleanerComponentReducer(CleanerComponent, ABC):
    def __init__(self, config: CleanerComponentConfig, reduce_config: ReduceConfig):
        input_path: str  # Directory path of the input data.
        extensions: List[str]  # File extensions to work with (eg. json).
        encoding_threshold: float  # Encoding threshold if --encoding auto (ignored otherwise. If the encoding detector is
        # not above this threshold, it assigns utf-8.
        encoding: str = 'auto'  # Input encoding format (eg. utf-8. If set to auto, the program tries to guess the
        # encoding).
        encoding_error_policy: str = float  # Encoding error policy (same options as open()).
        url_doc: Optional[str] = None  # Path to a url list (plain text, one url per line) that should be filtered and
        # processed'.
        warc_warn: bool = False  # Enable warnings of WARC parser.
        bytes_: bool = False  # Whether input is compressed (GZIP).
        done_paths: Iterable[str] = ()  # Already preprocessed paths (for checkpointing).
        timeout_encoding_guessing: int = 5.0  # Timeout for encoding guessing (otherwise, UTF-8).
        input_lang: Optional[
            str] = None  # Assume that input is in a given language (e.g., if we know fore sure that all
        # input is in Spanish).

        data_parser_config = DataParserConfig(input_path=reduce_config.input_path, extensions=reduce_config.input_path,
                                              extensions=reduce_config.extensions)
        self._data_parser = DataParserFactory.get_parser(input_format=data_parser_config)

    def _reduce(self):
        raise NotImplementedError()

    def reduce(self):
        self._reduce()

    def get_documents(self):
        return self._data_parser.parse()

    def output(self, documents: List[Document]):
        # self.logger.info('Outputting...')
        output_formatter = OutputFormatterFactory.get_output_formatter(self.args, self.format, self.tmp_file)
        output_formatter.apply(documents)



class DummyReducer(LegacyCleanerComponentReducer):
    def __init__(self, args: argparse.Namespace, output_path: Optional[str] = None):
        out_path = output_path if output_path is not None else args.output_path
        onion_input_file = os.path.join(out_path, 'input.onion.debug')
        super().__init__(args, format_='onion', tmp_file=onion_input_file, input_path=out_path,
                         extensions=('.debug',), final_path='')
        self.output_path = out_path
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_input_file
        self.onion_tmp = os.path.join(out_path, 'tmp')

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        pass

    def _reduce(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_input_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)

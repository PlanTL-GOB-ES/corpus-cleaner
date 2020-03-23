from document import Document
from typing import Iterable
import argparse
import logging
from components.data_parser.data_parser import DataParser
from components.pre_filterer.pre_filterer import PreFilterer
from components.encoding_fixer.encoding_fixer import EncodingFixer
from components.normalizer.normalizer import Normalizer
from components.sentence_splitter._sentence_splitter import _SentenceSplitter
from components.sentence_filter.sentence_filter import SentenceFilter
from components.document_filter.document_filter import DocumentFilter
from components.document_organizer.document_organizer import DocumentOrganizer
from .components.output_formatter.output_formatter import OutputFormatter

COMPONENTS_DEFAULT = [DataParser, PreFilterer, EncodingFixer,
                      _SentenceSplitter, SentenceFilter, Normalizer,
                      DocumentFilter, DocumentOrganizer, OutputFormatter]


class Cleaner:
    def __init__(self, args: argparse.Namespace, output_dir: str, logger: logging):
        self.args = args
        self.output_dir = output_dir
        self.logger = logger
        self.components = COMPONENTS_DEFAULT
        self.pipeline = []

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--no-component', type=str, help='remove a given component from the pipeline')

    @staticmethod
    def check_args(parser: argparse.Namespace):
        # TODO check custom args
        pass

    def _create_pipeline(self):
        pass

    def clean(self, documents: Iterable[Document]) -> Iterable[Document]:
        pass

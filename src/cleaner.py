from typing import Any
import argparse
import logging
from components.data_parser.data_parser import DataParser
from components.data_parser.data_parser_factory import DataParserFactory
from components.pre_filterer.pre_filterer import PreFilterer
from components.encoding_fixer.encoding_fixer import EncodingFixer
from components.normalizer.normalizer import Normalizer
from components.sentence_splitter_component.sentence_splitter_component import SentenceSplitterComponent
from components.sentence_filter.sentence_filter import SentenceFilter
from components.document_filter.document_filter import DocumentFilter
from components.document_organizer.document_organizer import DocumentOrganizer
from components.output_formatter.output_formatter import OutputFormatter
from components.output_formatter.output_formatter_factory import OutputFormatterFactory
from typing import Iterable, Union
from components.cleaner_component import CleanerComponent
from document import Document

COMPONENTS_DEFAULT = (
    EncodingFixer, PreFilterer,
    SentenceSplitterComponent, SentenceFilter, Normalizer,
    DocumentFilter, DocumentOrganizer
)


class Cleaner:
    def __init__(self, args: argparse.Namespace, logger: logging):
        self.args = args
        self.logger = logger
        self.components = COMPONENTS_DEFAULT
        self.documents = self._get_documents()
        self.pipeline = self._create_pipeline()

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--no-component', type=str, help='remove a given component from the pipeline')

    @staticmethod
    def check_args(parser: argparse.Namespace):
        # TODO check custom args
        pass

    # TODO: remove specific component from the pipeline using cli arguments
    def _remove_component(self):
        raise NotImplementedError()

    def _get_documents(self):
        parser = DataParserFactory.get_parser(self.args)
        return parser.apply()

    def _create_pipeline(self) -> Iterable[CleanerComponent]:
        return (component(self.args) for component in self.components)

    def _output(self, documents: Iterable[Document]):
        output_formatter = OutputFormatterFactory.get_output_formatter(self.args)
        output_formatter.apply(documents)

    def clean(self):
        documents = self.documents
        for component in self.pipeline:
            documents = component.apply(documents)
        self._output(documents)

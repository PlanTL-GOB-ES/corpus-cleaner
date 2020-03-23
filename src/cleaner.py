from typing import Any
import argparse
import logging
from components.data_parser.data_parser import DataParser
from components.pre_filterer.pre_filterer import PreFilterer
from components.encoding_fixer.encoding_fixer import EncodingFixer
from components.normalizer.normalizer import Normalizer
from components.sentence_splitter_component.sentence_splitter_component import SentenceSplitterComponent
from components.sentence_filter.sentence_filter import SentenceFilter
from components.document_filter.document_filter import DocumentFilter
from components.document_organizer.document_organizer import DocumentOrganizer
from components.output_formatter.output_formatter import OutputFormatter

COMPONENTS_DEFAULT = (PreFilterer, EncodingFixer,
                      SentenceSplitterComponent, SentenceFilter, Normalizer,
                      DocumentFilter, DocumentOrganizer, OutputFormatter)


class Cleaner:
    def __init__(self, args: argparse.Namespace, output_dir: str, logger: logging):
        self.args = args
        self.output_dir = output_dir
        self.logger = logger
        self.components = COMPONENTS_DEFAULT
        self.documents = None
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
        raise NotImplementedError

    def _get_documents(self):
        parser = DataParser(**vars(self.args))
        self.documents = parser.apply(self.documents)

    def _create_pipeline(self):
        return (component(**vars(self.args)) for component in self.components)

    def clean(self):
        documents = self.documents
        for component in self.pipeline:
            documents = component.apply(documents)

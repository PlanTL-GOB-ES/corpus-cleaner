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
from typing import Iterable, Union, List
from components.cleaner_component import CleanerComponent
from document import Document

COMPONENTS_DEFAULT = [
    EncodingFixer, PreFilterer,
    SentenceSplitterComponent, SentenceFilter, Normalizer,
    DocumentFilter, DocumentOrganizer
]


class Cleaner:
    def __init__(self, args: argparse.Namespace, logger: logging):
        self.args = args
        self.logger = logger
        self.components = COMPONENTS_DEFAULT
        if args.components is not None:
            self.components = []
            for comp in COMPONENTS_DEFAULT:
                if comp.__name__ in args.components:
                    self.components.append(comp)
        self.documents = self._get_documents()
        self.pipeline = self._create_pipeline()

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--components', type=str, help='Elements of the pipeline', nargs='+',
                            default=list(map(lambda x: x.name, COMPONENTS_DEFAULT)))

    @staticmethod
    def check_args(args: argparse.Namespace):
        for comp in args.components:
            if comp not in list(map(lambda x: x.name, COMPONENTS_DEFAULT)):
                raise Exception('Unknown component', comp)
        # TODO: add more checks (eg. sentence splitting requirement for other components

    # TODO: remove specific component from the pipeline using cli arguments
    def _remove_component(self):
        raise NotImplementedError()

    def _get_documents(self) -> Iterable[Document]:
        self.logger.info('Parsing...')
        parser = DataParserFactory.get_parser(self.args, self.logger)
        return parser.apply()

    def _create_pipeline(self) -> List[CleanerComponent]:
        return [component(self.args, self.logger) for component in self.components]

    def _output(self, documents: Iterable[Document]):
        self.logger.info('Outputting...')
        output_formatter = OutputFormatterFactory.get_output_formatter(self.args, self.logger)
        output_formatter.apply(documents)

    def clean(self):
        documents = list(self.documents)
        for idx, component in enumerate(list(self.pipeline)):
            self.logger.info(f'Cleaning... ({idx + 1}/{len(self.pipeline)} components)')
            documents = list(component.apply(documents))
        self._output(documents)

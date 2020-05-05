import argparse
import logging
from corpus_cleaner.components.a_data_parser.data_parser import DataParser
from corpus_cleaner.components.a_data_parser.data_parser_factory import DataParserFactory
from corpus_cleaner.components.b_encoding_fixer.encoding_fixer import EncodingFixer
from corpus_cleaner.components.c_pre_filterer.pre_filterer import PreFilterer
from corpus_cleaner.components.d_sentence_splitter_component.sentence_splitter_component import \
    SentenceSplitterComponent
from corpus_cleaner.components.e_sentence_filter.sentence_filter import SentenceFilter
from corpus_cleaner.components.f_normalizer.normalizer import Normalizer
from corpus_cleaner.components.g_document_filter.document_filter import DocumentFilter
from corpus_cleaner.components.h_document_organizer.document_organizer import DocumentOrganizer
from corpus_cleaner.components.i_output_formatter.output_formatter import OutputFormatter
from corpus_cleaner.components.i_output_formatter.output_formatter_factory import OutputFormatterFactory
from typing import Iterable, List, Tuple
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
from collections import OrderedDict
from pipel import Pipeline
from pipel import PipelineLogger
from typing import Generator
from typing import cast

COMPONENTS_DEFAULT = [
    EncodingFixer, PreFilterer,
    SentenceSplitterComponent, SentenceFilter, Normalizer,
    DocumentFilter, DocumentOrganizer
]


class Cleaner:

    @staticmethod
    def get_components_classes() -> List:
        return [DataParser] + COMPONENTS_DEFAULT + [OutputFormatter]

    @staticmethod
    def get_valid_input_output_formats() -> Tuple:
        return DataParserFactory.VALID_INPUT_FORMATS, OutputFormatterFactory.VALID_OUTPUT_FORMATS

    def __init__(self, args: argparse.Namespace, logger: logging):
        self.args = args
        self.logger = PipelineLogger(logger)
        self.args.logger = self.logger
        self.components = COMPONENTS_DEFAULT
        if args.components is not None:
            self.components = []
            for comp in COMPONENTS_DEFAULT:
                if comp.__name__ in args.components:
                    self.components.append(comp)
        self.documents = None
        self.pipeline = self._create_pipeline()
        self.stats = OrderedDict()

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--components', type=str, help='Elements of the pipeline', nargs='+',
                            default=list(map(lambda x: x.__name__, COMPONENTS_DEFAULT)))
        parser.add_argument('--parallel',  action='store_true', help='Run the cleaner in parallel')

    @staticmethod
    def check_args(args: argparse.Namespace):
        for comp in args.components:
            if comp not in list(map(lambda x: x.__name__, COMPONENTS_DEFAULT)):
                raise Exception('Unknown component', comp)
        # TODO: add more checks (eg. sentence splitting requirement for other components

    def _get_documents(self) -> List[Iterable[Document]]:
        # self.logger.info('Parsing...')
        parser = DataParserFactory.get_parser(self.args)
        return parser.parse()

    def _create_pipeline(self) -> List[CleanerComponent]:
        return [component(self.args) for component in self.components]

    def _output(self, documents: Iterable[Document]):
        # self.logger.info('Outputting...')
        output_formatter = OutputFormatterFactory.get_output_formatter(self.args)
        output_formatter.apply(documents)

    def clean(self):

        pipeline = Pipeline(streamers=[cast(Generator, iterable) for iterable in self._get_documents()],
                            mappers_factory=self._create_pipeline,
                            output_reducer=self._output, batch_size=100,
                            parallel=True, logger=self.logger, log_every_iter=1)
        pipeline.run()


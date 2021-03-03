from corpus_cleaner.components.a_data_parser.data_parser import DataParser
from corpus_cleaner.components.a_data_parser.data_parser_factory import DataParserFactory
from corpus_cleaner.components.c_pre_filterer.pre_filterer import PreFilterer
from corpus_cleaner.components.d_sentence_splitter_component.sentence_splitter_component import \
    SentenceSplitterComponent

from corpus_cleaner.components.e_sentence_filter.sentence_filter import SentenceFilter
from corpus_cleaner.components.g_document_filter.document_filter import DocumentFilter
from corpus_cleaner.components.i_output_formatter.output_formatter import OutputFormatter
from corpus_cleaner.components.i_output_formatter.output_formatter_factory import OutputFormatterFactory
from typing import Iterable, List, Tuple
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
from corpus_cleaner.checkpoint import Checkpoint
from collections import OrderedDict
from corpus_cleaner.par_utils import MappingPipeline, PipelineLogger
from corpus_cleaner.components.cleaner_component_reducer import DummyReducer
import logging
import os
from . import __version__
from typing import Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import enum
from dataclasses import dataclass
from corpus_cleaner.components.cleaner_component import CleanerComponentConfig
from corpus_cleaner.components.a_data_parser.data_parser import DataParserConfig
from corpus_cleaner.components.c_pre_filterer.pre_filterer import PreFiltererConfig
from corpus_cleaner.components.d_sentence_splitter_component.sentence_splitter_component import SentenceSplitterConfig
from corpus_cleaner.components.e_sentence_filter.sentence_filter import SentenceFilterConfig
from corpus_cleaner.components.g_document_filter.document_filter import DocumentFilterConfig
from corpus_cleaner.components.i_output_formatter.output_formatter import OutputFormatterConfig


MAPPERS = [
    PreFilterer,
    SentenceSplitterComponent, SentenceFilter
]
REDUCER = DocumentFilter
COMPONENTS = [DataParser] + MAPPERS + [REDUCER, OutputFormatter]

class ParallelBackend(enum.Enum):
    MP = 'mp'
    RAY = 'ray'

class CheckpointBackend(enum.Enum):
    SHELVE = 'shelve'
    FILE = 'file'

@dataclass
class GlobalConfig:
    name: str  # A name to identify the run
    input_path: str  # Input data directory
    output_path: str  # Input data directory
    input_format: str  # Input data format
    output_format: str  # Output data format
    checkpoint_backend: CheckpointBackend = CheckpointBackend.FILE  # Shelve is more convenient but file is more robust.
    # For distributed executions, we recommend file.
    parallel: bool = False  # Run the cleaner in parallel. Only useful if there are multiple files.
    log_every_iter: int = -1  # Log the pipeline every N iterations (-1, silent)
    backend: ParallelBackend = ParallelBackend.MP  # Parallel backend (mp or ray)
    only_reduce: bool = False  # Only document filter
    only_reduce_output: bool = False  # Only document filter for output files (tmp/.onion)
    debug: bool = False  # Activate the debug error mode to compare the original and cleaned sentences
    components: Tuple[str] = tuple(map(lambda x: x.__name__, COMPONENTS))

    assert log_every_iter == -1 or log_every_iter >= 1



@dataclass
class CleanerConfig:
    global_config: GlobalConfig
    parser_config: DataParserConfig
    prefilterer_config: PreFiltererConfig
    sentence_splitter_config: SentenceSplitterConfig
    sentence_filter_config: SentenceFilterConfig
    document_filter_config: DocumentFilterConfig
    output_formatter_config: OutputFormatterConfig


class SentencePacker(CleanerComponentMapper):

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        document.sentences = [sen for sen in document.content.splitlines() if len(sen.split()) > 0]
        return document

class Cleaner:
    def __init__(self, config: CleanerConfig, logger: logging, checkpoint: Checkpoint):
        self._config = config
        self.logger = PipelineLogger(logger)
        self.mappers = MAPPERS
        self.tmp_dir = os.path.join(self._config.global_config.output_path, 'tmp')
        if not checkpoint.resume:
            os.makedirs(self.tmp_dir)
        self.mappers = []
        for comp in MAPPERS:
            if comp.__name__ in self._config.global_config.components:
                self.mappers.append(comp)
        if not self._config.global_config.only_reduce:
            self.mappers = [lambda x: DataParserFactory.get_parser_mapper(x)] + self.mappers + \
                           [lambda x: OutputFormatterFactory.get_output_formatter_mapper(
                               args=self.args, output_format='onion',
                               output_path=os.path.join(self.tmp_dir,
                                                        os.uname()[1] + '-' + str(os.getpid()) + '.onion'))]
        else:

            self.mappers = [lambda x: DataParserFactory.get_parser_mapper(x)] + [SentencePacker] + \
                           [lambda x: OutputFormatterFactory.get_output_formatter_mapper(
                               args=self.args, output_format='onion',
                               output_path=os.path.join(self.tmp_dir,
                                                        os.uname()[1] + '-' + str(os.getpid()) + '.onion'))]
        self.reducer = REDUCER if not self._config.global_config.debug else DummyReducer
        if self._config.components is not None and not self._config.global_config.debug:
            self.reducer = None
            for comp in self._config.components.components:
                if comp == REDUCER.__name__:
                    self.reducer = REDUCER
                    break
        self.documents = None
        self.stats = OrderedDict()
        self.checkpoint = checkpoint

    @staticmethod
    def get_components_classes() -> List:
        return [DataParser, PreFilterer, SentenceSplitterComponent, SentenceFilter, DocumentFilter, OutputFormatter]

    @staticmethod
    def get_valid_input_output_formats() -> Tuple:
        return DataParserFactory.VALID_INPUT_FORMATS, OutputFormatterFactory.VALID_OUTPUT_FORMATS


    def _get_documents(self) -> List[Iterable[Document]]:
        # self.logger.info('Parsing...')
        parser = DataParserFactory.get_parser(self._config.parser_config, input_format=self._config.)
        return parser.parse()

    def _get_paths(self) -> List[Tuple[int, str]]:
        # self.logger.info('Parsing...')
        parser = DataParserFactory.get_parser(self.args, done_paths=self.checkpoint.get_done_paths())
        return parser.get_idx_relative_filepaths()

    def _create_pipeline_mappers(self) -> List[CleanerComponent]:
        return [component(self.args) for component in self.mappers]

    def _output(self, documents: Iterable[Document]):
        # self.logger.info('Outputting...')
        output_formatter = OutputFormatterFactory.get_output_formatter(self._config.output_formatter_config)
        output_formatter.apply(documents)

    def clean(self):
        if not self._config.global_config.only_reduce_output:
            self.reducer = self.reducer(self.args)
            components_str = self.args.input_format + ' -> '
            for idx, c in enumerate(self.mappers):
                if idx not in [0, len(self.mappers) - 1]:
                    components_str += c.__name__ + ' -> '
            components_str += 'onion'
            self.logger.logger.info(components_str)
            pipeline = MappingPipeline(streams=self._get_paths(),
                                       mappers_factory=self._create_pipeline_mappers,
                                       parallel=self.args.parallel,
                                       logger=self.logger if self.args.log_every_iter != -1 else None,
                                       log_every_iter=self.args.log_every_iter,
                                       backend=self.args.backend,
                                       checkpoint_path=self.checkpoint.checkpoint_path)
            pipeline.run()

        if self.reducer is not None:
            self.reducer = self.reducer(self.args, output_path=os.path.join(self.args.input_path))
            self.logger.logger.info(f'Reducing with {self.reducer.__class__.__name__}')
            self.reducer.reduce()
            self.logger.logger.info(f'onion -> {self.args.output_format}')
            self.logger.logger.info('Writing deduplicated documents')
            self._output(self.reducer.get_documents()[0])

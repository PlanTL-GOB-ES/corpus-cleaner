from .output_formatter import OutputFormatter
from .fairseq_lm_output_formatter import FairseqLMOutputFormatter
from .onion_output_formatter import OnionOutputFormatter
from .sentence_output_formatter import SentenceOutputFormatter
from .output_formatter_mapper import OutputFormatterMapper
from corpus_cleaner.cleaner import GlobalConfig
from typing import Optional
from dataclasses import dataclass
import argparse
from corpus_cleaner.components.i_output_formatter.output_formatter import OutputFormatterConfig


class OutputFormatterFactory:
    VALID_OUTPUT_FORMATS = ['fairseq-lm', 'sentence']

    def __init__(self, config: GlobalConfig):
        self._config = config

    @staticmethod
    def get_output_formatter(config: OutputFormatterConfig) -> OutputFormatter:
        if config.output_format == 'fairseq-lm':
            return FairseqLMOutputFormatter()
        elif config.output_format == 'sentence':
            return SentenceOutputFormatter()
        elif config.output_format == 'onion':
            return OnionOutputFormatter()

    @staticmethod
    def get_output_formatter_mapper(args: argparse.Namespace, output_format: Optional[str] = None,
                                    output_path: Optional[str] = None, **kwargs) -> OutputFormatterMapper:
        return OutputFormatterMapper(args, OutputFormatterFactory.get_output_formatter(args, output_format, output_path,
                                                                                       **kwargs))

from .output_formatter import OutputFormatter
from .fairseq_lm_output_formatter import FairseqLMOutputFormatter
from .onion_output_formatter import OnionOutputFormatter
from .sentence_output_formatter import SentenceOutputFormatter
from .output_formatter_mapper import OutputFormatterMapper
from typing import Optional
import argparse


class OutputFormatterFactory:
    VALID_OUTPUT_FORMATS = ['fairseq-lm', 'sentence']

    @staticmethod
    def get_output_formatter(args: argparse.Namespace, output_format: Optional[str] = None,
                             output_path: Optional[str] = None, **kwargs) -> OutputFormatter:
        if output_format is None:
            if args.output_format == 'fairseq-lm':
                return FairseqLMOutputFormatter(args, **kwargs)
            elif args.output_format == 'sentence':
                return SentenceOutputFormatter(args, **kwargs)
            else:
                raise NotImplementedError()
        else:
            if output_format == 'onion':
                return OnionOutputFormatter(args, output_path)
            elif args.output_format == 'fairseq-lm':
                return FairseqLMOutputFormatter(args, output_path)
            else:
                raise NotImplementedError()

    @staticmethod
    def get_output_formatter_mapper(args: argparse.Namespace, output_format: Optional[str] = None,
                                    output_path: Optional[str] = None, **kwargs) -> OutputFormatterMapper:
        return OutputFormatterMapper(args, OutputFormatterFactory.get_output_formatter(args, output_format, output_path,
                                                                                       **kwargs))

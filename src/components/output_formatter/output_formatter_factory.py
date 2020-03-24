from .output_formatter import OutputFormatter
from .fairseq_lm_output_formatter import FairseqLMOutputFormatter
import argparse
import logging


class OutputFormatterFactory:
    VALID_OUTPUT_FORMATS = ['fairseq-lm']

    @staticmethod
    def get_output_formatter(args: argparse.Namespace, logger: logging.Logger, **kwargs) -> OutputFormatter:
        if args.output_format == 'fairseq-lm':
            return FairseqLMOutputFormatter(args, logger, **kwargs)
        else:
            raise NotImplementedError()

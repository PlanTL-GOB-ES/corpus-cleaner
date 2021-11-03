from .output_formatter import OutputFormatter
from .fairseq_lm_output_formatter import FairseqLMOutputFormatter
from .onion_output_formatter import OnionOutputFormatter
from .sentence_output_formatter import SentenceOutputFormatter
from .output_formatter_mapper import OutputFormatterMapper
from corpus_cleaner.cleaner import GlobalConfig
from corpus_cleaner.components.i_output_formatter.output_formatter import OutputFormatterConfig


class OutputFormatterFactory:
    VALID_OUTPUT_FORMATS = ['fairseq-lm', 'sentence']

    @staticmethod
    def get_output_formatter(config: OutputFormatterConfig) -> OutputFormatter:
        if config.output_format == 'fairseq-lm':
            return FairseqLMOutputFormatter(config)
        elif config.output_format == 'sentence':
            return SentenceOutputFormatter(config)
        elif config.output_format == 'onion':
            return OnionOutputFormatter(config)
        else:
            raise NotImplementedError(config.output_format)

    @staticmethod
    def get_output_formatter_mapper(config: OutputFormatterConfig) -> OutputFormatterMapper:
        return OutputFormatterMapper(OutputFormatterFactory.get_output_formatter(config))

from .output_formatter import OutputFormatter
from .fairseq_lm_output_formatter import FairseqLMOutputFormatter


class OutputFormatterFactory:
    VALID_OUTPUT_FORMATS = ['fairseq-lm']

    def __init__(self, output_format: str, **kwargs):
        self.output_format = output_format

    def get_output_formatter(self, *args, **kwargs) -> OutputFormatter:
        if self.output_format == 'fairseq-lm':
            return FairseqLMOutputFormatter(*args, **kwargs)
        else:
            raise NotImplementedError()

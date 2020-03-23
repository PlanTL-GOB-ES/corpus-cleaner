from .output_formatter import OutputFormatter
from .fairseq_lm_output_formatter import FairseqLMOutputFormatter


class OutputFormatterFactory:
    def __init__(self, format_type: str):
        self.format_type = format_type

    def get_output_formatter(self, args, kwargs) -> OutputFormatter:
        if self.format_type == 'fairseq_lm':
            return FairseqLMOutputFormatter(*args, **kwargs)
        else:
            raise NotImplementedError()

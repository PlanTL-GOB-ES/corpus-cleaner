from .output_formatter import OutputFormatter, OutputFormatterConfig
from corpus_cleaner.document import Document
import os
from corpus_cleaner.constants import TXT_OUTPUT_PATH

class FairseqLMOutputFormatter(OutputFormatter):
    def __init__(self, config: OutputFormatterConfig):
        super().__init__(config)

    def _init_writing(self):
        self.fd = open(os.path.join(self.path, TXT_OUTPUT_PATH), 'a')

    def _write_document(self, document: Document):
        if len(document.sentences) > 0:
            self.fd.writelines(f'{sentence}\n' for sentence in document.sentences)
            self.fd.write('\n')

    def _end_writing(self):
        self.fd.close()


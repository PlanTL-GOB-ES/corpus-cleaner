from .output_formatter import OutputFormatter
from typing import Iterable
from corpus_cleaner.document import Document
import os


class FairseqLMOutputFormatter(OutputFormatter):

    def _init_writing(self):
        self.fd = open(os.path.join(self.path, 'output.txt'), 'w')

    def _write_document(self, document: Document):
        for sentence in document.sentences:
            self.fd.write(sentence + '\n')
        self.fd.write('\n')

    def _end_writing(self):
        self.fd.close()


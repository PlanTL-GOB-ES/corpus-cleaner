from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document
import os
from typing import Optional


class FairseqLMOutputFormatter(OutputFormatter):
    def __init__(self, args, output_path: Optional[str] = None):
        if output_path is None:
            output_path = os.path.join(args.output_path, 'output.txt')
        super().__init__(args, output_path)

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        if len(document.sentences) > 0:
            self.fd.writelines(f'{sentence}\n' for sentence in document.sentences)
            self.fd.write('\n')

    def _end_writing(self):
        self.fd.close()


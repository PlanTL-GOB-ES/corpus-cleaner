from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document
import os


class FairseqLMOutputFormatter(OutputFormatter):
    def __init__(self, args, output_path: str = 'output.txt'):
        super().__init__(args, output_path)

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        if len(document.sentences) > 0:
            # sentences = [sentence.replace(f'{self.separator}', '\t') for sentence in document.sentences]
            self.fd.writelines(f'{sentence}\n' for sentence in document.sentences)
            self.fd.write('\n')

    def _end_writing(self):
        self.fd.close()


from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document
import argparse


class OnionOutputFormatter(OutputFormatter):
    def __init__(self, args: argparse.Namespace, output_path: str, **kwargs):
        super().__init__(args, output_path)
        self.start_doc_tag = '<doc '
        self.start_p_tag = ' >\n<p>\n'
        self.end_doc_tag = '\n</p>\n</doc>\n'

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        if document is not None:
            doc_onion = self.start_doc_tag + document.attr_str() + '\n'.join(document.sentences) + self.end_doc_tag
            self.fd.writelines(doc_onion)

    def _end_writing(self):
        self.fd.close()

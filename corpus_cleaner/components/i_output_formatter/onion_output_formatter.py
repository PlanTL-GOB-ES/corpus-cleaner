from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document, DiscardedDocument
import argparse


class OnionOutputFormatter(OutputFormatter):
    def __init__(self, args: argparse.Namespace, output_path: str):
        super().__init__(args, output_path)
        self.start_doc_tag = '<doc '
        self.start_p_tag = ' >\n<p>\n'
        self.end_doc_tag = '\n</p>\n</doc>\n'

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        # In normal mode, consider only non-discarded documents
        if not isinstance(document, DiscardedDocument):
            sentences_cleaned = document.sentences_cleaned
            doc_onion = self.start_doc_tag + document.attr_str() + self.start_p_tag + '\n'.join(sentences_cleaned) + \
                        self.end_doc_tag
            self.fd.writelines(doc_onion)

    def _end_writing(self):
        self.fd.close()


class DebugOnionOutputFormatter(OutputFormatter):
    def __init__(self, args: argparse.Namespace, output_path: str, **kwargs):
        super().__init__(args, output_path)
        self.start_doc_tag = '<doc '
        self.start_p_tag = ' >\n<p>\n'
        self.end_doc_tag = '\n</p>\n</doc>\n'

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        operations = [", ".join(ops) for ops in document.operations]
        sentences_cleaned = [f'{sent}{self.separator}{sent_clean}{self.separator}{operation}'
                             for sent, sent_clean, operation in zip(document.sentences,
                                                                    document.sentences_cleaned,
                                                                    operations)]
        doc_onion = self.start_doc_tag + document.attr_str() + self.start_p_tag + '\n'.join(sentences_cleaned) + \
                    self.end_doc_tag
        self.fd.writelines(doc_onion)

    def _end_writing(self):
        self.fd.close()

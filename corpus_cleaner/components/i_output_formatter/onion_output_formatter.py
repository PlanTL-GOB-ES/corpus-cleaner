from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document
import argparse


class OnionOutputFormatter(OutputFormatter):
    def __init__(self, args: argparse.Namespace, output_path: str, **kwargs):
        super().__init__(args, output_path)
        self.start_doc_tag = '<doc '
        self.start_p_tag = ' >\n<p>\n'
        self.end_doc_tag = '\n</p>\n</doc>\n'
        self.debug = args.debug

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        if document is not None:
            if self.debug:
                operations = [", ".join(ops) for ops in document.operations]
                sentences = [f'{sent_orig}{self.separator}{sent_clean}{self.separator}{operation}'
                             for sent_orig, sent_clean, operation in zip(document.sentences_orig,
                                                                         document.sentences,
                                                                         operations)]
            else:
                sentences = document.sentences
            doc_onion = self.start_doc_tag + document.attr_str() + self.start_p_tag + '\n'.join(sentences) + \
                        self.end_doc_tag

            self.fd.writelines(doc_onion)

    def _end_writing(self):
        self.fd.close()

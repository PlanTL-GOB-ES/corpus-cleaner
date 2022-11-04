from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document
import os
from typing import Optional
from ordered_set import OrderedSet


class ParagraphOutputFormatter(OutputFormatter):
    def __init__(self, args, output_path: Optional[str] = None):
        if output_path is None:
            output_path = os.path.join(args.output_path, 'output.txt')
        super().__init__(args, output_path)
        self.end_doc_tag = '<end-of-doc>\n'

    def _init_writing(self):
        self.fd = open(self.path, 'a')

    def _write_document(self, document: Document):
        if len(document.sentences) > 0:

            for paragraph_idx in OrderedSet(document.sentence_to_paragraph_idx.values()):
                paragraph_sentences = []

                for sentence_idx, sentence in enumerate(document.sentences):
                    if document.sentence_to_paragraph_idx[sentence_idx] == paragraph_idx:
                        paragraph_sentences.append(sentence)

                self.fd.write(' '.join(paragraph_sentences))

                if paragraph_idx == max(document.sentence_to_paragraph_idx.values()):
                    self.fd.write('\n')
                else:
                    self.fd.write('\n\n')
            self.fd.write(self.end_doc_tag)

    def _end_writing(self):
        self.fd.close()


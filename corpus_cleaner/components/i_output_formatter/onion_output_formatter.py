from .output_formatter import OutputFormatter
from corpus_cleaner.document import Document, DiscardedDocument
from corpus_cleaner.cleaner import GlobalConfig
from corpus_cleaner.constants import ONION_START_P_TAG, ONION_START_DOC_TAG, ONION_END_P_TAG


class OnionOutputFormatter(OutputFormatter):
    def __init__(self, config: GlobalConfig):
        super().__init__(config)
        self.start_doc_tag = ONION_START_DOC_TAG
        self.start_p_tag = ONION_START_P_TAG
        self.end_doc_tag = ONION_END_P_TAG

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
    def __init__(self, config: GlobalConfig):
        super().__init__(config)
        self.start_doc_tag = ONION_START_DOC_TAG
        self.start_p_tag = ONION_START_P_TAG
        self.end_doc_tag = ONION_END_P_TAG

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

from . import OutputFormatter
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
from typing import Iterable
from typing import Tuple, Optional
import os
from corpus_cleaner.constants import CHECKPOINT_PATH_ESCAPE
from typing import Set


class OutputFormatterMapper(CleanerComponent):
    def __init__(self, output_formatter: OutputFormatter):
        self.output_formatter = output_formatter

    def _write_checkpoint(self, e: str):
        self.output_formatter.write_checkpoint(e)

    def __call__(self, documents: Iterable[Document]):# -> Iterable[Document]
        self.output_formatter.init_writing()
        filename = None
        for document in documents:
            self.output_formatter.write_document(document)
            filename = document.filename
        self.output_formatter.end_writing()

        self._write_checkpoint(filename)

        #return filename


from corpus_cleaner.document import Document
from typing import Iterable, Union
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from typing import TextIO, Optional
from corpus_cleaner.constants import DEBUG_SEPARATOR, CHECKPOINT_PATH_ESCAPE
import os


class OutputFormatterConfig:
    output_format: str
    output_path: str
    write_checkpoint_path: Optional[str] = None


class OutputFormatter(CleanerComponentMapper):
    def __int__(self, config: OutputFormatterConfig):
        self._config = config
        self.path = config.output_path
        self.fd: Optional[TextIO] = None
        self.separator = DEBUG_SEPARATOR

    def write_checkpoint(self, e: str):
        if self._config.write_checkpoint_path:
            with open(os.path.join(
                    self._config.write_checkpoint_path, e.replace('/', CHECKPOINT_PATH_ESCAPE)), 'w') as f:
                pass

    def _init_writing(self):
        raise NotImplementedError

    def write_document(self, document: Document):
        raise NotImplementedError

    def _end_writing(self):
        raise NotImplementedError

    def _output_format(self, documents: Iterable[Document]):
        if self.fd is None:
            self._init_writing()
        for document in documents:
            if document is None:
                continue
            self.write_document(document)
        self._end_writing()

    def apply(self, documents: Optional[Iterable[Document]]) -> Optional[Iterable[Document]]:
        return self._output_format(documents)

    def init_writing(self):
        self._init_writing()

    def end_writing(self):
        self._end_writing()

from corpus_cleaner.document import Document
from typing import Iterable, Union
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from typing import TextIO
from corpus_cleaner.constants import DEBUG_SEPARATOR
from cleaner import GlobalConfig


class OutputFormatter(CleanerComponentMapper):
    def __int__(self, config: GlobalConfig):
        self._config = config
        self.path = self._config.output_path
        self.fd: Union[TextIO, None] = None
        self.separator = DEBUG_SEPARATOR

    def _init_writing(self):
        raise NotImplementedError()

    def _write_document(self, document: Document):
        raise NotImplementedError()

    def _end_writing(self):
        raise NotImplementedError()

    def _output_format(self, documents: Iterable[Document]):
        if self.fd is None:
            self._init_writing()
        for document in documents:
            if document is None:
                continue
            self._write_document(document)
        self._end_writing()

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._output_format(documents)

    def init_writing(self):
        self._init_writing()

    def end_writing(self):
        self._end_writing()

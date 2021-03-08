from . import OutputFormatter
from corpus_cleaner.components.cleaner_component import CleanerComponent
from corpus_cleaner.document import Document
from typing import Iterable
from typing import Tuple, Optional
import os


class OutputFormatterMapper(CleanerComponent):
    def __int__(self, config: GlobalConfig, output_formatter: OutputFormatter):
        self._config = config
        self.output_formatter = output_formatter

    def _write_checkpoint(self, e: str):
        with open(os.path.join(self._config.write_checkpoint_path, e.replace('/', '!')), 'w') as f:
            pass

    def __call__(self, documents: Iterable[Document]) -> Tuple[int, Optional[Tuple], Optional[str]]:
        self.output_formatter.init_writing()
        filename = None
        for document in documents:
            self.output_formatter._write_document(document)
            filename = document.filename
        self.output_formatter.end_writing()

        if self._config.write_checkpoint_path:
            self._write_checkpoint(filename)

        return filename


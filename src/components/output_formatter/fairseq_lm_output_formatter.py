from .output_formatter import OutputFormatter
from typing import Iterable
from document import Document
import os


class FairseqLMOutputFormatter(OutputFormatter):
    def _output_format(self, documents: Iterable[Document]):
        with open(os.path.join(self.path, 'output.txt'), 'w') as f:
            for doc in documents:
                f.writelines(doc.sentences)
                f.write('\n')

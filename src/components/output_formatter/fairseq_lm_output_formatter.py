from .output_formatter import OutputFormatter
from typing import Iterable
from document import Document


class FairseqLMOutputFormatter(OutputFormatter):
    def output_format(self, path: str, documents: Iterable[Document]):
        with open(path, 'r') as f:
            for doc in documents:
                f.writelines(doc.sentences)
                f.write('\n')

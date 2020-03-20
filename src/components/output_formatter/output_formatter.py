import document
from typing import Iterable


class OutputFormatter:
    def output_format(self, path: str, documents: Iterable[document]):
        raise NotImplementedError()

from typing import Iterable
from src.document import Document


class Parser:
    def __init__(self, path: str):
        self.path = path

    def parse(self) -> Iterable[Document]:
        raise NotImplementedError()

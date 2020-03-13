from typing import Iterable
from document import Document


class DataParser:
    def __init__(self, path: str):
        self.path = path

    def parse(self) -> Iterable[Document]:
        raise NotImplementedError()

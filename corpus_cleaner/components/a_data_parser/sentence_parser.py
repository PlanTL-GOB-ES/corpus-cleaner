from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Tuple
import argparse


class SentenceParser(DataParser):
    def __init__(self,  args: argparse.Namespace, extensions: Tuple[str] = ('txt',),
                 encoding='utf-8', **kwargs):
        super(SentenceParser, self).__init__(args, input_path=args.input_path, extensions=extensions,
                                             encoding=encoding, **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        url = None
        title = None
        i = 1
        for line in fd:
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                filename = relative_filepath
                doc_id = f'{relative_filepath}-{i}'
                yield Document(content=line, id_=doc_id, url=url, title=title,
                               filename=filename)

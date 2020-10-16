from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Tuple
import argparse


class FairseqLMParser(DataParser):
    def __init__(self,  args: argparse.Namespace, extensions: Tuple[str] = ('txt',),
                 encoding='utf-8', **kwargs):
        super(FairseqLMParser, self).__init__(args, input_path=args.input_path, extensions=extensions,
                                              encoding=encoding, **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        doc_lines = []
        doc_id = ''
        url = None
        title = ''
        first = True
        i = 1
        for line in fd:
            line = line.strip()
            if first and len(line) == 0:
                continue
            if first:
                first = False
                doc_id = relative_filepath + '-' + str(i)
                title = line
                doc_lines.append(line + '\n')
            elif len(line) == 0:
                filename = relative_filepath
                yield Document(content=''.join(doc_lines), id_=doc_id, url=url, title=title,
                               filename=filename)
                doc_lines = []
                doc_id = ''
                url = ''
                title = ''
            else:
                doc_lines.append(line + '\n')

        if len(doc_lines) > 0:
            filename = relative_filepath
            yield Document(content='\n'.join(doc_lines), id_=doc_id, url=url, title=title,
                           filename=filename)

from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Tuple
import argparse
from typing import Optional


class OnionParser(DataParser):
    def __init__(self, args: argparse.Namespace, extensions: Tuple[str] = ('.dedup',), input_path: Optional[str] = None,
                 **kwargs):
        super(OnionParser, self).__init__(args, encoding='utf-8',
                                          input_path=args.output_path if input_path is None else input_path,
                                          extensions=extensions, **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        doc_sentences = []
        doc = Document(content='')
        for line in fd:
            line_index, line = line.split('\t')
            # ignore the first two lines with the start tags
            if line.startswith('<doc'):
                sp = line.split()
                if len(sp) > 2:
                    doc = Document.parse_str(sp[1:-1])
                else:
                    doc = Document(content='')
            if line.startswith('<p>') or line.startswith('</p>'):
                continue
            # empty the document sentences list when a new document is reached and return the document object
            elif line.startswith('</doc>'):
                # TODO: add the raw content for each document with the Onion tags
                doc.sentences = doc_sentences
                yield doc
                doc_sentences = []
            else:
                if line_index == '0':
                    doc_sentences.append(line.strip())

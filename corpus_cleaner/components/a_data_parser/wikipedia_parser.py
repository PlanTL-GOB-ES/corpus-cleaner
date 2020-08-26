from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
import xml.etree.ElementTree as ET
from typing import TextIO
from typing import Tuple
import argparse


class WikipediaParser(DataParser):
    def __init__(self,  args: argparse.Namespace, extensions: Tuple[str] = ('*',),
                 encoding='utf-8', **kwargs):
        super(WikipediaParser, self).__init__(args, input_path=args.input_path, extensions=extensions,
                                              encoding=encoding, **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        doc_lines = []
        doc_id = ''
        url = ''
        title = ''
        first = True
        for line in fd:
            parsed_line = line.split()
            if len(parsed_line) == 0:
                continue
            if parsed_line[0] == '<doc':
                first = True
                root = ET.fromstring(line + '</doc>')
                attribs = root.attrib
                doc_id = attribs['id']
                url = attribs['url']
                title = attribs['title']
            elif parsed_line[0] == '</doc>':
                filename = relative_filepath
                yield Document(content=''.join(doc_lines), id_=doc_id, url=url, title=title,
                               filename=filename)
                doc_lines = []
                doc_id = ''
                url = ''
                title = ''
            else:
                if first:
                    doc_lines.append(line + '.\n')
                    first = False
                else:
                    doc_lines.append(line + '\n')

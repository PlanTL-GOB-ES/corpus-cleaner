from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Tuple
import argparse
import xml.etree.ElementTree as ET


class DocumentParser(DataParser):
    def __init__(self, args: argparse.Namespace, extensions: Tuple[str] = ('*',), **kwargs):
        super(DocumentParser, self).__init__(args, input_path=args.input_path, extensions=extensions, **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        raw = ''
        for line in fd.readlines():
            if line[0:4] == '<doc':
                if len(raw) > 0:
                    tree = ET.fromstring(raw)
                    content = ''.join([p.text + '\n' for p in tree.findall('p')])
                    sentences = None
                    filename = relative_filepath
                    title = None
                    url = tree.attrib['url']
                    id_ = tree.attrib['id']
                    keywords = None
                    heads = None
                    language = None

                    yield Document(content=content, sentences=sentences, filename=filename, title=title, url=url,
                                   id_=id_, keywords=keywords, heads=heads, language=language)

                raw = line
            else:
                raw += line

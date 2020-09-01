from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Tuple
import argparse
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape
import re


class DocumentParser(DataParser):
    def __init__(self, args: argparse.Namespace, extensions: Tuple[str] = ('*',), **kwargs):
        super(DocumentParser, self).__init__(args, input_path=args.input_path, extensions=extensions, **kwargs)
        self.url = re.compile('(url=\")(.*)(\"\s)')
        self.tags = re.compile('<.*?>')

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        raw = ''
        for line in fd:
            if line[0:4] == '<doc':
                if len(raw) > 0:
                    try:
                        ls = raw.splitlines()
                        l1 = ls[0]
                        url_search = self.url.search(l1)
                        if url_search:
                            url = url_search.group(2)
                            escaped_url = escape(url)
                            l1 = self.url.sub('\\1' + escaped_url + '\\3', l1)
                            tree = ET.fromstring(l1 + '</doc>')
                            sentences = None
                            filename = relative_filepath
                            title = None
                            url = unescape(tree.attrib['url'])
                            id_ = tree.attrib['id']
                            keywords = None
                            heads = None
                            language = None
                        else:
                            sentences = None
                            filename = relative_filepath
                            title = None
                            url = None
                            id_ = None
                            keywords = None
                            heads = None
                            language = None
                        content = ''
                        for l in ls[1:-1]:
                            if l.startswith('<p'):
                                content += self.tags.sub('', l) + '\n'
                    except BaseException as e:
                        self.logger.logger.info(e)
                        raw = ''
                        continue

                    yield Document(content=content, sentences=sentences, filename=filename, title=title, url=url,
                                   id_=id_, keywords=keywords, heads=heads, language=language)

                raw = line
            else:
                raw += line

from components.data_parser import DataParser
from typing import Iterable
from document import Document
import os
import xml.etree.ElementTree as ET


class WikipediaParser(DataParser):
    def parse(self) -> Iterable[Document]:
        for chunk in os.listdir(self.path):
            for filename in os.listdir(os.path.join(self.path, chunk)):
                with open(os.path.join(self.path, chunk, filename), 'r', errors='ignore') as f:
                    doc_lines = []
                    doc_id = ''
                    url = ''
                    title = ''
                    for line in f.readlines():
                        parsed_line = line.split()
                        if len(parsed_line) == 0:
                            continue
                        if parsed_line[0] == '<doc':
                            root = ET.fromstring(line + '</doc>')
                            attribs = root.attrib
                            doc_id = attribs['id']
                            url = attribs['url']
                            title = attribs['title']
                        elif parsed_line[0] == '</doc>':
                            filename = os.path.join(chunk, filename)
                            yield Document(content=''.join(doc_lines), id_=doc_id, url=url, title=title,
                                           filename=filename)
                            doc_lines = []
                            doc_id = ''
                            url = ''
                            title = ''
                        else:
                            doc_lines.append(line + '\n')

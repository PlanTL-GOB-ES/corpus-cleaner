from components.data_parser import DataParser
from typing import Iterable
from document import Document
import xml.etree.ElementTree as ET
from typing import TextIO


class WikipediaParser(DataParser):
    def __init__(self, *args, **kwargs):
        super(WikipediaParser, self).__init__(*args, extensions=['*'], **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, doc_counter: int) -> Iterable[Document]:
        doc_lines = []
        doc_id = ''
        url = ''
        title = ''
        for line in fd.readlines():
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
                filename = relative_filepath
                yield Document(content=''.join(doc_lines), id_=doc_id, url=url, title=title,
                               filename=filename)
                doc_lines = []
                doc_id = ''
                url = ''
                title = ''
            else:
                doc_lines.append(line + '\n')


def test():
    import os
    file_dir = os.path.join('..', '..', '..', 'test', 'wiki')
    parser = WikipediaParser(file_dir, encoding='utf-8')
    documents = parser.parse()

    # Show the first document
    for idx, doc in enumerate(documents):
        print(f'DOC {idx}: {doc.content}\n')
        if idx == 1:
            break


if __name__ == '__main__':
    test()

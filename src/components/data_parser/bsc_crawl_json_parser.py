from components.data_parser import DataParser
from typing import Iterable
from document import Document
import json
from typing import TextIO
from typing import Tuple
import argparse


class BSCCrawlJSONParser(DataParser):

    def __init__(self, args: argparse.Namespace, extensions: Tuple[str]=('.json',), **kwargs):
        super(BSCCrawlJSONParser, self).__init__(args,  input_path=args.input_path, extensions=extensions, **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, doc_counter: int) -> Iterable[Document]:
        i = doc_counter + 1
        for idx, line in enumerate(fd.readlines()):
            j = json.loads(line)
            url = j['url']
            keywords = j['url']
            content = j['p']
            heads = j['heads']
            title = j['titles']
            filename = relative_filepath
            yield Document(content=content, filename=filename, url=url, id_=i,
                           keywords=keywords, heads=heads, title=title)
            i += idx


def test():
    import os
    file_dir = os.path.join('..', '..', '..', 'test', 'bne')
    parser = BSCCrawlJSONParser(file_dir)
    documents = parser._parse()

    # Show the first document
    for idx, doc in enumerate(documents):
        print(f'DOC {idx}: {doc.content}\n')
        if idx == 1:
            break


if __name__ == '__main__':
    test()

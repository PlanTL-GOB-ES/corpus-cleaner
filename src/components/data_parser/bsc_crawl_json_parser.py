from components.data_parser import DataParser
from typing import Iterable
from document import Document
import os
import json


class BSCCrawlJSONParser(DataParser):
    def parse(self) -> Iterable[Document]:
        i = 1
        for chunk in sorted(os.listdir(self.path)):
            for filename in sorted(os.listdir(os.path.join(self.path, chunk))):
                with open(os.path.join(self.path, chunk, filename), 'r', errors='ignore') as f:
                    for idx, line in enumerate(f.readlines()):
                        i += idx
                        j = json.loads(line)
                        url = j['url']
                        keywords = j['url']
                        content = j['p']
                        heads = j['heads']
                        title = j['titles']
                        filename = os.path.join(chunk, filename)
                        yield Document(content=content, filename=filename, url=url, id_=i,
                                       keywords=keywords, heads=heads, title=title)


def test():
    file_dir = '../../../test/bne'
    parser = BSCCrawlJSONParser(file_dir)
    documents = parser.parse()

    # Show the first two documents
    for idx, doc in enumerate(documents):
        print(f'DOC {idx}: {doc.content}\n')
        if idx == 1:
            break


if __name__ == '__main__':
    test()

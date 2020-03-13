from components.data_parser import DataParser
from typing import Iterable
from document import Document
import os
import json


class BSCCrawlJSONParser(DataParser):
    def parse(self) -> Iterable[Document]:
        i = 1
        for chunk in sorted(os.listdir(self.path)):
            for filepath in sorted(os.listdir(os.path.join(self.path, chunk))):
                with open(os.path.join(self.path, chunk, filepath), 'r') as f:
                    for idx, line in enumerate(f.readlines()):
                        i += idx
                        j = json.loads(line)
                        url = j['url']
                        keywords = j['url']
                        content = j['p']
                        heads = j['heads']
                        title = j['titles']
                        filename = os.path.join(chunk, filepath)
                        yield Document(content=content, filename=filename, url=url, id_=i,
                                       keywords=keywords, heads=heads, title=title)

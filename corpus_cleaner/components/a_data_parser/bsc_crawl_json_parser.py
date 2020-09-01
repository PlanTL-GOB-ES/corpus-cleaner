from .data_parser import DataParser
from typing import Iterable
from corpus_cleaner.document import Document
import json
from typing import TextIO
from typing import Tuple
import argparse


class BSCCrawlJSONParser(DataParser):

    def __init__(self, args: argparse.Namespace, extensions: Tuple[str]=('.json', '.json.gz'), **kwargs):
        super(BSCCrawlJSONParser, self).__init__(args, input_path=args.input_path, extensions=extensions,
                                                 **kwargs)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) ->\
            Iterable[Document]:
        for idx, line in enumerate(fd):
            j = json.loads(line)
            url = j['url']
            keywords = j['url']
            content = j['p']
            heads = j['heads']
            title = j['titles']
            filename = relative_filepath
            yield Document(content=content, filename=filename, url=url, id_=f'{idx_filepath}-{idx+1}',
                           keywords=keywords, heads=heads, title=title)

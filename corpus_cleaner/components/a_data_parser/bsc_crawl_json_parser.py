from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
import json
from typing import TextIO, Optional
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import HARDCODED_EXTENSIONS


class BSCCrawlJSONParser(DataParser):

    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None):
        hardcoded = False
        if not config.extensions:
            config.extensions = ('.json', '.json.gz')
        else:
            hardcoded = True
        super().__init__(config, logger)
        if hardcoded:
            self._warn(HARDCODED_EXTENSIONS)

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

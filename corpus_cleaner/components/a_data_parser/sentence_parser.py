from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Optional
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import HARDCODED_EXTENSIONS, HARDCODED_ENCODING


class SentenceParser(DataParser):
    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None):
        hardcoded_extensions = False
        if not config.extensions:
            config.extensions = ('.txt',)
        else:
            hardcoded_extensions = True
        hardcoded_encoding = False
        if not config.encoding:
            config.encoding = 'utf-8'
        else:
            hardcoded_encoding = True
        super().__init__(config, logger)
        if hardcoded_extensions:
            self._warn(HARDCODED_EXTENSIONS)
        if hardcoded_encoding:
            self._warn(HARDCODED_ENCODING)


    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        url = None
        title = None
        i = 1
        for line in fd:
            line = line.strip()
            if len(line) == 0:
                continue
            else:
                filename = relative_filepath
                doc_id = f'{relative_filepath}-{i}'
                yield Document(content=line, id_=doc_id, url=url, title=title,
                               filename=filename)

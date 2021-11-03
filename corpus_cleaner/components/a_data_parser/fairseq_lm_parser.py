from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Optional
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import HARDCODED_EXTENSIONS, HARDCODED_ENCODING


class FairseqLMParser(DataParser):
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
        doc_lines = []
        doc_id = ''
        url = None
        title = ''
        first = True
        i = 1
        for line in fd:
            line = line.strip()
            if first and len(line) == 0:
                continue
            if first:
                first = False
                doc_id = relative_filepath + '-' + str(i)
                title = line
                doc_lines.append(line + '\n')
            elif len(line) == 0:
                filename = relative_filepath
                yield Document(content=''.join(doc_lines), id_=doc_id, url=url, title=title,
                               filename=filename)
                doc_lines = []
                doc_id = ''
                url = ''
                title = ''
            else:
                doc_lines.append(line + '\n')

        if len(doc_lines) > 0:
            filename = relative_filepath
            yield Document(content='\n'.join(doc_lines), id_=doc_id, url=url, title=title,
                           filename=filename)

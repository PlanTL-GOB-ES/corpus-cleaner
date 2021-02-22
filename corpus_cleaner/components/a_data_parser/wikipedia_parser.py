from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
import xml.etree.ElementTree as ET
from typing import TextIO
from typing import Optional
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import HARDCODED_EXTENSIONS, HARDCODED_ENCODING


class WikipediaParser(DataParser):
    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None):
        hardcoded_extensions = False
        if not config.extensions:
            config.extensions = ('*',)
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
        url = ''
        title = ''
        first = True
        for line in fd:
            parsed_line = line.split()
            if len(parsed_line) == 0:
                continue
            if parsed_line[0] == '<doc':
                first = True
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
                if first:
                    doc_lines.append(line + '.\n')
                    first = False
                else:
                    doc_lines.append(line + '\n')

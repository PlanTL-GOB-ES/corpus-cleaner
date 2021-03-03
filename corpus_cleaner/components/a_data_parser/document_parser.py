from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO, Optional
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape
import re
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import HARDCODED_EXTENSIONS


class DocumentParser(DataParser):
    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None):
        hardcoded = False
        if not config.extensions:
            config.extensions = ('*',)
        else:
            hardcoded = True
        super().__init__(config, logger)
        if hardcoded:
            self._warn(HARDCODED_EXTENSIONS)
        self._url = re.compile('(url=\")(.*)(\"\s)')
        self._tags = re.compile('<.*?>')

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        raw = ''
        for line in fd:
            if line[0:4] == '<doc':
                if len(raw) > 0:
                    try:
                        ls = raw.splitlines()
                        l1 = ls[0]
                        url_search = self._url.search(l1)
                        if url_search:
                            url = url_search.group(2)
                            escaped_url = escape(url)
                            l1 = self._url.sub('\\1' + escaped_url + '\\3', l1)
                            tree = ET.fromstring(l1 + '</doc>')
                            sentences = None
                            filename = relative_filepath
                            title = None
                            url = unescape(tree.attrib['url'])
                            id_ = tree.attrib['id']
                            keywords = None
                            heads = None
                            language = None
                        else:
                            sentences = None
                            filename = relative_filepath
                            title = None
                            url = None
                            id_ = None
                            keywords = None
                            heads = None
                            language = None
                        content = ''
                        for l in ls[1:-1]:
                            if l.startswith('<p'):
                                content += self._tags.sub('', l) + '\n'
                    except BaseException as e:
                        self._log(str(e))
                        raw = ''
                        continue

                    yield Document(content=content, sentences=sentences, filename=filename, title=title, url=url,
                                   id_=id_, keywords=keywords, heads=heads, language=language)

                raw = line
            else:
                raw += line

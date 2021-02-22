from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from typing import Optional
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import DEDUP_EXTENSION


class OnionParser(DataParser):
    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None, debug: bool = False):
        config.extensions = (DEDUP_EXTENSION,)
        config.encoding = 'utf-8'
        # Here, unlike in the other parsers, we don't warn about the hardcoding of extensions and encoding, because this
        # parser is for internal usage.
        super().__init__(config, logger)
        self._debug = debug

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        doc_sentences = []
        doc = Document(content='')
        for line in fd:
            if not self._debug:
                line_index = line.split('\t')[0]
                line = '\t'.join(line.split('\t')[1:])
            # ignore the first two lines with the start tags
            if line.startswith('<doc'):
                sp = line.split()
                if len(sp) > 2:
                    doc = Document.parse_str(sp[1:-1])
                else:
                    doc = Document(content='')
            elif line in ['<p>\n', '</p>\n']:
                continue
            # empty the document sentences list when a new document is reached and return the document object
            elif line.startswith('</doc>'):
                # TODO: add the raw content for each document with the Onion tags
                doc.sentences = doc_sentences
                yield doc
                doc_sentences = []
            else:
                if self._debug or line_index == '0':
                    doc_sentences.append(line.strip('\n'))

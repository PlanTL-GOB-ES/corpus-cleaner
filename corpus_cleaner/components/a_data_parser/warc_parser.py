from .data_parser import DataParser, DataParserConfig
from typing import Iterable
from corpus_cleaner.document import Document
from typing import TextIO
from warcio.archiveiterator import ArchiveIterator
import re
from selectolax.parser import HTMLParser
from typing import BinaryIO, List, Optional
from corpus_cleaner.constants import WARC_SKIP
from corpus_cleaner.par_utils import PipelineLogger
from corpus_cleaner.constants import HARDCODED_EXTENSIONS, HARDCODED_ENCODING


# BSC Soup from BSC for BNE
#    author: Joaquim More and Claudia Rosas
#    date: october 2019
#
#    modified by: Ona de Gibert
#    date: july 2020
#
#    modified by: Jordi Armengol
#     data: july 2020
# TODO: I believe this file should be refactored, annotated with types, pythonified, PEPified. I have just adapted it
# to work with the rest of the pipeline
# Additional notes: When parsing plain text files, we applied encoding guessing. Now, with binary files, we don't.
# Also, we do NOT store the intermediate jsons, and nothing is really parameterized.

class WARCParser(DataParser):

    def __init__(self, config: DataParserConfig, logger: Optional[PipelineLogger] = None):
        hardcoded_extensions = False
        if not config.extensions:
            config.extensions = ('.warc', '.warc.gz')
        else:
            hardcoded_extensions = True
        hardcoded_bytes = False
        if not config.encoding:
            config.bytes_ = True
        else:
            hardcoded_bytes = False
        super().__init__(config, logger)
        if hardcoded_extensions:
            self._warn(HARDCODED_EXTENSIONS)
        if hardcoded_bytes:
            self._warn(HARDCODED_ENCODING)

        self.file_data = {}
        self.error_msgs = ['404. That’s an error.', 'was not found on this server', '400. That’s an error.',
                           'The document has moved here.', 'You don\'t have permission to access',
                           'The requested file could not be found.', 'You do not have permission to access']
        self.skip = WARC_SKIP
        self.compulsory = 'p'
        if not self._config.warc_warn:
            import logging
            logging.getLogger('warcio').setLevel(logging.ERROR)

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> \
            Iterable[Document]:
        raise RuntimeError('WARCParser should not parse plain text files')

    def _parse_binary_file(self, fd: BinaryIO, relative_filepath: str, idx_filepath: int) -> \
            List[Iterable[Document]]:

        try:
            warc_file = fd
            filename = relative_filepath.replace(".warc.gz", "").replace("./", "")
            n_documents = 0
            for i, record in enumerate(ArchiveIterator(warc_file)):
                if record.rec_type == 'response' and record.rec_headers.get_header('Content-Type').split(';')[0] == \
                        'application/http':
                    if record.rec_headers.get_header('WARC-Target-URI')[-3:] in self.skip:
                        continue
                    elif int(record.rec_headers.get_header('Content-Length')) > 10000000:
                        pass
                        #  print('Warning!' + record.rec_headers.get_header('WARC-Target-URI') +
                        #      " Too big to be only text. Skipped")
                    else:
                        url, paragraphs, heads, titles, keywords = self._read_doc(record)
                        if url:
                            try:
                                n_documents += 1

                                if re.search('[a-zA-Z]', paragraphs) and self._ok_str(paragraphs):
                                    complete_url = filename + url
                                    yield Document(content=paragraphs, filename=relative_filepath, url=complete_url,
                                                               id_=f'{idx_filepath}-{n_documents+1}', keywords=keywords,
                                                               heads=heads, title=titles)
                            except:
                                pass
        except:
            # TODO: Properly debug the GeneratorExit in WARC
            return
        return

    def _ok_str(self, text):
        test = True
        i = 0
        while test and i < len(self.error_msgs):
            e = self.error_msgs[i]
            if e in text:
                test = False
            else:
                i += 1
        return test

    @staticmethod
    def _parse_selectolax(html):
        tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'meta']
        # Replace breaks with a new line in front to make sure they mark an EOL
        html = str(html.decode('utf-8')).replace("<br", "\n<br")
        tree = HTMLParser(html)
        paragraphs = []
        heads = []
        links = []
        keyws = []
        for t in tags:
            selector = t
            for node in tree.css(selector):
                if selector == 'meta':
                    if 'name' in node.attributes and 'content' in node.attributes:
                        if node.attributes['name'] == 'keywords' and node.attributes['content'] is not None:
                            keyws.append(node.attributes['content'])
                if selector == 'p':
                    paragraphs.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'h1':
                    heads.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'h2':
                    heads.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'h3':
                    heads.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'h4':
                    heads.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'h5':
                    heads.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'h6':
                    heads.append(str(" ".join(node.text(separator=' ').split(' '))))
                if selector == 'a' and 'href' in node.attributes and 'title' in node.attributes:
                    links.append(str(node.attributes['href']) + "\|" + str(node.attributes['title']))

        return "<p>".join(paragraphs), "<h>".join(heads), "<t>".join(links), "<k>".join(keyws)

    def _read_doc(self, record):
        url = record.rec_headers.get_header('WARC-Target-URI')[4:]
        paragraphs = None
        heads = None
        titles = None
        keywords = None
        if url:
            payload = record.content_stream().read()
            html = payload
            if len(html) > 0:
                paragraphs, heads, titles, keywords = self._parse_selectolax(html)
        return url, paragraphs, heads, titles, keywords

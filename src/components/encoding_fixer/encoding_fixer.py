from document import Document
import ftfy
from typing import Iterable


class EncodingFixer:

    def fix_encoding(self, documents: Iterable[Document]) -> Iterable[Document]:
        # TODO: Study defaults
        # https://ftfy.readthedocs.io/en/latest/
        # ftfy.fix_text(text, *, fix_entities='auto', remove_terminal_escapes=True, fix_encoding=True,
        #              fix_latin_ligatures=True, fix_character_width=True, uncurl_quotes=True, fix_line_breaks=True,
        #              fix_surrogates=True, remove_control_chars=True, remove_bom=True, normalization='NFC',
        #              max_decode_length=1000000)
        # Also: Consider adding heuristics from https://github.com/PlanTL-SANIDAD/utils/tree/master/FixEncodingErrors
        for doc in documents:
            doc.content = ftfy.fix_text(doc.content)
            yield doc


def test():
    from components.data_parser.bsc_crawl_json_parser import BSCCrawlJSONParser
    import os
    file_dir = os.path.join('..', '..', '..', 'test', 'bne')
    parser = BSCCrawlJSONParser(file_dir)
    documents = parser.parse()
    encoding = EncodingFixer()
    documents = encoding.fix_encoding(documents)

    # Show the first document
    for idx, doc in enumerate(documents):
        print(f'DOC {idx}: {doc.content}\n')
        if idx == 1:
            break


if __name__ == '__main__':
    test()

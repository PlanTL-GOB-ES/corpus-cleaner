from document import Document
from typing import Iterable
from components.data_parser.bsc_crawl_json_parser import BSCCrawlJSONParser
import sentence_splitter


# The split method does not use the self parameter, meaning that the
# implementation as method class is not necessary
class SentenceSplitter:
    @staticmethod
    def split(documents: Iterable[Document], language: str) -> Iterable[Document]:
        splitter = _get_sentence_splitter(language)
        for doc in documents:
            sentences = []
            for sent in splitter.split(doc.content):
                sentences.append(sent)
            doc.sentences = sentences
            yield doc


def _get_sentence_splitter(language: str):
    return sentence_splitter.SentenceSplitter(language=language)


def test():
    file_dir = '../../../test/bne'
    # parse documents
    parser = BSCCrawlJSONParser(file_dir)
    documents_parsed = parser.parse()

    # apply sentence splitting
    splitter = SentenceSplitter()
    documents_splitted = splitter.split(documents_parsed, language='es')

    # Show the first three documents
    for idx, doc in enumerate(documents_splitted):
        print(f'DOC {idx}: {doc.sentences}\n')
        if idx == 2:
            break


if __name__ == '__main__':
    test()

from document import Document
from typing import Iterable
import sentence_splitter
from components.cleaner_component import CleanerComponent
import argparse


# Use leading underscore to distinguish the class from the 'sentence_splitter' module class 'SentenceSplitter'
class SentenceSplitterComponent(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, language: str):
        self.language = language
        self.splitter = self._get_sentence_splitter()

    def split(self, documents: Iterable[Document]) -> Iterable[Document]:
        for idx, doc in enumerate(documents):
            sentences = []
            for sent in self.splitter.split(doc.content):
                sentences.append(sent)
            doc.sentences = sentences
            yield doc

    def _get_sentence_splitter(self):
        return sentence_splitter.SentenceSplitter(language=self.language)


def test():
    from components.data_parser.bsc_crawl_json_parser import BSCCrawlJSONParser
    import os
    file_dir = os.path.join('..', '..', '..', 'test', 'bne')
    # parse documents
    parser = BSCCrawlJSONParser(file_dir)
    documents_parsed = parser.parse()

    # apply sentence splitting
    splitter = SentenceSplitterComponent(language='es')
    documents_splitted = splitter.split(documents_parsed)

    # Show the first two documents
    for idx, doc in enumerate(documents_splitted):
        print(f'DOC {idx}: {doc.sentences}\n')
        if idx == 1:
            break


if __name__ == '__main__':
    test()

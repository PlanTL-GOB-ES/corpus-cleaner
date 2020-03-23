from document import Document
from typing import Iterable, Union
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

    def __init__(self, **kwargs):
        self.splitter_dict = {}

    def _split(self, documents: Iterable[Document]) -> Iterable[Document]:
        for idx, doc in enumerate(documents):
            if doc.language in self.splitter_dict:
                splitter = self.splitter_dict[doc.language]
            else:
                self.splitter_dict[doc.language]
                splitter = self.splitter_dict[doc.language]
            sentences = []
            for sent in splitter.split(doc.content):
                sentences.append(sent)
            doc.sentences = sentences
            yield doc

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._split(documents)


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

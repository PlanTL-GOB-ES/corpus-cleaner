from corpus_cleaner.document import Document
from typing import Iterable, Union
import sentence_splitter
from corpus_cleaner.components.cleaner_component import CleanerComponent
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

    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.splitter_dict = {}

    def _split(self, documents: Iterable[Document]) -> Iterable[Document]:
        for idx, doc in enumerate(documents):
            if doc.language in self.splitter_dict:
                splitter = self.splitter_dict[doc.language]
            else:
                self.splitter_dict[doc.language] = sentence_splitter.SentenceSplitter(language=doc.language)
                splitter = self.splitter_dict[doc.language]
            sentences = []
            for sent in splitter.split(doc.content):
                sentences.append(sent)
            doc.sentences = sentences
            yield doc

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._split(documents)

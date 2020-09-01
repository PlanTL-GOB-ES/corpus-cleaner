from corpus_cleaner.document import Document
from typing import Optional
import sentence_splitter
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import argparse


class SentenceSplitterComponent(CleanerComponentMapper):
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

    def _split(self, document: Optional[Document]) -> Optional[Document]:
        if document.language in self.splitter_dict:
            splitter = self.splitter_dict[document.language]
        elif document.language is None:
            if self.args.lang_filter is not None:
                self.splitter_dict[self.args.lang_filter[0]] = \
                    sentence_splitter.SentenceSplitter(language=self.args.lang_filter[0])
                splitter = self.splitter_dict[self.args.lang_filter[0]]
            else:
                self.splitter_dict['en'] = \
                    sentence_splitter.SentenceSplitter(language='en')
                splitter = self.splitter_dict['en']

        else:
            self.splitter_dict[document.language] = sentence_splitter.SentenceSplitter(language=document.language)
            splitter = self.splitter_dict[document.language]
        sentences = []
        for sent in splitter.split(document.content):
            sentences.append(sent)
        document.sentences = sentences
        return document

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._split(document)

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
                try:
                    self.splitter_dict[self.args.lang_filter[0]] = \
                        sentence_splitter.SentenceSplitter(language=self.args.lang_filter[0])
                    splitter = self.splitter_dict[self.args.lang_filter[0]]
                except:
                    self.splitter_dict['en'] = \
                        sentence_splitter.SentenceSplitter(language='en')
                    splitter = self.splitter_dict['en']
            else:
                self.splitter_dict['en'] = \
                    sentence_splitter.SentenceSplitter(language='en')
                splitter = self.splitter_dict['en']

        else:
            try:
                self.splitter_dict[self.args.lang_filter[0]] = \
                    sentence_splitter.SentenceSplitter(language=self.args.lang_filter[0])
                splitter = self.splitter_dict[self.args.lang_filter[0]]
            except:
                self.splitter_dict[document.language] = sentence_splitter.SentenceSplitter(language='en')
                splitter = self.splitter_dict[document.language]

        if self.debug:
            if not document.content:
                # If the document received is empty since has been filtered out in the previous step,
                # but the debug mode is activated, store a number of empty cleaned sentences equal to
                # the number of lines in the original content
                empty_sentences_number = len(document.content_orig.splitlines())
                document.sentences = [''] * empty_sentences_number
                document.sentences_orig = document.content_orig.splitlines()
            else:
                document.sentences = [sent for sent in splitter.split(document.content)]
                document.sentences_orig = [sent for sent in splitter.split(document.content_orig)]

                if len(document.sentences) > 1:
                    document.operations.append(f'{self.__class__.__name__}-_sentence_splitter')

                # If the original sentences are not aligned to the cleaned ones, place the whole document on the first
                # line to allow manual alignment
                if not len(document.sentences) == len(document.sentences_orig):
                    if len(document.sentences) > len(document.sentences_orig):
                        content_orig = document.content_orig.replace('\n', '')
                        document.sentences_orig = [f'UNALIGNED:{content_orig}']
                        document.sentences_orig.extend(['UNALIGNED:'] * (len(document.sentences) - len(document.sentences_orig)))
                    else:
                        return None
            # add operations for each sentence in the document
            document.operations = [document.operations.copy() for _ in range(len(document.sentences))]
        else:
            document.sentences = [sent for sent in splitter.split(document.content)]
        return document

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._split(document)

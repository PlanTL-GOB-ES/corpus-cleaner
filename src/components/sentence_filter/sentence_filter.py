from document import Document
from typing import Iterable, Union
from components.data_parser.bsc_crawl_json_parser import BSCCrawlJSONParser
from components.sentence_splitter_component.sentence_splitter_component import SentenceSplitterComponent
from components.cleaner_component import CleanerComponent
import argparse


class SentenceFilter(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--char-length-filter-sentence', type=int, default=30,
                            help='filter sentences shorter than a given minimum character length')
        parser.add_argument('--profanity-check', action='store_true',
                            help='filter sentences with sensible content')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def __init__(self, args: argparse.Namespace, char_length_filter_sentence: int = 30, profanity_check: bool = True):
        self.char_length_filter_sentence = args.char_length_filter_sentence if args.char_length_filter_sentence is not \
                                                                               None else char_length_filter_sentence
        self.profanity_check = args.profanity_check if args.profanity_check is not None else profanity_check
        self.filters = []
        self._get_filters()

    def filter(self, documents: Iterable[Document]) -> Iterable[Document]:
        for doc in documents:
            sentences_filtered = []
            for sent in doc.sentences:
                # keep only sentences that are not filtered out by all the filters
                if all(_filter(sent) for _filter in self.filters):
                    sentences_filtered.append(sent)
            # return the document if contains at least one sentence
            if sentences_filtered:
                doc.sentences = sentences_filtered
                yield doc

    def _get_filters(self):
        if self.char_length_filter_sentence:
            self.filters.append(self._check_char_len)

    def _check_char_len(self, sentence: str) -> bool:
        if len(sentence) > self.char_length_filter_sentence:
            return True
        else:
            return False

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self.filter(documents)


def test():
    file_dir = '../../../test/bne'
    # parse documents
    parser = BSCCrawlJSONParser(file_dir)
    documents_parsed = parser.parse()

    # apply sentence splitting
    splitter = SentenceSplitterComponent(language='es')
    documents_splitted = splitter.split(documents_parsed)

    # apply sentence filtering
    sentence_filter = SentenceFilter(char_length_filter_sentence=1)
    documents_sentence_filtered = sentence_filter.filter(documents_splitted)

    # Show the first two documents
    for idx, doc in enumerate(documents_sentence_filtered):
        print(f'DOC {idx} (sentences filtered): {doc.sentences}\n')

        if idx == 1:
            break


if __name__ == '__main__':
    test()

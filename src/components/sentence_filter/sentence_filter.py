from document import Document
from typing import Iterable
from components.data_parser.bsc_crawl_json_parser import BSCCrawlJSONParser
from components.sentence_splitter._sentence_splitter import _SentenceSplitter


class SentenceFilter:
    def __init__(self, max_char_len: int, profanity_check: bool = True):
        self.max_char_len = max_char_len
        self.profanity_check = profanity_check
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
        if self.max_char_len:
            self.filters.append(self._check_max_char_len)

    def _check_max_char_len(self, sentence: str) -> bool:
        if len(sentence) > self.max_char_len:
            return True
        else:
            return False


def test():
    file_dir = '../../../test/bne'
    # parse documents
    parser = BSCCrawlJSONParser(file_dir)
    documents_parsed = parser.parse()

    # apply sentence splitting
    splitter = _SentenceSplitter(language='es')
    documents_splitted = splitter.split(documents_parsed)

    # apply sentence filtering
    sentence_filter = SentenceFilter(max_char_len=1)
    documents_sentence_filtered = sentence_filter.filter(documents_splitted)

    # Show the first two documents
    for idx, doc in enumerate(documents_sentence_filtered):
        print(f'DOC {idx} (sentences filtered): {doc.sentences}\n')

        if idx == 1:
            break


if __name__ == '__main__':
    test()

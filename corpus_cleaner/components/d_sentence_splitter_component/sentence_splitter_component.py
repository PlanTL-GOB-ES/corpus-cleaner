from corpus_cleaner.document import Document, DiscardedDocument
from typing import Optional
import sentence_splitter
from dataclasses import dataclass
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from typing import Union, Tuple


@dataclass
class SentenceSplitterConfig:
    target_langs: Union[Tuple[str], None] = None  # Target languages. PREVIOUSLY: --lang-


class SentenceSplitterComponent(CleanerComponentMapper):
    def __init__(self, config: SentenceSplitterConfig):
        super().__init__()
        self._config = config
        self.splitter_dict = {}

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        if document.language in self.splitter_dict:
            splitter = self.splitter_dict[document.language]
        elif document.language is None:
            if self._config.target_langs is not None:
                try:
                    self.splitter_dict[self._config.target_langs[0]] = \
                        sentence_splitter.SentenceSplitter(language=self._config.target_langs[0])
                    splitter = self.splitter_dict[self._config.target_langs[0]]
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
                self.splitter_dict[self._config.target_langs[0]] = \
                    sentence_splitter.SentenceSplitter(language=self._config.target_langs[0])
                splitter = self.splitter_dict[self._config.target_langs[0]]
            except:
                self.splitter_dict[document.language] = sentence_splitter.SentenceSplitter(language='en')
                splitter = self.splitter_dict[document.language]

        # If the document received is empty since has been filtered out in the previous step,
        # store a number of empty cleaned sentences equal to the number of lines in the original content
        if isinstance(document, DiscardedDocument):
            empty_sentences_number = len(document.content.splitlines())
            document.sentences_cleaned = [''] * empty_sentences_number
            document.sentences = document.content.splitlines()
        else:
            document.sentences_cleaned = [sent for sent in splitter.split(document.content_cleaned)]
            document.sentences = [sent for sent in splitter.split(document.content)]
            if len(document.sentences_cleaned) > 1:
                document.register_operation(f'{self.__class__.__name__}-SentenceSplitter')

            # If the original sentences are not aligned to the cleaned ones, place the whole document on the first
            # line to allow manual alignment
            if len(document.sentences_cleaned) != len(document.sentences):
                content_one_line = document.content.replace('\n', '')
                document.sentences = [f'UNALIGNED:{content_one_line}']  # make sure the original content is one line
                document.sentences.extend(
                    ['UNALIGNED:'] * (len(document.sentences_cleaned) - len(document.sentences)))

        # add operations for each sentence in the document
        document.operations = [document.operations.copy() for _ in range(len(document.sentences_cleaned))]

        return document

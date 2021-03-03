from corpus_cleaner.document import Document
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

        # TODO: implemente debug param
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
                        document.sentences_orig.extend(
                            ['UNALIGNED:'] * (len(document.sentences) - len(document.sentences_orig)))
                    else:
                        return None
            # add operations for each sentence in the document
            document.operations = [document.operations.copy() for _ in range(len(document.sentences))]
        else:
            document.sentences = [sent for sent in splitter.split(document.content)]
        return document

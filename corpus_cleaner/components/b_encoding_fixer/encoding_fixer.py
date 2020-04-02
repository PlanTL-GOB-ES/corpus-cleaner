from corpus_cleaner.document import Document
import ftfy
from typing import Iterable
from corpus_cleaner.components.cleaner_component import CleanerComponent
import argparse
from typing import Union
from tqdm import tqdm


class EncodingFixer(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _fix_encoding(self, documents: Iterable[Document]) -> Iterable[Document]:
        # TODO: Study defaults
        # https://ftfy.readthedocs.io/en/latest/
        # ftfy.fix_text(text, *, fix_entities='auto', remove_terminal_escapes=True, fix_encoding=True,
        #              fix_latin_ligatures=True, fix_character_width=True, uncurl_quotes=True, fix_line_breaks=True,
        #              fix_surrogates=True, remove_control_chars=True, remove_bom=True, normalization='NFC',
        #              max_decode_length=1000000)
        # Also: Consider adding heuristics from https://github.com/PlanTL-SANIDAD/utils/tree/master/FixEncodingErrors
        # self.logger.info('Fixing encoding errors')
        for doc in documents:
            doc.content = ftfy.fix_text(doc.content, normalization='NFKD')
            yield doc

    def apply(self, documents: Union[Iterable[Document], None]) -> Union[Iterable[Document], None]:
        return self._fix_encoding(documents)


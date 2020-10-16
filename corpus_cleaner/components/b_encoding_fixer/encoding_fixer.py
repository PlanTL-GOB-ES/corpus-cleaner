from corpus_cleaner.document import Document
import ftfy
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
import argparse
from typing import Optional


class EncodingFixer(CleanerComponentMapper):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _fix_encoding(self, document: Optional[Document]) -> Optional[Document]:
        # TODO: Study defaults
        # https://ftfy.readthedocs.io/en/latest/
        # ftfy.fix_text(text, *, fix_entities='auto', remove_terminal_escapes=True, fix_encoding=True,
        #              fix_latin_ligatures=True, fix_character_width=True, uncurl_quotes=True, fix_line_breaks=True,
        #              fix_surrogates=True, remove_control_chars=True, remove_bom=True, normalization='NFC',
        #              max_decode_length=1000000)
        # Also: Consider adding heuristics from https://github.com/PlanTL-SANIDAD/utils/tree/master/FixEncodingErrors
        # TODO: initialize the attribute operations in the Document class
        document.operations = []
        document.content = ftfy.fix_text(document.content, normalization='NFKC').replace('\x92', "'")
        if document.content_orig != document.content:
            document.operations.append(f'{self.__class__.__name__}-_fix_encoding')
        return document

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._fix_encoding(document)


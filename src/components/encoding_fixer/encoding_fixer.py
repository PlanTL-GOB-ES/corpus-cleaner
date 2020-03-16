from document import Document
import ftfy


class EncodingFixer:

    def fix_encoding(self, doc: Document) -> Document:
        # TODO: Study defaults
        # https://ftfy.readthedocs.io/en/latest/
        # ftfy.fix_text(text, *, fix_entities='auto', remove_terminal_escapes=True, fix_encoding=True,
        #              fix_latin_ligatures=True, fix_character_width=True, uncurl_quotes=True, fix_line_breaks=True,
        #              fix_surrogates=True, remove_control_chars=True, remove_bom=True, normalization='NFC',
        #              max_decode_length=1000000)
        # Also: Consider adding heuristics from https://github.com/PlanTL-SANIDAD/utils/tree/master/FixEncodingErrors
        doc.content = ftfy.fix_text(doc.content)
        return doc

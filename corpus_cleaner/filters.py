from alphabet_detector import AlphabetDetector
from typing import Union, Tuple, Optional
import fasttext
import re
import os


class StringFilter:

    def filter(self, text: str) -> bool:
        raise NotImplementedError

    def __call__(self, text: str) -> bool:
        return self.filter(text)


class FilterByCharLen(StringFilter):
    def __init__(self, char_length_filter_document):
        self.char_length_filter_document = char_length_filter_document

    def filter(self, text: str) -> bool:
        value = len(text)
        if value < self.char_length_filter_document:
            return False
        return True


class FilterByDigits:
    def __init__(self, digits_filter: float):
        self.digits_filter = digits_filter

    def filter(self, text: str):
        value = sum(c.isdigit() for c in text) / len(text)
        if value > self.digits_filter:
            return False
        return True


class FilterByAlphanum:
    def __init__(self, alphanum_filter: float):
        self.alphanum_filter = alphanum_filter

    def filter(self, text: str):
        concat_content = ''.join(text.split())
        value = (1 - (sum(c.isalnum() for c in concat_content) / len(concat_content)))
        if value > self.alphanum_filter:
            return False
        return True


class FilterByLangChars:
    def __init__(self, alphabet, lang_chars_filter: float):
        self.alphabet = alphabet
        self.lang_chars_filter = lang_chars_filter

    def filter(self, text: str):
        concat_content = ''.join(text.split())
        value = (1 - (sum(c in self.alphabet for c in concat_content) / len(concat_content)))
        if value > self.lang_chars_filter:
            return False
        return True


class FilterByUppercase:
    def __init__(self, uppercase_filter: int):
        self.uppercase_filter = uppercase_filter

    def filter(self, text: str):
        value = sum(c.isupper() for c in text) / len(text)
        if value > self.uppercase_filter:
            return False
        return True


class FilterByAlphabet:
    def __init__(self, alphabet_filter: Union[Tuple[str], None]):
        self.ad = AlphabetDetector()
        self.alphabet_filter = alphabet_filter

    def filter(self, text: str):
        # TODO: Check thresholds?
        try:
            value = len(self.ad.detect_alphabet(text).intersection(set(self.alphabet_filter)))
            if value == 0:
                return False
        # TODO: catch proper exception
        except Exception:
            return True
        return True


class FilterByDict:
    def __init__(self, dictionary_filter: Optional[str]):
        self.dictionary_filter_pattern = re.compile("|".join(dictionary_filter))

    def _filter_by_dict(self, text: str):
        if self.dictionary_filter_pattern.search(text):
            return False
        return True


# TOFIX: this filter needs a document objects as input
class FilterByHeads(StringFilter):
    def filter(self, text: str) -> bool:
        value = []
        if doc.heads is not None:
            for token in ['found', '404', 'robots.txt', 'error', 'trouvée']:
                if re.search(token, doc.heads, re.IGNORECASE):
                    value.append(token)
                    return False
        return True


# TOFIX: this filter needs a document objects as input
class FilterByLang:
    def __init__(self, lang_filter: str, initial_lang_filter_threshold: float):
        self.url_placeholder_pattern = re.compile(
            "((\w+):\/\/)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
        )
        self.no_eols_pattern = re.compile('\n')
        self.fasttext_lid = fasttext.load_model(os.path.join('lib', 'lid.176.bin'))
        self.lang_filter = lang_filter
        self.initial_lang_filter_threshold = initial_lang_filter_threshold

    def fitler(self, text: str):
        content = self.url_placeholder_pattern.sub('', text)
        content = self.no_eols_pattern.sub('. ', content)
        res = self.fasttext_lid.predict(content)
        lang = res[0][0][-2:]
        conf = res[1][0]
        if lang in self.lang_filter and conf > self.initial_lang_filter_threshold:
            doc.language = lang
            return True
        value = f"({round(conf, 2)}, {lang})"
        return False, value

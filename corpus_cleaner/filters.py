from alphabet_detector import AlphabetDetector
from typing import Union, Tuple, Optional
import fasttext
import re
import os
from corpus_cleaner.document import Document


class StringFilter:

    def filter(self, text: str) -> bool:
        raise NotImplementedError

    def __call__(self, text: str) -> bool:
        return self.filter(text)


class CharLenStringFilter(StringFilter):
    def __init__(self, char_length_threshold: int):
        self._char_length_threshold = char_length_threshold

    def filter(self, text: str) -> bool:
        value = len(text)
        if value < self._char_length_threshold:
            return False
        return True


class DigitsStringFilter(StringFilter):
    def __init__(self, digits_percentage_threshold: float):
        self._digits_percentage_threshold = digits_percentage_threshold

    def filter(self, text: str):
        value = sum(c.isdigit() for c in text) / len(text)
        if value > self._digits_percentage_threshold:
            return False
        return True


class AlphanumStringFilter(StringFilter):
    def __init__(self, alphanum_percentage_threshold: float):
        self._alphanum_percentage_threshold = alphanum_percentage_threshold

    def filter(self, text: str):
        concat_content = ''.join(text.split())
        value = (1 - (sum(c.isalnum() for c in concat_content) / len(concat_content)))
        if value > self._alphanum_percentage_threshold:
            return False
        return True


class LangCharsStringFilter(StringFilter):
    def __init__(self, alphabet, lang_chars_percentage_threshold: float):
        self._alphabet = alphabet
        self._lang_chars_percentage_threshold = lang_chars_percentage_threshold

    def filter(self, text: str):
        concat_content = ''.join(text.split())
        value = (1 - (sum(c in self._alphabet for c in concat_content) / len(concat_content)))
        if value > self._lang_chars_percentage_threshold:
            return False
        return True


class UppercaseStringFilter(StringFilter):
    def __init__(self, uppercase_percentage_threshold: float):
        self._uppercase_percentage_threshold = uppercase_percentage_threshold

    def filter(self, text: str):
        value = sum(c.isupper() for c in text) / len(text)
        if value > self._uppercase_percentage_threshold:
            return False
        return True


class AlphabetFilter(StringFilter):
    def __init__(self, alphabets: Union[Tuple[str], None]):
        self._ad = AlphabetDetector()
        self._alphabets = alphabets

    def filter(self, text: str):
        # TODO: Check thresholds?
        try:
            value = len(self._ad.detect_alphabet(text).intersection(set(self._alphabets)))
            if value == 0:
                return False
            else:
                return True
        # TODO: catch proper exception
        except Exception:
            return True


class DictStringFilter(StringFilter):
    def __init__(self, dictionary_terms: Optional[str]):
        self._dictionary_filter_pattern = re.compile("|".join(dictionary_terms))  # TODO: What are these terms? Lines?

    def filter(self, text: str):
        if self._dictionary_filter_pattern.search(text):
            return False
        return True


class MetadataFilter:

    def filter(self, doc: Document) -> bool:
        raise NotImplementedError

    def __call__(self, doc: Document) -> bool:
        return self.filter(doc)


class HeadsMetadataFilter(MetadataFilter):
    def filter(self, doc: Document) -> bool:
        value = []
        if doc.heads is not None:
            for token in ['found', '404', 'robots.txt', 'error', 'trouvée']:
                if re.search(token, doc.heads, re.IGNORECASE):
                    value.append(token)
                    return False
        return True


class LangIdentifier:

    def filter(self, text: str) -> Tuple[bool, float]:
        raise NotImplementedError

    def __call__(self, text: str) -> Tuple[bool, float]:
        return self.filter(text)

# TOFIX: this filter needs a document objects as input
class FilterByLang:
    def __init__(self, lang_filter: str, initial_lang_filter_threshold: float, replace_urls: bool):
        self.replace_urls = replace_urls
        if self.replace_urls:
            self.url_placeholder_pattern = re.compile('\s+\[URL\]')
        else:
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

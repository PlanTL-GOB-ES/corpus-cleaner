from alphabet_detector import AlphabetDetector
from typing import Union, Tuple, Optional, List, Set
import re
from corpus_cleaner.document import Document
from corpus_cleaner.lang_identifier import FasttextLangIdentifier, LangIdLangIdentifier


class StringFilter:

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        """
        Check whether to keep a text.
        :param text: Text to filter
        :return: Tuple result, reason, where result is True iff the text is okay, and False otherwise, and reason is
        the reason why it was filtered (e.g., value checked against the threshold).
        """
        raise NotImplementedError

    def __call__(self, text: str) -> Tuple[bool, Optional[str]]:
        return self.keep(text)


class CharLenStringFilter(StringFilter):
    def __init__(self, char_length_threshold: int):
        self._char_length_threshold = char_length_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        value = len(text)
        res = value > self._char_length_threshold
        return res, str(value)


# TODO: this filter include the CharLenStringFilter!
class LenStringFilter(StringFilter):
    def __init__(self, char_length_threshold: int, word_length_threshold: int):
        self._char_length_threshold = char_length_threshold
        self._word_length_threshold = word_length_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        len_sentence = len(text)
        len_words = len(text.split(' '))
        if len_sentence < self._char_length_threshold and len_words < self._word_length_threshold:
            value = f"({round(len_sentence)} chars, {len_words} words)"
            return False, str(value)
        return True, None


class DigitsStringFilter(StringFilter):
    def __init__(self, digits_percentage_threshold: float):
        self._digits_percentage_threshold = digits_percentage_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        value = sum(c.isdigit() for c in text) / len(text)
        res = value < self._digits_percentage_threshold
        return res, str(value)


class AlphanumStringFilter(StringFilter):
    def __init__(self, alphanum_percentage_threshold: float):
        self._alphanum_percentage_threshold = alphanum_percentage_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        concat_content = ''.join(text.split())
        value = (1 - (sum(c.isalnum() for c in concat_content) / len(concat_content)))
        res = value > self._alphanum_percentage_threshold
        return res, str(value)


class LangCharsStringFilter(StringFilter):
    def __init__(self, alphabet, lang_chars_percentage_threshold: float):
        self._alphabet = alphabet
        self._lang_chars_percentage_threshold = lang_chars_percentage_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        concat_content = ''.join(text.split())
        value = (1 - (sum(c in self._alphabet for c in concat_content) / len(concat_content)))
        res = value > self._lang_chars_percentage_threshold
        return res, str(value)


class UppercaseStringFilter(StringFilter):
    def __init__(self, uppercase_percentage_threshold: float):
        self._uppercase_percentage_threshold = uppercase_percentage_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        value = sum(c.isupper() for c in text) / len(text)
        res = value < self._uppercase_percentage_threshold
        return res, str(value)


class AlphabetFilter(StringFilter):
    def __init__(self, alphabets: Union[Tuple[str], None]):
        self._ad = AlphabetDetector()
        self._alphabets = alphabets

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        # TODO: Check thresholds?
        try:
            value = len(self._ad.detect_alphabet(text).intersection(set(self._alphabets)))
            return value != 0, str(value)
        # TODO: catch proper exception
        except Exception:
            return True, None


class DictStringFilter(StringFilter):
    def __init__(self, dictionary_terms: List[str]):
        self._dictionary_filter_pattern = re.compile("|".join(dictionary_terms))  # TODO: What are these terms? Lines?

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        if self._dictionary_filter_pattern.search(text):
            return False, None
        return True, None


class CodeStringFilter(StringFilter):
    def __init__(self, code_threshold: float):
        self._code_keywords_pattern = re.compile('\\b(var|function|const|if|else|script)\\b')
        self._code_chars_pattern = re.compile(r'[;=&\[\](){}/\\\\]')
        self._code_threshold = code_threshold

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        value = (len(re.findall(self._code_keywords_pattern, text)) / len(text.split())) \
                + len(re.findall(self._code_chars_pattern, text)) / len(text)
        if value > self._code_threshold:
            return False, str(value)
        return True, None


class SrcTgtStringFilter(StringFilter):
    def __init__(self):
        self.src_tag_pattern = re.compile('src=')

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        found = self.src_tag_pattern.search(text)
        if found is not None:
            return False, str(found.span())
        return True, None


class CascadeLangStringFilter(StringFilter):
    def __init__(self, languages: Set[str], fast_lang_filter_threshold: float, slow_lang_filter_threshold: float,
                 replace_urls: bool):
        self._languages = languages
        self._fast_lang_filter_threshold = fast_lang_filter_threshold
        self._slow_lang_filter_threshold = slow_lang_filter_threshold

        # We set the cascade sequence to 1) fasttext and 2) langid for speed and accuracy reasons.
        self._language_id1 = FasttextLangIdentifier(replace_urls=replace_urls)
        self._language_id2 = LangIdLangIdentifier(replace_urls=replace_urls)

    def keep(self, text: str) -> Tuple[bool, Optional[str]]:
        lang, conf = self._language_id1.identify(text.lower())
        if lang in self._languages and conf > self._fast_lang_filter_threshold:
            return True, None

        elif lang in self._languages:
            lang, conf = self._language_id2.identify(text)
            if lang in self._languages and conf > self._slow_lang_filter_threshold:
                return True, None
            else:
                value = f"({round(conf, 2)}, {lang})"
                return False, value

        else:
            value = f"({round(conf, 2)}, {lang})"
            return False, value


class MetadataFilter:

    def filter(self, doc: Document) -> Tuple[bool, Optional[str]]:
        raise NotImplementedError

    def __call__(self, doc: Document) -> Tuple[bool, Optional[str]]:
        return self.filter(doc)


class HeadsMetadataFilter(MetadataFilter):
    def filter(self, doc: Document) -> Tuple[bool, Optional[str]]:
        if doc.heads is not None:
            for token in ['found', '404', 'robots.txt', 'error', 'trouvée']:
                if re.search(token, doc.heads, re.IGNORECASE):
                    return False, token
        return True, None

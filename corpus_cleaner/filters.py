from alphabet_detector import AlphabetDetector
from typing import Union, Tuple, Optional
import re
from corpus_cleaner.document import Document


class StringFilter:

    def keep(self, text: str) -> Tuple[bool, str]:
        """
        Check whether to keep a text.
        :param text: Text to filter
        :return: Tuple result, reason, where result is True iff the text is okay, and False otherwise, and reason is
        the reason why it was filtered (e.g., value checked against the threshold).
        """
        raise NotImplementedError

    def __call__(self, text: str) -> Tuple[bool, str]:
        return self.keep(text)


class CharLenStringFilter(StringFilter):
    def __init__(self, char_length_threshold: int):
        self._char_length_threshold = char_length_threshold

    def keep(self, text: str) -> Tuple[bool, str]:
        value = len(text)
        res = value < self._char_length_threshold
        return res, str(value)


class DigitsStringFilter(StringFilter):
    def __init__(self, digits_percentage_threshold: float):
        self._digits_percentage_threshold = digits_percentage_threshold

    def keep(self, text: str) -> Tuple[bool, str]:
        value = sum(c.isdigit() for c in text) / len(text)
        res = value > self._digits_percentage_threshold
        return res, str(value)


class AlphanumStringFilter(StringFilter):
    def __init__(self, alphanum_percentage_threshold: float):
        self._alphanum_percentage_threshold = alphanum_percentage_threshold

    def filter(self, text: str) -> bool:
        concat_content = ''.join(text.split())
        value = (1 - (sum(c.isalnum() for c in concat_content) / len(concat_content)))
        if value > self._alphanum_percentage_threshold:
            return False
        return True


class LangCharsStringFilter(StringFilter):
    def __init__(self, alphabet, lang_chars_percentage_threshold: float):
        self._alphabet = alphabet
        self._lang_chars_percentage_threshold = lang_chars_percentage_threshold

    def filter(self, text: str) -> bool:
        concat_content = ''.join(text.split())
        value = (1 - (sum(c in self._alphabet for c in concat_content) / len(concat_content)))
        if value > self._lang_chars_percentage_threshold:
            return False
        return True


class UppercaseStringFilter(StringFilter):
    def __init__(self, uppercase_percentage_threshold: float):
        self._uppercase_percentage_threshold = uppercase_percentage_threshold

    def filter(self, text: str) -> bool:
        value = sum(c.isupper() for c in text) / len(text)
        if value > self._uppercase_percentage_threshold:
            return False
        return True


class AlphabetFilter(StringFilter):
    def __init__(self, alphabets: Union[Tuple[str], None]):
        self._ad = AlphabetDetector()
        self._alphabets = alphabets

    def filter(self, text: str) -> bool:
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

    def filter(self, text: str) -> bool:
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

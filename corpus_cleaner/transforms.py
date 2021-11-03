
import ftfy
from typing import Iterable, Tuple, List
import re
from textnorm import normalize_space
import regex
from sacremoses import MosesPunctNormalizer

class StringTransform:

    def transform(self, text: str) -> str:
        raise NotImplementedError

    def __call__(self, text: str) -> str:
        return self.transform(text)
      

class FixEncodingStringTransform(StringTransform):
    def transform(self, text: str) -> str:
        # TODO: Study defaults
        # https://ftfy.readthedocs.io/en/latest/
        # ftfy.fix_text(text, *, fix_entities='auto', remove_terminal_escapes=True, fix_encoding=True,
        #              fix_latin_ligatures=True, fix_character_width=True, uncurl_quotes=True, fix_line_breaks=True,
        #              fix_surrogates=True, remove_control_chars=True, remove_bom=True, normalization='NFC',
        #              max_decode_length=1000000)
        # Also: Consider adding heuristics from https://github.com/PlanTL-SANIDAD/utils/tree/master/FixEncodingErrors
        return ftfy.fix_text(text, normalization='NFKC').replace('\x92', "'")


class LanguageNormalizationStringTransform(StringTransform):
    def __init__(self, langs: Iterable[str]):
        self._langs = langs
        self._geminate_l_pattern = re.compile(r'l\.l')

    def transform(self, text: str) -> str:
        if 'ca' in self._langs:
            text = self._geminate_l_pattern.sub('l·l', text)
        return text


class RemoveCitationsStringTransform(StringTransform):
    def __init__(self):
        self._remove_citations_pattern = re.compile(r'[,.]*\[[\d]{,3}\]')

    def transform(self, text: str) -> str:
        text = self._remove_citations_pattern.sub('', text)
        return text


class ReplaceEmailsStringTransform(StringTransform):
    def __init__(self, lang_chars: Tuple[str]):
        self._emails_pattern = re.compile(rf'[{lang_chars}0-9_.+-]+@[a-zA-Z0-9-]+\.[a-z0-9-.]+')
        self._replace = ' [EMAIL] '

    def transform(self, text: str) -> str:
        text = self._emails_pattern.sub(self._replace, text)
        return text


class RemoveHashtagsMentionsStringTransform(StringTransform):
    def __init__(self):
        self._remove_hashtags_pattern = re.compile('(@[A-Za-z0-9_]+)|(#[\w_]+)')

    def transform(self, text: str) -> str:
        text = self._remove_hashtags_pattern.sub(' ', text)
        return text


class RemoveTagsStringTransform(StringTransform):
    def __init__(self):
        self._tags_pattern = re.compile(' *(<.*?> ?)+ *')
        self._p_tags_pattern = re.compile('(\s*)(<p>)+')

    def transform(self, text: str) -> str:
        text = self._tags_pattern.sub(' ', self._p_tags_pattern.sub('\n', text))
        return text


class SpaceNormalizationTransform(StringTransform):
    def __init__(self, langs: List[str]):
        self._punc_no_space_pattern = re.compile("(\w+|\"|')([!,:;?])([a-zA-Z]\w)")
        if langs == ['ca']:
            self._punc_space_pattern = re.compile("(\s)([!,:;?.])")
            self._quote_no_space_pattern1 = re.compile("(\w)([«“\"])(\w+(\s\w+)*)([\"”»])")
            self._quote_no_space_pattern2 = re.compile("([«“\"])(\w+(\s\w+)*)([\"”»])(\w+)")
        else:
            self._punc_space_pattern = re.compile("(\s)([!',:;?.])")
            self._quote_no_space_pattern1 = re.compile("(\w)([«“'\"])(\w+(\s\w+)*)(['\"”»])")
            self._quote_no_space_pattern2 = re.compile("([«“'\"])(\w+(\s\w+)*)(['\"”»])(\w+)")
        self._zero_width_space_pattern = re.compile('\u200b')

    def transform(self, text: str) -> str:
        text = normalize_space(text, preserve=['\n'])
        text = self._punc_space_pattern.sub('\\2', text)
        text = self._zero_width_space_pattern.sub('', text)
        text = self._punc_no_space_pattern.sub('\\1\\2 \\3', text)
        text = self._quote_no_space_pattern1.sub('\\1 \\2\\3\\5', text)
        text = self._quote_no_space_pattern2.sub('\\1\\2\\4 \\5', text)
        return text


class SegSentencesStringTransform(StringTransform):
    def __init__(self):
        self._final_sentence_pattern1 = regex.compile(r"(\s)(\p{Ll}+)([.!?:]*)(\p{Lu})(\p{Ll}+)([\s.,;:?!])")
        self._final_sentence_pattern2 = regex.compile(r"(\s)(\p{Ll}+)([.!?:]+)('|\")(\p{Lu})(\p{Ll}+)([\s.,;:?!])")

    def transform(self, text: str) -> str:
        text = self._final_sentence_pattern1.subf("{1}{2}{3}\n{4}{5}{6}", text)
        text = self._final_sentence_pattern2.subf("{1}{2}{3}\n{4}{5}{6}{7}", text)
        return text


class ReplaceURLsStringTransform(StringTransform):
    def __init__(self, lang_chars: Tuple[str]):
        self._replace = ' [URL] '
        self._urls_pattern = re.compile(
            rf'\((@)?((http|https)://)?([{lang_chars}0-9./?\\\\@\-—_=#])+\.[a-z]{{2,6}}([{lang_chars}0-9&/\\\\+~*?%:!@—_=#()-])*')
        self._urls_pattern2 = re.compile('(\[URL\]\.?\w*\s*)+')

    def transform(self, text: str) -> str:
        text = self._urls_pattern2.sub(self._replace, self._urls_pattern.sub(self._replace, text))
        return text


class PunctuationNormalizationStringTransform(StringTransform):
    def __init__(self, lang: str):
        self._punct_normalizer = MosesPunctNormalizer(lang)

    def transform(self, text: str) -> str:
        return self._punct_normalizer.normalize(text)


class SpellCheckStringTransform:
    def transform(self, text: str) -> str:
        raise NotImplementedError


class TerminologyNormalizationStringTransform:
    def transform(self, text: str) -> str:
        raise NotImplementedError

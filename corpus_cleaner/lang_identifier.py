from typing import Tuple
import re
import fasttext
from corpus_cleaner.constants import FASTTEXT_PATH
from langid.langid import LanguageIdentifier, model


class LangIdentifier:
    def __init__(self, replace_urls: bool):
        super().__init__()
        self._replace_urls = replace_urls
        if self._replace_urls:
            self._url_placeholder_pattern = re.compile('\s+\[URL\]')
        else:
            self._url_placeholder_pattern = re.compile(
                "((\w+):\/\/)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)"
            )
        self._no_eols_pattern = re.compile('\n')

    def identify(self, text: str) -> Tuple[str, float]:
        raise NotImplementedError

    def __call__(self, text: str) -> Tuple[str, float]:
        content = self._url_placeholder_pattern.sub('', text)
        content = self._no_eols_pattern.sub('. ', content)
        return self.identify(content)


class FasttextLangIdentifier(LangIdentifier):
    def __init__(self, replace_urls: bool):
        super().__init__(replace_urls=replace_urls)
        self._fasttext_lid = fasttext.load_model(FASTTEXT_PATH)

    def identify(self, text: str) -> Tuple[str, float]:
        res = self._fasttext_lid.predict(text)
        lang = res[0][0][-2:]
        conf = res[1][0]
        return lang, conf


class LangIdLangIdentifier(LangIdentifier):
    def __init__(self, replace_urls: bool):
        super().__init__(replace_urls=replace_urls)
        self._lang_id = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        _ = self._lang_id.classify('')  # force init

    def identify(self, text: str) -> Tuple[str, float]:
        res = self._lang_id.classify(text)
        lang = res[0]
        conf = res[1]
        return lang, conf

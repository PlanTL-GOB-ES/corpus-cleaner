from corpus_cleaner.document import Document
from typing import Union, Dict, Optional
from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from corpus_cleaner.transforms import PunctuationNormalizationStringTransform
from dataclass import dataclass
from typing import Union, Tuple
from transforms import PunctuationNormalizationStringTransform, StringTransform


class NormalizerConfig:
    punctuation_norm: bool  # Apply punctuation normalization

    target_langs: Union[Tuple[str], None] = None  # Target languages. PREVIOUSLY: --lang-

    spell_check: bool  # Apply spell checking (not implemented)

    terminology_norm: Union[None, Dict[str, str]]  # Apply terminology normalization (not implemented)


class Normalizer(CleanerComponentMapper):
    def __init__(self, config: NormalizerConfig):
        super().__init__()
        self._config = config
        self._string_transforms = self._build_string_transforms()

    def _build_string_transforms(self):
        transforms = []
        if self._config.punctuation_norm:
            transforms.append(PunctuationNormalizationStringTransform(self._config.target_langs[0]))
        if self._config.spell_check:
            raise NotImplementedError
        if self._config.terminology_norm is not None:
            raise NotImplementedError
        return transforms

    def _normalize(self, document: Optional[Document]) -> Optional[Document]:
        sent_norms = []
        for idx_sent, sent in enumerate(document.sentences):
            sent_norm = sent
            for string_transform in self._string_transforms:
                sent_norm = string_transform(sent_norm)
                # TODO: implement debug param
                if self.debug and sent_norm:
                    if sent_norm != sent:
                        class_name = self.__class__.__name__
                        document.register_operation(operation=f"{class_name}-{string_transform.__name__}",
                                                    sublist_index=idx_sent)
            sent_norms.append(sent_norm)
        document.sentences = sent_norms
        return document

    def apply(self, document: Optional[Document]) -> Optional[Document]:
        return self._normalize(document)

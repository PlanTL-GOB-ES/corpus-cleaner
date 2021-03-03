from corpus_cleaner.components.cleaner_component_mapper import CleanerComponentMapper
from corpus_cleaner.configs.langs import langs
from dataclasses import dataclass
from corpus_cleaner.transforms import *
from corpus_cleaner.filters import *
from corpus_cleaner.lang_identifier import FasttextLangIdentifier
from corpus_cleaner import DiscardedDocument

@dataclass
class PreFiltererConfig:
    none_filter: bool = False  # Apply no filters.

    lang_filter: bool = True  # Apply language filter on documents. PREVIOUSLY: Don't write --no-lang-filter-document.

    language_normalization: bool = False  # Applying language-specific normalization. PREVIOUSLY: Don't write
    # --no-language-normalization.

    replace_emails: bool = True  # Replacing email addresses with "[EMAIL]". PREVIOUSLY: Don't write
    # --no-replace-emails.

    remove_hashtags_mentions: bool = True  # Remove hashtags and mentions. PREVIOUSLY: Don't write
    # --no-remove-hashtags-mentions.

    remove_tags: bool = True  # Removing XML/HTML tags. PREVIOUSLY: Don't write --no-remove-tags.

    space_normalization: bool = True  # normalizing white spaces. PREVIOUSLY: Don't write --no-space-normalization.

    replace_urls: bool = False  # Avoid replacing URLs with "[URL]". PREVIOUSLY: Don't write --no-replace-urls.

    char_length_filter: int = 40  # Minimum char length per document. Set to 0 not to apply any filter.

    head_filter: bool = False  # Filtering documents coming from a crawler (having a "heads" attribute) with
    # common HTTP errors. PREVIOUSLY: Don't write --no-head-filter.

    digits_filter: float = 0.1  # Maximum allowed proportion of digit characters.

    remove_citations: bool = False  # If used, remove citations in the common square brackets format, e.g [34].

    lang_chars_filter: float = 0.1  # Maximum allowed proportion of characters not belonging to the alphabet of the
    # language.

    alphanum_filter: float = 0.3  # Maximum allowed proportion of non-alphanumeric characters.

    uppercase_filter: float = 0.4  # Maximum allowed proportion of uppercase characters.

    alphabet_filter: Union[Tuple[str], None] = ('LATIN',)  # Maximum allowed proportion of non-alphanumeric characters.

    target_langs: Union[Tuple[str], None] = None  # Target languages. PREVIOUSLY: --lang-

    initial_lang_filter_threshold: float = 0.3  # 'If --lang-filter is set, minimum threshold for the initial lang
    # identifier.

    dictionary_filter: Optional[List[str]] = None  # Path to dictionary (plain text, one term per line of terms that
    # should not appear in a document). PREVIOUSLY: DO write dictionary_filter.

    seg_sentences: bool = False  # Segment wrongfully concatenated sentences (Example: "My name is Peter.I'm 30 years
    # old.")


class PreFilterer(CleanerComponentMapper):
    def __init__(self, config: PreFiltererConfig):
        super().__init__()
        self._config = config
        self._alphabet = set([])
        for lang in self._config.target_langs:
            self._alphabet.update(langs[lang]['alphabet'])
        self._lang_chars = tuple("".join(char for char in self._alphabet if char.isalpha()))
        self._metadata_filters = self._build_metadata_filters()
        self._string_transforms = self._build_string_transforms()
        self._string_filters = self._build_string_filters()
        # If string transforms already remove URLs, not required to do it again for the lang id. But the lang id
        # itself needs it to work properly
        self._lang_identifier = FasttextLangIdentifier(replace_urls=not self._config.replace_urls)

    def _build_metadata_filters(self) -> List[MetadataFilter]:
        filters = []

        if self._config.head_filter:
            filters.append(HeadsMetadataFilter())

        return filters

    def _build_string_transforms(self) -> List[StringTransform]:
        transforms = []

        if self._config.language_normalization:
            transforms.append(LanguageNormalizationStringTransform(langs=self._config.target_langs))

        if self._config.replace_emails:
            transforms.append(ReplaceEmailsStringTransform(lang_chars=self._lang_chars))

        if self._config.remove_hashtags_mentions:
            transforms.append(RemoveHashtagsMentionsStringTransform())

        if self._config.remove_tags:
            transforms.append(RemoveTagsStringTransform())

        if self._config.replace_urls:
            transforms.append(ReplaceURLsStringTransform(lang_chars=self._lang_chars))

        if self._config.space_normalization:
            transforms.append(SpaceNormalizationTransform(langs=list(self._config.target_langs)))

        if self._config.seg_sentences:
            transforms.append(SegSentencesStringTransform())

        if self._config.remove_citations:
            transforms.append(RemoveCitationsStringTransform())

        return transforms

    def _build_string_filters(self) -> List[StringFilter]:
        filters = [FixEncodingStringTransform()]

        if self._config.char_length_filter > 0:
            filters.append(CharLenStringFilter(char_length_threshold=self._config.char_length_filter))

        if self._config.digits_filter > 0:
            filters.append(DigitsStringFilter(digits_percentage_threshold=self._config.digits_filter))

        if self._config.alphanum_filter > 0:
            filters.append(AlphanumStringFilter(alphanum_percentage_threshold=self._config.alphanum_filter))

        if self._config.lang_chars_filter > 0:
            filters.append(LangCharsStringFilter(lang_chars_percentage_threshold=self._config.lang_chars_filter,
                                                 alphabet=self._alphabet))

        if self._config.uppercase_filter > 0:
            filters.append(UppercaseStringFilter(uppercase_percentage_threshold=self._config.uppercase_filter))

        if self._config.alphabet_filter is not None:
            filters.append(AlphabetFilter(alphabets=self._config.alphabet_filter))

        if self._config.dictionary_filter is not None:
            filters.append(DictStringFilter(dictionary_terms=self._config.dictionary_filter))

        return filters

    def apply(self, document: Document) -> Optional[Document]:
        # Metadata filters: based on document metadata (e.g., document.heads might contain "404" (Error 404), in which
        # case we can already discard it.
        for metadata_filter in self._metadata_filters:
            keep, reason = metadata_filter(document)
            if not keep:
                document_discarded = DiscardedDocument(document.content)
                document_discarded.register_operation(f"{self.__class__.__name__}-{metadata_filter.__class__.__name__}:{reason}")
                return document_discarded

        # String transforms. Transform document contents. (E.g., regex-based replaces).
        # String transforms modify the content of the documents, but they do not discard any of them.
        for string_transform in self._string_transforms:
            transformed = string_transform(document.content)
            if transformed != document.content:
                document_discarded = DiscardedDocument(document.content)
                document_discarded.register_operation(f"{self.__class__.__name__}-{string_transform.__class__.__name__}")
                document.content = transformed

        # If the result of the transformations is an empty document, then discard it.
        if len(document.content.split()) == 0:
            document_discarded = DiscardedDocument(document.content)
            document_discarded.register_operation(f"{self.__class__.__name__}-NoWordsLeftAtDocAfterTransformsDocument")
            return document_discarded

        # String filters. Don't modify documents, but decide whether to keep them.
        for string_filter in self._string_filters:
            keep, reason = string_filter(document.content)
            if not keep:
                document_discarded = DiscardedDocument(document.content)
                document_discarded.register_operation(f"{self.__class__.__name__}-{string_filter.__class__.__name__}:{reason}")
                return document_discarded

        # Language identifier. Similar to filter, but handled as a particular case since we do more complex stuff.
        # The first condition is for cases in which the document metadata already contained information on the language.
        if document.language and document.language not in self._config.target_langs:
            document_discarded = DiscardedDocument(document.content)
            document_discarded.register_operation(f"{self.__class__.__name__}-MetadataLanguage")
            return document_discarded
        if not document.language and self._config.lang_filter:
            lang, confidence = self._lang_identifier(document.content)
            if lang in self._config.target_langs and confidence > self._config.initial_lang_filter_threshold:
                document.language = lang  # Set inferred language.
            else:
                reason = f"({round(confidence, 2)}, {lang})"
                document_discarded = DiscardedDocument(document.content)
                document_discarded.register_operation(f"{self.__class__.__name__}-{self._lang_identifier.__class__.__name__}:"
                                            f"{reason}")
                return document_discarded
        else:
            return document
        return document

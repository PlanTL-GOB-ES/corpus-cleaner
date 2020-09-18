from typing import List
from typing import Optional


class Document:
    def __init__(self,
                 content: str,
                 sentences: Optional[List[str]] = None,
                 sentences_orig: Optional[List[str]] = None,
                 filename: Optional[str] = None,
                 title: Optional[str] = None,
                 url: Optional[str] = None,
                 id_: Optional[str] = None,
                 keywords: Optional[str] = None,
                 heads: Optional[str] = None,
                 language: Optional[str] = None):
        self.content = content
        self.content_orig = content
        self.sentences = sentences
        self.sentences_orig = sentences_orig
        self.title = title
        self.url = url
        self.id = id_
        self.keywords = keywords
        self.heads = heads
        self.filename = filename
        self.language = language

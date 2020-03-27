from typing import List


class Document:
    def __init__(self,
                 content: str,
                 sentences: List[str] = None,
                 filename: str = None,
                 title: str = None,
                 url: str = None,
                 id_: str = None,
                 keywords: str = None,
                 heads: str = None,
                 language: str = None):
        self.content = content
        self.sentences = sentences
        self.title = title
        self.url = url
        self.id = id_
        self.keywords = keywords
        self.heads = heads
        self.filename = filename
        self.language = language

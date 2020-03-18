class Document:
    def __init__(self,
                 content: str,
                 sentences: list = [],
                 filename: str = None,
                 title: str = None,
                 url: str = None,
                 id_: str = None,
                 keywords: str = None,
                 heads: str = None):
        self.content = content
        self.sentences = sentences
        self.title = title
        self.url = url
        self.id = id_
        self.keywords = keywords
        self.heads = heads
        self.filename = filename

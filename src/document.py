class Document:
    def __init__(self, content: str, filename: str = None, title: str = None, url: str = None, id_: str = None, keywords: str = None,
                 heads: str = None):
        self.content = content
        self.title = title
        self.url = url
        self.id = id_
        self.keywords = keywords
        self.heads = heads
        self.filename = filename

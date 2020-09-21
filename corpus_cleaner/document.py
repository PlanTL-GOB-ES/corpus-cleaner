from typing import List
from typing import Optional

class Document:
    def __init__(self,
                 content: str,
                 sentences: Optional[List[str]] = None,
                 filename: Optional[str] = None,
                 title: Optional[str] = None,
                 url: Optional[str] = None,
                 id_: Optional[str] = None,
                 keywords: Optional[str] = None,
                 heads: Optional[str] = None,
                 language: Optional[str] = None):
        self.content = content
        self.sentences = sentences
        self.title = title
        self.url = url
        self.id = id_
        self.keywords = keywords
        self.heads = heads
        self.filename = filename
        self.language = language

    def attr_str(self) -> str:
        res = []
        if self.title is not None:
            res.append(('title', self.title))
        if self.url is not None:
            res.append(('url', self.url))
        if self.id is not None:
            res.append(('id', self.id))
        if self.heads is not None:
            res.append(('heads', self.heads))
        if self.keywords is not None:
            res.append(('keywords', self.keywords))
        if self.filename is not None:
            res.append(('filename', self.filename))
        if self.language is not None:
            res.append(('language', self.language))
        s = ''
        for e in res:
            s += f'{e[0]}="{e[1]}" '
        return s[:-1]

    @classmethod
    def parse_str(cls, s):

        attr_dict = {}
        key = ''
        value = ''
        is_key = True
        for c in s:
            if not is_key and c == '=':
                is_key = False
            elif is_key:
                key += c
            elif c.isspace():
                attr_dict[key] = value[1:-1]
                key = ''
                value = ''
                is_key = True
            else:
                value += c
        if len(key) > 0 and len(value) > 0:
            attr_dict[key] = value[1:-1]

        def get_att(att_name):
            return attr_dict[att_name] if att_name in attr_dict else None

        return Document(content='',
                        sentences=[],
                        filename=get_att('filename'),
                        title=get_att('title'),
                        url=get_att('url'),
                        id_=get_att('id'),
                        keywords=get_att('keywords'),
                        heads=get_att('heads'),
                        language=get_att('language')
                        )


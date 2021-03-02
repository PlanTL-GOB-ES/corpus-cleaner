from typing import List
from typing import Optional
from dataclasses import dataclass


@dataclass
class Document:
    content: str
    filename: Optional[str] = None
    sentences: Optional[List[str]] = None
    sentences_orig: Optional[List[str]] = None
    title: Optional[str] = None
    url: Optional[str] = None
    id_: Optional[str] = None
    keywords: Optional[str] = None
    heads: Optional[str] = None
    language: Optional[str] = None
    operations: Optional[List] = None

    def attr_str(self) -> str:
        res = []
        if self.title is not None:
            res.append(('title', self.title.replace('\n', ' ')))
        if self.url is not None:
            res.append(('url', self.url.replace('\n', ' ')))
        if self.id_ is not None:
            res.append(('id', self.id_.replace('\n', ' ')))
        if self.heads is not None:
            res.append(('heads', self.heads.replace('\n', ' ')))
        if self.keywords is not None:
            res.append(('keywords', self.keywords.replace('\n', ' ')))
        if self.filename is not None:
            res.append(('filename', self.filename.replace('\n', ' ')))
        if self.language is not None:
            res.append(('language', self.language.replace('\n', ' ')))
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

    def register_operation(self, operation: str, sublist_index: Optional[int] = None):
        # Append to the sublist
        if sublist_index:
            self.operations[sublist_index].append(operation)
        else:
            self.operations.append(operation)

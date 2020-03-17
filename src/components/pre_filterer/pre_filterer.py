from typing import Union, Set
from typing import Iterable
from document import Document
import re
from langid.langid import LanguageIdentifier, model # fast



class PreFilterer:
    def __init__(self, length_filter: int = 10, head_filter: bool = True, lang_filter: Union[Set[str], None] = None,
                 dictionary_filter: Union[None, Set[str]] = None):
        self.length_filter = length_filter
        self.head_filter = head_filter
        self.lang_filter = lang_filter
        self.dictionary_filter = dictionary_filter
        self.filters = []
        self._build_filters()

    def _remove_tags(self, text):
        p = re.compile('<.*?>')
        return re.sub(p, '', text)

    def _build_filters(self):
        if self.length_filter > 0:
            self.filters.append(self._filter_by_length)
        if self.head_filter:
            self.filters.append(self._filter_by_heads)
        if self.lang_filter is not None:
            self.filters.append(self._filter_by_lang)
        if self.dictionary_filter is not None:
            self.filters.append(self._filter_by_dict)
            self._compile_dict()

    def _compile_dict(self):
        pass

    def _filter_by_length(self, doc: Document):
        if len(doc.content < self.length_filter):
            return False
        return True

    def _filter_by_heads(self, doc: Document):
        pass

    def _filter_by_lang(self, doc: Document):
        pass

    def _filter_by_dict(self, doc: Document):
        pass

    def filter(self, documents: Iterable[Document]):
        for doc in documents:
            keep = True
            for filter_ in self.filters:
                keep = filter_(doc)
                if not keep:
                    break
            if keep:
                yield doc
                
                
    def heur_filters(self, text, thres_length=40, thres_digit=0.1, thres_alpha=0.05, 
                     thres_upper=0.1, target_lang='es', thres_conf=0.95):
        '''
        Remove documents: non-Spanish
                          short length
                          high a ratio: 
                                    digits,  
                                    uppercase,
                                    non-alphanumeric
        Parameters
        ----------
        text : list of strings
            Every element in the text is a string containing one single sentence
        thres_length: int
            Minimum document length to keep it.
        thres_digit: float
            Maximum proportion of digits in document to keep it
        thres_alpha: float
            Maximum proportion of alphanumeric characters in document to keep it
        thres_upper: float
            Maximum proportion of uppercase characters in document to keep it
        target_lang: str
            Language code we want to keep (es, cat, eu, etc)
        thres_conf: float
            Minimum language confidence to keep it
            
        Returns
        -------
        bool
            Whether to keep document or not
        '''
             
        ## Length condition
        l = len(text)
        if (l < thres_length):
            return False
        
        ## Ratio conditions
        # Digit ratio filter
        if sum(c.isdigit() for c in text)/l > thres_digit:
            return False
        # Not alphanumeric filter
        if (1 - (sum(c.isalnum() for c in text)/l)) > thres_alpha:
            return False
        # Uppercase ratio filter
        if sum(c.isupper() for c in text)/l > thres_upper:
            return False
        
        ## Language condition
        identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
        my_model = identifier.classify(text)
        if ((my_model[0] == target_lang) & 
            (my_model[1]>thres_conf)):
            return True
        else:
            return False

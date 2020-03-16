from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser
from .wikipedia_parser import DataParser


class DataParserFactory:
    def __init__(self, parser_type: str):
        self.parser_type = parser_type

    def get_parser(self, args, kwargs) -> DataParser:
        if self.parser_type == 'wikipedia':
            return WikipediaParser(*args, encoding='utf-8', **kwargs)
        elif self.parser_type == 'bsc-crawl-json':
            return BSCCrawlJSONParser(*args, **kwargs)

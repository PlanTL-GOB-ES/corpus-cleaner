from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser


class DataParserFactory:
    def __init__(self, path: str, parser_type: str):
        if parser_type == 'wikipedia':
            return WikipediaParser
        elif parser_type == 'bsc-crawl-json':
            return BSCCrawlJSONParser

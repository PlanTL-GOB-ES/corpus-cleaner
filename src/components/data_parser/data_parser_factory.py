from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser


def data_parser_factory(path: str, parser_type: str):
    if parser_type == 'wikipedia':
        return WikipediaParser(path)
    elif parser_type == 'bsc-crawl-json':
        return BSCCrawlJSONParser(path)

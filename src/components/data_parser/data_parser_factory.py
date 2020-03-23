from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser
from .wikipedia_parser import DataParser
import argparse


class DataParserFactory:
    VALID_INPUT_FORMATS = ['wikipedia', 'bsc-crawl-json']

    @staticmethod
    def get_parser(args: argparse.Namespace, **kwargs) -> DataParser:
        if args.input_format == 'wikipedia':
            return WikipediaParser(args, **kwargs)
        elif args.input_format == 'bsc-crawl-json':
            return BSCCrawlJSONParser(args, **kwargs)

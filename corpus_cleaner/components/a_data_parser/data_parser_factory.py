from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser
from .onion_parser import OnionParser
from .data_parser import DataParser
import argparse
from typing import Optional


class DataParserFactory:
    VALID_INPUT_FORMATS = ['wikipedia', 'bsc-crawl-json']

    @staticmethod
    def get_parser(args: argparse.Namespace, input_format: Optional[str] = None, **kwargs)\
            -> DataParser:
        if input_format is None:
            if args.input_format == 'wikipedia':
                return WikipediaParser(args, **kwargs)
            elif args.input_format == 'bsc-crawl-json':
                return BSCCrawlJSONParser(args, **kwargs)
            else:
                raise NotImplementedError()
        else:
            if input_format == 'onion':
                return OnionParser(args, **kwargs)
            raise NotImplementedError()

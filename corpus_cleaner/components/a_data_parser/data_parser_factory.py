from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser
from .fairseq_lm_parser import FairseqLMParser
from .sentence_parser import SentenceParser
from .onion_parser import OnionParser
from .data_parser import DataParser
from .data_parser_mapper import DataParserMapper
import argparse
from typing import Optional


class DataParserFactory:
    VALID_INPUT_FORMATS = ['wikipedia', 'bsc-crawl-json', 'fairseq-lm', 'sentence']

    @staticmethod
    def get_parser(args: argparse.Namespace, input_format: Optional[str] = None, **kwargs)\
            -> DataParser:
        if input_format is None:
            if args.input_format == 'wikipedia':
                return WikipediaParser(args, **kwargs)
            elif args.input_format == 'bsc-crawl-json':
                return BSCCrawlJSONParser(args, **kwargs)
            elif args.input_format == 'fairseq-lm':
                return FairseqLMParser(args, **kwargs)
            elif args.input_format == 'sentence':
                return SentenceParser(args, **kwargs)
            else:
                raise NotImplementedError()
        else:
            if input_format == 'onion':
                return OnionParser(args, **kwargs)
            raise NotImplementedError()

    @staticmethod
    def get_parser_mapper(args: argparse.Namespace, input_format: Optional[str] = None, **kwargs) \
            -> DataParserMapper:
        return DataParserMapper(args, DataParserFactory.get_parser(args, input_format, **kwargs))

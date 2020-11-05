from .wikipedia_parser import  WikipediaParser
from .bsc_crawl_json_parser import BSCCrawlJSONParser
from .fairseq_lm_parser import FairseqLMParser
from .sentence_parser import SentenceParser
from .onion_parser import OnionParser
from .warc_parser import WARCParser
from .data_parser import DataParser
from .data_parser_mapper import DataParserMapper
from .document_parser import DocumentParser
from .textfile_parser import TextfileParser
import argparse
from typing import Optional


class DataParserFactory:
    VALID_INPUT_FORMATS = ['wikipedia', 'bsc-crawl-json', 'fairseq-lm', 'sentence', 'warc', 'document', 'textfile']

    @staticmethod
    def get_parser(args: argparse.Namespace, input_format: Optional[str] = None, input_path: Optional[str] = None,
                   **kwargs)\
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
            elif args.input_format == 'warc':
                kwargs['warc_warn'] = args.warc_warn
                return WARCParser(args, **kwargs)
            elif args.input_format == 'document':
                return DocumentParser(args, **kwargs)
            elif args.input_format == 'textfile':
                return TextfileParser(args, **kwargs)
            else:
                raise NotImplementedError(args.input_format)
        else:
            if input_format == 'onion':
                args.encoding = 'utf-8'
                return OnionParser(args, input_path=input_path, **kwargs)
            raise NotImplementedError()

    @staticmethod
    def get_parser_mapper(args: argparse.Namespace, input_format: Optional[str] = None, **kwargs) \
            -> DataParserMapper:
        return DataParserMapper(args, DataParserFactory.get_parser(args, input_format, **kwargs))

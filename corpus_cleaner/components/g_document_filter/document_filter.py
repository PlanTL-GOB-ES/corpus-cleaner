from corpus_cleaner.components.cleaner_component_mapper import CleanerComponent
from corpus_cleaner.components.a_data_parser.data_parser import DataParser
from corpus_cleaner.components.i_output_formatter import OutputFormatter
from corpus_cleaner.document import Document
from typing import TextIO, Iterable, Optional, Tuple, List
import subprocess
import argparse
import os


# Class used to parse the de-duplicated documents from the Onion output file
class OnionParser(DataParser):
    def __init__(self, args: argparse.Namespace, extensions: Tuple[str]=('.onion',), **kwargs):
        super(OnionParser, self).__init__(args, input_path=args.input_path, extensions=extensions, **kwargs)
        self.input_path = os.path.join(args.output_path, 'output_deduplicated.onion')

    def _parse_file(self, fd: TextIO, relative_filepath: str, idx_filepath: int) -> Iterable[Document]:
        doc_sentences = []
        for line in fd.readlines():
            line_index, line = line.split('\t')
            # ignore the first two lines with the start tags
            if line.startswith('<doc>') or line.startswith('<p>') or line.startswith('</p>'):
                continue
            # empty the document sentences list when a new document is reached and return the document object
            elif line.startswith('</doc>'):
                # TODO: add the raw content for each document with the Onion tags
                yield Document(content='', sentences=doc_sentences)
                doc_sentences = []
            else:
                if line_index == '0':
                    doc_sentences.append(line.strip())


# Class used to write the documents in the Onion input file
class OnionOutputFormatter(OutputFormatter):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.file = os.path.join(args.output_path, 'output.onion')
        self.file_fd = None
        self.start_doc_tag = '<doc>\n<p>\n'
        self.end_doc_tag = '</doc>\n</p>\n'

    def _init_writing(self):
        self.file_fd = open(self.file, 'w+')

    def _write_document(self, document: Document):
        doc_onion = self.start_doc_tag + '\n'.join(document.sentences) + self.end_doc_tag
        self.file_fd.writelines(doc_onion)

    def _end_writing(self):
        self.file_fd.close()


class DocumentFilter(CleanerComponent):
    def __init__(self, args: argparse.Namespace):
        super().__init__(args)
        self.onion_parser = OnionParser(args)
        self.onion_formatter = OnionOutputFormatter(args)
        self.onion_input_file = self.onion_formatter.file
        self.onion_output_file = os.path.join(args.output_path, 'output_deduplicate.onion')

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _deduplicate_onion(self, documents: Optional[Iterable[Document]]) -> List[Iterable[Document]]:
        self.onion_formatter.apply(documents)  # write documents in Onion input file
        self._run_onion()  # run Onion de-duplication
        return self.onion_parser.parse() # apply Onion parser to generate a new iterable of documents

    def _run_onion(self):
        onion_command = f'onion -m -n 1 -t 0.8 {self.onion_input_file}'
        with open(self.onion_output_file, 'w') as fd:
            process = subprocess.run(onion_command, stdout=subprocess.PIPE, shell=True, check=True,
                                     universal_newlines=True)
            output = process.stdout
            fd.writelines(output)


    def _filter(self, documents: Optional[Iterable[Document]]) -> List[Iterable[Document]]:
        return self._deduplicate_onion(documents)

    def apply(self, documents: Optional[Iterable[Document]]) -> List[Iterable[Document]]:
        return self._filter(documents)

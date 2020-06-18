import subprocess
import argparse
import os
from ..cleaner_component_reducer import CleanerComponentReducer

'''
class DocumentFilter(CleanerComponentReducer):
    def __init__(self, args: argparse.Namespace, document_deduplication_threshold: float = 0.5):
        onion_input_file = os.path.join(args.output_path, 'input.onion')
        onion_output_file = os.path.join(args.output_path, 'output_deduplicate.onion.dedup')
        super().__init__(args, format_='onion', tmp_file=onion_input_file, final_path=onion_output_file)
        self.document_deduplication_threshold = args.document_deduplication_threshold \
            if args.document_deduplication_threshold is not None else document_deduplication_threshold
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = os.path.join('lib', 'onion-1.2', 'bin', 'onion')

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--document-deduplication-threshold', type=float,
                            help='Threshold for document de-duplication, expressed as the percentage of sentences'
                                 'overlap between documents',
                            default=0.5)

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _run_onion(self):
        onion_command = f'{self.onion_path} -m -n 1 -t {self.document_deduplication_threshold} {self.onion_input_file}' \
            f' > {self.onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

    def _reduce(self):
        self._run_onion()
'''

class DocumentFilter(CleanerComponentReducer):
    def __init__(self, args: argparse.Namespace, document_deduplication_threshold: float = 0.5):
        onion_input_file = os.path.join(args.output_path, 'input.onion')
        onion_output_file = os.path.join(args.output_path, 'output_deduplicate.onion.dedup')
        super().__init__(args, format_='onion', tmp_file=onion_input_file, final_path=onion_output_file)
        self.document_deduplication_threshold = args.document_deduplication_threshold \
            if args.document_deduplication_threshold is not None else document_deduplication_threshold
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = os.path.join('lib', 'onion-1.2', 'bin', 'onion')
        self.onion_tmp = os.path.join(args.output_path, 'tmp')

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--document-deduplication-threshold', type=float,
                            help='Threshold for document de-duplication, expressed as the percentage of sentences'
                                 'overlap between documents',
                            default=0.5)

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _run_onion(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_input_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)
        onion_command = f'{self.onion_path} -m -n 1 -t {self.document_deduplication_threshold} {self.onion_input_file}' \
            f' > {self.onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

    def _reduce(self):
        self._run_onion()

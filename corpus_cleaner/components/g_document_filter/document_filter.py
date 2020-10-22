import subprocess
import argparse
import os
from collections import defaultdict
from ..cleaner_component_reducer import CleanerComponentReducer
from typing import Optional


class DocumentFilter(CleanerComponentReducer):
    def __init__(self, args: argparse.Namespace, document_deduplication_threshold: float = 0.5,
                 dedup_buffer: int = 16777216,
                 remove_glob_rep_sen: int = 5, output_path: Optional[str] = None):
        # TODO: Modify "args.document_deduplication_threshold if args.document_deduplication_threshold is not None
        # else..." pattern
        out_path = output_path if output_path is not None else args.output_path
        onion_input_file = os.path.join(out_path, 'input.onion')
        onion_output_file = os.path.join(out_path, 'output_deduplicate.onion.dedup')
        onion_output_dedup_sentences_file = os.path.join(out_path, 'output_deduplicate.onion.dedup.sentences')
        super().__init__(args, format_='onion', tmp_file=onion_input_file,
                         input_path=out_path)
        self.output_path = out_path
        self.document_deduplication_threshold = args.document_deduplication_threshold \
            if args.document_deduplication_threshold is not None else document_deduplication_threshold
        self.remove_glob_rep_sen = args.remove_glob_rep_sen \
            if args.remove_glob_rep_sen is not None else remove_glob_rep_sen
        self.dedup_buffer = args.dedup_buffer \
            if args.dedup_buffer is not None else dedup_buffer
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = os.path.join('lib', 'onion-1.2', 'bin', 'onion')
        self.onion_tmp = os.path.join(out_path, 'tmp')
        self.onion_output_dedup_sentences_file = onion_output_dedup_sentences_file

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--document-deduplication-threshold', type=float,
                            help='Threshold for document de-duplication, expressed as the percentage of sentences'
                                 'overlap between documents',
                            default=0.5)
        parser.add_argument('--remove-glob-rep-sen', type=int, default=5,
                            help='Whether to remove corpus-level repeated sentences (threshold of repetitions; -1'
                                 'to deactivate)')
        parser.add_argument('--dedup-buffer', type=int, default=16777216,
                            help='Deduplication buffer size, in bytes (default: 16777216)')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _run_onion(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_input_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)
        onion_command = f'{self.onion_path} -m -n 1 -t {self.document_deduplication_threshold} -b {self.dedup_buffer} ' \
            f'{self.onion_input_file} > {self.onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

    def _remove_global_duplicate_sentences(self, threshold: int):
        with open(self.onion_output_file) as fn:
            lines = fn.readlines()

        seen = defaultdict(int)
        sentence_dupli = []
        for line in lines:
            line_index = line.split('\t')[0]
            sentence = '\t'.join(line.split('\t')[1:])
            seen[sentence] += 1
            if line_index == '0':
                if not sentence.startswith('<doc') and sentence not in ['<p>\n', '</p>\n', '</doc>\n']:
                    if seen[sentence] < threshold:
                        sentence_dupli.append(f"{line_index}\t{sentence}")
                else:
                    sentence_dupli.append(f"{line_index}\t{sentence}")
            else:
                sentence_dupli.append(f"{line_index}\t{sentence}")

        with open(self.onion_output_file, 'w') as fn:
            fn.writelines(line for line in sentence_dupli)

    def _reduce(self):
        self._run_onion()
        if self.remove_glob_rep_sen != -1:
            self._remove_global_duplicate_sentences(self.remove_glob_rep_sen)

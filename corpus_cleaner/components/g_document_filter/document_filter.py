import subprocess
import argparse
import os
from ..cleaner_component_reducer import CleanerComponentReducer


class DocumentFilter(CleanerComponentReducer):
    def __init__(self, args: argparse.Namespace, document_deduplication_threshold: float = 0.5,
                 remove_globally_repeated_sentences: bool = False):
        # TODO: Modify "args.document_deduplication_threshold if args.document_deduplication_threshold is not None
        # else..." pattern
        onion_input_file = os.path.join(args.output_path, 'input.onion')
        onion_output_file = os.path.join(args.output_path, 'output_deduplicate.onion.dedup')
        onion_output_dedup_sentences_file = os.path.join(args.output_path, 'output_deduplicate.onion.dedup.sentences')
        remove_globally_repeated_sentences = args.remove_glob_rep_sen \
            if args.remove_glob_rep_sen is not None else remove_globally_repeated_sentences
        final_path = onion_output_file if not remove_globally_repeated_sentences else onion_output_dedup_sentences_file
        super().__init__(args, format_='onion', tmp_file=onion_input_file, final_path=final_path)
        self.document_deduplication_threshold = args.document_deduplication_threshold \
            if args.document_deduplication_threshold is not None else document_deduplication_threshold
        self.remove_globally_repeated_sentences = remove_globally_repeated_sentences
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = os.path.join('lib', 'onion-1.2', 'bin', 'onion')
        self.onion_tmp = os.path.join(args.output_path, 'tmp')
        self.onion_output_dedup_sentences_file = onion_output_dedup_sentences_file

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--document-deduplication-threshold', type=float,
                            help='Threshold for document de-duplication, expressed as the percentage of sentences'
                                 'overlap between documents',
                            default=0.5)
        parser.add_argument('--remove-glob-rep-sen', type=int,
                            help='Whether to remove corpus-level repeated sentences')

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _run_onion(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_input_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)
        onion_command = f'{self.onion_path} -m -n 1 -t {self.document_deduplication_threshold} {self.onion_input_file}'\
            f' > {self.onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

    def _run_remove_sentences(self, threshold: int):
        awk = '''{
    switch($0)
    {
    case /0\\t\</:
        { if(!seen[$0]++ < ''' + str(threshold) + '''){ print;getline;print } else { getline;print } }
        break
    default:
        print
        break
    }
}
    '''
        awk_path = os.path.join(self.args.output_path, 'script.awk')
        with open(awk_path, 'w') as f:
            f.write(awk)
        command = f"gawk -f {awk_path} {self.onion_output_file} > {self.onion_output_dedup_sentences_file}"
        subprocess.run(command, shell=True, check=True, universal_newlines=True)
        os.remove(awk_path)

    def _reduce(self):
        self._run_onion()
        if self.args.remove_glob_rep_sen:
            self._run_remove_sentences(self.remove_globally_repeated_sentences)

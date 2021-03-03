import subprocess
import argparse
import os
from ..cleaner_component_reducer import CleanerComponentReducer
from typing import Optional
from corpus_cleaner.constants import ONION_PATH, DEBUG_EXTENSION, DEDUP_EXTENSION, SENTENCES_EXTENSIONS, TMP_PATH,\
    ONION_INPUT, ONION_OUTPUT, ONION_OUTPUT_DEDUP_SENTENCES
from dataclasses import dataclass


@dataclass
class DocumentFilterConfig:
    document_deduplication_threshold: float = 0.5  # Threshold for document de-duplication, expressed as the percentage
    # of sentences overlap between documents
    remove_glob_rep_sen: int = 5  # Whether to remove corpus-level repeated sentences (threshold of repetitions; -1
    # to deactivate)
    dedup_buffer: int = 100000000  # Deduplication buffer size, in bytes (default: 100000000)


class DocumentFilter(CleanerComponentReducer):
    def __init__(self, args: argparse.Namespace, config: DocumentFilterConfig,
                 output_path: Optional[str] = None):
        # TODO: Modify "args.document_deduplication_threshold if args.document_deduplication_threshold is not None
        # else..." pattern
        out_path = output_path if output_path is not None else args.output_path
        onion_input_file = os.path.join(out_path, ONION_INPUT)
        onion_output_file = os.path.join(out_path, ONION_OUTPUT)
        onion_output_dedup_sentences_file = os.path.join(out_path, ONION_OUTPUT_DEDUP_SENTENCES)
        remove_glob_rep_sen = args.remove_glob_rep_sen if args.remove_glob_rep_sen is not None else remove_glob_rep_sen
        final_path = onion_output_file if remove_glob_rep_sen < 2 else onion_output_dedup_sentences_file
        if args.debug:
            extensions = DEBUG_EXTENSION
        elif remove_glob_rep_sen < 2:
            extensions = DEDUP_EXTENSION
        else:
            extensions = SENTENCES_EXTENSIONS
        extensions = (extensions,)
        super().__init__(args, format_='onion', tmp_file=onion_input_file, final_path=final_path,
                         input_path=out_path, extensions=extensions)
        self.output_path = out_path
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = ONION_PATH
        self.onion_tmp = os.path.join(out_path, TMP_PATH)
        self.onion_output_dedup_sentences_file = onion_output_dedup_sentences_file

        self._config = config

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _run_onion(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_input_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)
        onion_command = f'{self.onion_path} -m -n 1 -t {self._configdocument_deduplication_threshold} -b {self._config.dedup_buffer} ' \
            f'{self.onion_input_file} > {self.onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

    def _remove_global_duplicate_sentences(self, threshold: int):
        # First, remove format-control letters to prevent errors in the awk script
        remove_format_modifiers_command = f"sed -i 's/%/___PERCENTAGE___/g' {self.onion_output_file}"
        subprocess.run(remove_format_modifiers_command, shell=True, check=True, universal_newlines=True)

        # Then, deduplicate with gawk command
        awk = '''{
                    switch($0)
                    {
                    case /0\t</:
                        print
                        break
                    case /0\t/:
                        seen[$0]++
                        {if (seen[$0] <= ''' + str(threshold) + ''') {print} else {printf "1" "\t"; for (i=2; i<NF; i++) printf $i " "; print $NF}}
                        break
                    default:
                        print
                        break
                    }
                }
        '''
        awk_path = os.path.join(self.output_path, 'script.awk')
        with open(awk_path, 'w') as f:
            f.write(awk)
        command = f"gawk -f {awk_path} {self.onion_output_file} > {self.onion_output_dedup_sentences_file}"
        subprocess.run(command, shell=True, check=True, universal_newlines=True)
        demask_command = f"sed -i 's/___PERCENTAGE___/%/g' {self.onion_output_dedup_sentences_file}"
        subprocess.run(demask_command, shell=True, check=True, universal_newlines=True)
        os.remove(awk_path)

    def _reduce(self):
        self._run_onion()
        if self.remove_glob_rep_sen != -1:
            self._remove_global_duplicate_sentences(self.remove_glob_rep_sen)

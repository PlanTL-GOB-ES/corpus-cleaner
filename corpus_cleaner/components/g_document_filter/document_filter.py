import subprocess
import os
from ..cleaner_component_reducer import CleanerComponentReducer
from typing import Optional
from glob import glob
from corpus_cleaner.par_utils import MappingPipeline, PipelineLogger

from ..cleaner_component_reducer import CleanerComponentReducer, ReduceConfig
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


class DummyReducer(CleanerComponentReducer):
    def __init__(self, output_path: str):
        onion_input_file = os.path.join(output_path, 'input.onion.debug')
        reduce_config = ReduceConfig(path=output_path, after_reduce_extension='debug')
        super().__init__(reduce_config)
        self.onion_final_file = onion_input_file
        self.onion_tmp = os.path.join(output_path, 'tmp')

    def _reduce(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_final_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)


class DocumentFilter(CleanerComponentReducer):
    def __init__(self, config: DocumentFilterConfig, output_path: str, debug: bool = False):
        onion_input_file = os.path.join(output_path, ONION_INPUT)
        onion_output_file = os.path.join(output_path, ONION_OUTPUT)
        onion_output_dedup_sentences_file = os.path.join(output_path, ONION_OUTPUT_DEDUP_SENTENCES)
        remove_glob_rep_sen = config.remove_glob_rep_sen
        self.final_path = onion_output_file if remove_glob_rep_sen < 2 else onion_output_dedup_sentences_file
        if debug:
            extension = DEBUG_EXTENSION
        elif remove_glob_rep_sen < 2:
            extension = DEDUP_EXTENSION
        else:
            extension = SENTENCES_EXTENSIONS
        reduce_config = ReduceConfig(path=output_path, after_reduce_extension=extension)
        super().__init__(reduce_config)
        self.output_path = output_path
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = ONION_PATH
        self.onion_tmp = os.path.join(output_path, TMP_PATH)
        self.onion_output_dedup_sentences_file = onion_output_dedup_sentences_file
        
        self._config = config


    @property
    def reduced_path(self) -> str:
        return self.final_path

    def _run_onion(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_input_file
        add_doc_tags = f"sed -i '1i <corpora>' {self.onion_input_file}; echo '</corpora>' >> {self.onion_input_file}"
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)
        onion_command = f'{self.onion_path} -m -n 1 -t {self._config.document_deduplication_threshold} -b {self._config.dedup_buffer} ' \
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

    def get_onion_files_paths(self):
        paths = []
        for path in glob(os.path.join(self.onion_tmp, '*.onion')):
            paths.append(path)
        return paths

    def run_single_onion_dedup_txt(self, path: str):
        # Onion
        onion_output_file = f'{path}.dedup'
        onion_command = f'{self.onion_path} -m -n 1 -t {self.document_deduplication_threshold} -b {self.dedup_buffer} ' \
                        f'{path} > {onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

        # Awk
        # First, remove format-control letters to prevent errors in the awk script
        if self.remove_glob_rep_sen != -1:
            threshold = self.remove_glob_rep_sen
            remove_format_modifiers_command = f"sed -i 's/%/___PERCENTAGE___/g' {onion_output_file}"
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
            awk_path = os.path.join(self.output_path, f'script{str(os.getpid())}.awk')
            with open(awk_path, 'w') as f:
                f.write(awk)
            onion_output_dedup_sentences_file = onion_output_file + '.sentences'
            command = f"gawk -f {awk_path} {onion_output_file} > {onion_output_dedup_sentences_file}"
            subprocess.run(command, shell=True, check=True, universal_newlines=True)
            demask_command = f"sed -i 's/___PERCENTAGE___/%/g' {onion_output_dedup_sentences_file}"
            subprocess.run(demask_command, shell=True, check=True, universal_newlines=True)
            os.remove(awk_path)


    def create_pipeline_reducer_mappers(self):
        return [self.run_single_onion_dedup_txt]

    def _reduce(self):
        if self.only_reduce_ind_onion:
            self.get_onion_files_paths()
            self.args.logger.logger.info('Distributed reduce')
            pipeline = MappingPipeline(streams=self.get_onion_files_paths(),
                                       mappers_factory=self.create_pipeline_reducer_mappers,
                                       parallel=self.args.parallel,
                                       logger=self.args.logger if self.args.log_every_iter != -1 else None,
                                       log_every_iter=self.args.log_every_iter,
                                       backend=self.args.backend,
                                       checkpoint_path=None)
            pipeline.run()
        else:
            self._run_onion()
            if self._config.remove_glob_rep_sen != -1:
                self._remove_global_duplicate_sentences(self._config.remove_glob_rep_sen)

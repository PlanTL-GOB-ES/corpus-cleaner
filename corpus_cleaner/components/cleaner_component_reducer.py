from abc import ABC
from .a_data_parser import DataParserFactory
from .a_data_parser.data_parser import DataParserConfig
import os
import subprocess
from corpus_cleaner.components.cleaner_component import CleanerComponent
from dataclasses import dataclass

@dataclass
class ReduceConfig:
    path: str
    after_reduce_extension: str  # .dedup, .debug,...


class CleanerComponentReducer(CleanerComponent, ABC):
    def __init__(self, config: ReduceConfig):

        data_parser_config = DataParserConfig(input_path=config.path, input_format='onion',
                                              extensions=(config.after_reduce_extension,))
        self._data_parser = DataParserFactory.get_parser(data_parser_config)
        self.reduced = False

    def _reduce(self):
        raise NotImplementedError

    def reduce(self):
        assert not self.reduced
        self._reduce()
        self.reduced = True

    @property
    def reduced_path(self) -> str:
        raise NotImplementedError

    def get_reduced_document(self):
        assert self.reduced
        return self._data_parser.parse()


class DummyReducer(CleanerComponentReducer):
    def __init__(self, output_path: str):
        onion_input_file = os.path.join(output_path, 'input.onion.debug')
        reduce_config = ReduceConfig(path=output_path, after_reduce_extension='debug')
        super().__init__(reduce_config)
        self.onion_final_file = onion_input_file
        self.onion_tmp = os.path.join(output_path, 'tmp')

    @property
    def reduced_path(self) -> str:
        return self.onion_final_file

    def _reduce(self):
        cat_command = "find " + self.onion_tmp + " -name '*.onion' -exec cat {} \; > " + self.onion_final_file
        subprocess.run(cat_command, shell=True, check=True, universal_newlines=True)

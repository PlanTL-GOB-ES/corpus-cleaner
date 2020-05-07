import subprocess
import argparse
import os
from ..cleaner_component_reducer import CleanerComponentReducer


class DocumentFilter(CleanerComponentReducer):
    def __init__(self, args: argparse.Namespace):
        onion_input_file = os.path.join(args.output_path, 'input.onion')
        onion_output_file = os.path.join(args.output_path, 'output_deduplicate.onion.dedup')
        super().__init__(args, format_='onion', tmp_file=onion_input_file, final_path=onion_output_file)
        self.onion_input_file = onion_input_file
        self.onion_output_file = onion_output_file
        self.onion_path = os.path.join('lib', 'onion-1.2', 'bin', 'onion')

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass

    @staticmethod
    def check_args(args: argparse.Namespace):
        # TODO check custom args
        pass

    def _run_onion(self):
        onion_command = f'{self.onion_path} -m -n 1 -t 0.8 {self.onion_input_file} > {self.onion_output_file}'
        subprocess.run(onion_command, shell=True, check=True, universal_newlines=True)

    def _reduce(self):
        self._run_onion()

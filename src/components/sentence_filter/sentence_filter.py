from components.cleaner_component import CleanerComponent
import argparse


class SentenceFilter(CleanerComponent):
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()


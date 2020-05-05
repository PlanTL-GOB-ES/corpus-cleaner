import argparse


class CleanerComponent:

    def __init__(self, args: argparse.Namespace):
        self.args = args

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

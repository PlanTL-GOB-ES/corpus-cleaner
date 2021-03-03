import argparse


class CleanerComponentConfig:
    pass


class CleanerComponent:
    @staticmethod
    def add_config() -> CleanerComponentConfig:
        raise NotImplementedError


class LegacyCleanerComponent:

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.debug = self.args.debug if args is not None else None

    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        raise NotImplementedError()

    @staticmethod
    def check_args(args: argparse.Namespace):
        raise NotImplementedError()

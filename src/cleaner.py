from document import Document
from typing import Iterable
from components.data_parser import *
import argparse
import logging


class Cleaner:
    def __init__(self, args: argparse.Namespace, output_dir: str, log: logging):
        self.args = args
        self.output_dir = output_dir
        self.logging = logging

    def clean(self):
        raise NotImplementedError()

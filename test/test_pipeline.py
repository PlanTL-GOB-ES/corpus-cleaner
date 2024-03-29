import pytest
import os
import datetime
import re

date_time = re.sub(r'[T]', '-', datetime.datetime.now().replace(microsecond=0).isoformat()).replace(":", "")[:-2]
filename = "output/pre-push-test-" + date_time + "/output.txt"


def test_pipeline_execution():
    os.system("python clean.py pre-push-test --input-path test/toy_data --input-format warc --output-format fairseq-lm "
              "--lang-filter ca")
    assert os.path.isfile(filename), "Execution unsucessful"


def test_file_exists():
    assert os.path.getsize(filename) > 0, "Output file is empty"


def test_file_length():
    with open(filename) as fn:
        lines = fn.readlines()
    assert len(lines) > 100, "Output file doesn't have the expected number of lines (268)"

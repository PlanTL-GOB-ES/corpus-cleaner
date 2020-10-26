from pathlib import Path
import sys
import re
import os
import logging

logging.basicConfig(level=logging.INFO)

data_dir = sys.argv[1]
p = Path(os.path.realpath(data_dir))

SUFFIX = ".txt"


def postprocess(file):
    # remove bullets point starting with L
    pattern_replace_bullets = re.compile(r" *ʟ *")

    # recover hyphen-splitter sentences
    pattern_line_break_1 = re.compile(r"-\n")
    # recover sentences split not preceded by a period and followed by lowercase character
    pattern_line_break_2 = re.compile(r"(?<![.?¿!¡])\s*\n(?=\s*[a-z])")

    with open(os.path.join(data_dir, file)) as fn:
        content = fn.read()
    content_postproc = pattern_replace_bullets.sub("", content)
    content_postproc = pattern_line_break_1.sub("", content_postproc)
    content_postproc = pattern_line_break_2.sub(" ", content_postproc)
    with open(os.path.join(data_dir, f"{file}_postproc"), 'w') as gn:
        gn.write(content_postproc)

    lines_raw = len(content.splitlines())
    lines_postproc = len(content_postproc.splitlines())
    logging.info(f"Raw lines: {lines_raw}, Postprocessed lines: {lines_postproc}, "
                 f"Difference: {lines_raw - lines_postproc}")


for file in p.rglob(f"*{SUFFIX}"):
    logging.info(f"Processing file {file}")
    postprocess(file)

from pathlib import Path
import sys
import re
import os
import logging

logging.basicConfig(level=logging.INFO)


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

    lines_raw = len(content.splitlines())
    lines_postproc = len(content_postproc.splitlines())

    dir_tree = os.path.dirname(os.path.relpath(file, data_dir))
    output_file = os.path.join(output_dir, dir_tree, f"{os.path.basename(file)}")
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as gn:
        gn.write(content_postproc)

    logging.info(f"Raw lines: {lines_raw}, Postprocessed lines: {lines_postproc}, "
                 f"Difference: {lines_raw - lines_postproc}, Outfile: {output_file}")


if __name__ == '__main__':
    data_dir = sys.argv[1]
    output_dir = sys.argv[2]
    p = Path(os.path.realpath(data_dir))
    os.makedirs(output_dir, exist_ok=True)

    SUFFIX = ".txt"

    files = list(p.rglob(f"*{SUFFIX}"))
    for file in files:
        logging.info(f"Processing file {file}")
        postprocess(file)

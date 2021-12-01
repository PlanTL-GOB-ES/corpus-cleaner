from pathlib import Path
import sys
import re
import os
import logging
import argparse

logging.basicConfig(level=logging.INFO)


def postprocess(file, data_dir, output_dir):
    # remove space before new lines
    pattern_replace_trailing_spaces = re.compile(r" *\n")

    # remove bullets point starting with L
    pattern_replace_bullets = re.compile(r" *ʟ *")

    # recover hyphen-splitter sentences
    pattern_line_break_1 = re.compile(r"-\n")

    # recover sentences split not preceded by a period and followed by lowercase character
    pattern_line_break_2 = re.compile(r"(?<![.?¿!¡])\n(?=\s*[a-z])")

    # recover sentences split by preceded by numerical bullet points
    pattern_line_break_3 = re.compile(r"(?<=[0-9]\.)\n")

    with open(file) as fn:
        content = fn.read()

    content_postproc = pattern_replace_trailing_spaces.sub('\n', content)
    content_postproc = pattern_replace_bullets.sub("", content_postproc)
    content_postproc = pattern_line_break_1.sub("", content_postproc)
    content_postproc = pattern_line_break_2.sub("", content_postproc)
    content_postproc = pattern_line_break_3.sub(" ", content_postproc)

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
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_dir', type=str, help='directory with data (processed recursively in case of subdirs)')
    parser.add_argument('--output_dir', type=str, help='output directory with processed data')
    parser.add_argument('--filename', type=str, help='filename to search within the data_dir')
    args = parser.parse_args()

    p = Path(os.path.realpath(args.data_dir))
    os.makedirs(args.output_dir, exist_ok=True)

    SUFFIX = args.filename

    files = list(p.rglob(f"*{SUFFIX}"))
    for file in files:
        logging.info(f"Processing file {file}")
        postprocess(str(file), args.data_dir, args.output_dir)

import os

FASTTEXT_PATH = os.path.join('lib', 'lid.176.bin')

HARDCODED_EXTENSIONS = 'HARDCODED EXTENSIONS'

HARDCODED_ENCODING = 'HARDCODED ENCODING'

ONION_PATH = os.path.join('lib', 'onion-1.2', 'bin', 'onion')

DEBUG_EXTENSION = '.debug'

DEBUG_SEPARATOR = "|"

DEDUP_EXTENSION = '.dedup'

SENTENCES_EXTENSIONS = '.sentences'

TMP_PATH = 'tmp'

ONION_INPUT = 'input.onion'

ONION_OUTPUT = 'output_deduplicate.onion.dedup'

ONION_OUTPUT_DEDUP_SENTENCES = 'output_deduplicate.onion.dedup.sentences'

ONION_START_DOC_TAG = '<doc '

ONION_START_P_TAG = ' >\n<p>\n'

ONION_END_P_TAG = '\n</p>\n</doc>\n'

WARC_SKIP = ['mp4', 'mp3', 'jpg', 'png', 'svg', '.js']

TXT_OUTPUT_PATH = 'output.txt'

CHECKPOINT_PATH_ESCAPE = '__PATH__'

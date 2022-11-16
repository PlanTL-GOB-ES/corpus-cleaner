# Corpus Cleaner

## Project description

Corpus Cleaner is a modular Python-based toolkit to clean raw text corpora through generator pipelines.

It was mainly designed to clean text collected from web crawlers resulting in a specific data format. However, due to its modularity, it can be customized and adapted to any data format.

## Install and run

We provide three ways of installing the Corpus Cleaner.

### Method 1: Virtual environment

Corpus Cleaner is not supposed to be run in Windows, specially the parallel implementation. Instead, a Unix system is assumed.

First create the Python virtualenv with python3.8 and install the dependencies (from `requirements.txt`), run:

```sh
bash setup.sh
```

For downloading third-party, non-Python dependencies, run:

```sh
bash get-third-party.sh
```

Currently, the non-Python dependencies are:
  - FastText language identifier (<https://fasttext.docs/en/language-identification.html>).
  - Onion (<http://corpus.tools/wiki/Onion>).
  
> Notice that installing a library required by Onion implies a system-wise installation of a library.

With the virtual environment activated (`source venv/bin/activate`), run the following with the python interpreter:

```sh
(venv) $ python clean.py [ARGS]
```

> To know the available arguments `[ARGS]`, see [Usage section](#usage) below.

### Method 2: Docker

Make sure docker is installed in your system: https://docs.docker.com/engine/install/

Build the docker image:

```sh
bash build-docker.sh
```

Run the docker container:

```sh
bash run-docker.sh [ARGS]
```

> To know the available arguments `[ARGS]`, see [Usage section](#usage) below.

### Method 3: Singularity

For building the Singularity image, once the Docker one has been built (since it is converted using <https://github.com/singularityhub/docker2singularity>), assuming Singularity is installed (<https://singularity.lbl.gov/docs-installation>), run:

```sh
bash build-singularity.sh
```

```sh
bash run-singularity.sh [ARGS]
```

> To know the available arguments `[ARGS]`, see [Usage section](#usage) below.

## Usage

### Data

In case Docker or Singularity are used, input data should be placed in a sub-directory in the `data/` directory. Use symbolic links in case you do not want to place there your actual data. One can use the `input-path` or `--output-path` arguments, which are supposed to be relative paths from the root of the project (e.g. `--input-path data/example-data`).

In the case of the virtual environment, data could be placed in other directories, as long as the path is correctly passed as an argument.

### Arguments

Currently, Corpus Cleaner has the following arguments:
```python
usage: clean.py [-h] [--input-path INPUT_PATH]
                     [--output-path OUTPUT_PATH]
                     [--input-format INPUT_FORMAT] 
                     [--output-format OUTPUT_FORMAT] 
                     [--checkpoint-backend {shelve,file}]                
                     [--components COMPONENTS [COMPONENTS ...]] 
                     [--parallel] 
                     [--log-every-iter LOG_EVERY_ITER]
                     [--backend BACKEND] 
                     [--only-reduce]
                     [--only-reduce-output]
                     [--debug] [--no-reduce]
                     [--extensions EXTENSIONS [EXTENSIONS ...]]
                     [--encoding ENCODING] 
                     [--encoding-threshold ENCODING_THRESHOLD]     
                     [--encoding-error-policy ENCODING_ERROR_POLICY]     
                     [--url-doc URL_DOC]
                     [--warc-warn] 
                     [--none_filter] 
                     [--lang-filter-document] 
                     [--language-normalization] 
                     [--replace-emails] 
                     [--remove-hashtags-mentions]
                     [--remove-tags]
                     [--space-normalization]
                     [--replace-urls] 
                     [--char-length-filter-document CHAR_LENGTH_FILTER_DOCUMENT]
                     [--head-filter]
                     [--digits_filter DIGITS_FILTER] 
                     [--remove-citations]
                     [--lang-chars-filter LANG_CHARS_FILTER] 
                     [--alphanum-filter ALPHANUM_FILTER]
                     [--uppercase-filter UPPERCASE_FILTER]
                     [--alphabet-filter ALPHABET_FILTER [ALPHABET_FILTER ...]]
                     [--lang-filter LANG_FILTER [LANG_FILTER ...]]      [--initial-lang-filter-threshold INITIAL_LANG_FILTER_THRESHOLD] 
                     [--dictionary-filter-doc DICTIONARY_FILTER_DOC] [--seg-sentences]
                     [--char-length-filter-sentence CHAR_LENGTH_FILTER_SENTENCE]      [--word-length-filter-sentence WORD_LENGTH_FILTER_SENTENCE] 
                     [--digits-filter-sentence DIGITS_FILTER_SENTENCE]
                     [--profanity-check] 
                     [--fast-lang-filter-threshold FAST_LANG_FILTER_THRESHOLD]      [--slow-lang-filter-threshold SLOW_LANG_FILTER_THRESHOLD]      [--lang-filter-sentence]
                     [--lang-filter-sentence_src_tgt] 
                     [--code-threshold CODE_THRESHOLD] 
                     [--dictionary-filter-sen DICTIONARY_FILTER_SEN] [--dedup-same-doc-sentences] 
                     [--spell-check]
                     [--terminology-norm TERMINOLOGY_NORM]
                     [--punctuation-norm]
                     [--document-deduplication-threshold DOCUMENT_DEDUPLICATION_THRESHOLD]
                     [--remove-glob-rep-sen REMOVE_GLOB_REP_SEN]
                     [--dedup-buffer DEDUP_BUFFER] 
                     [--only-reduce-ind-onion]
                     name

Clean raw text data.

positional arguments:
  name                  A name to identify the run

optional arguments:
  -h, --help            show this help message and exit
  --input-path INPUT_PATH
                        Input data directory
  --output-path OUTPUT_PATH
                        Output data directory
  --input-format INPUT_FORMAT
                        Input data format
  --output-format OUTPUT_FORMAT
                        Output data format
  --checkpoint-backend {shelve,file}
                        Shelve is more convenient but file is more robust. For distributed executions,we recommend file.
  --components COMPONENTS [COMPONENTS ...]
                        Elements of the pipeline
  --parallel            Run the cleaner in parallel
  --log-every-iter LOG_EVERY_ITER
                        Log the pipeline every N iterations(-1, silent)
  --backend BACKEND     Parallel backend (mp or ray)
  --only-reduce         Only document filter
  --only-reduce-output  Only document filter for output files
  --debug               Activate the debug error mode to compare the original and cleaned sentences
  --no-reduce           suppress document filter component
  --extensions EXTENSIONS [EXTENSIONS ...]
                        File extensions to work with (eg. json)
  --encoding ENCODING   Input encoding format (eg. utf-8. If set to auto, the programtries to guess the encoding
  --encoding-threshold ENCODING_THRESHOLD
                        Encoding threshold if --encoding auto (ignoredotherwise. If the encoding detector is not above this threshold, it assigns utf-8.
  --encoding-error-policy ENCODING_ERROR_POLICY
                        Encoding error policy (same options as open()
  --url-doc URL_DOC     Path to a url list (plain text, one url per line)that should be filtered and processed
  --warc-warn           Enable warnings of WARC parser
  --none_filter         Apply no filters
  --lang-filter-document
                        Applying language filter on documents
  --language-normalization
                        Applying language-specific normalization
  --replace-emails      Replacing email adresses with "[EMAIL]"
  --remove-hashtags-mentions
                        Remove hashtags and mentions.
  --remove-tags         Remove XML/HTML tags
  --space-normalization
                        Normalize white spaces
  --replace-urls        Replacing URLs with "[URL]"
  --char-length-filter-document CHAR_LENGTH_FILTER_DOCUMENT
                        Minimum char length per document. Set to 0 not to apply any filter.
  --head-filter         Filter documents coming froma crawler (having a "heads" attribute) withcommon HTTP errors.
  --digits_filter DIGITS_FILTER
                        Maximum allowed proportion of digit characters
  --remove-citations    If used, remove citations in the common square brackets format, e.g [34]
  --lang-chars-filter LANG_CHARS_FILTER
                        Maximum allowed proportion of characters notbelonging to the alphabet of the language
  --alphanum-filter ALPHANUM_FILTER
                        Maximum allowed proportion of non-alphanumericcharacters
  --uppercase-filter UPPERCASE_FILTER
                        Maximum allowed proportion of uppercase characters
  --alphabet-filter ALPHABET_FILTER [ALPHABET_FILTER ...]
                        Alphabets that should be present (eg. LATIN)
  --lang-filter LANG_FILTER [LANG_FILTER ...]
                        List of languages that should allowed when filtering bylang. If not set, no filtering is applied.
  --initial-lang-filter-threshold INITIAL_LANG_FILTER_THRESHOLD
                        If --lang-filter is set, minimumthreshold for the initial langidentifier
  --dictionary-filter-doc DICTIONARY_FILTER_DOC
                        Path to dictionary (plain text, one term perline of terms that should not appear in adocument
  --seg-sentences       Segment wrongfully concatenated sentences.
  --char-length-filter-sentence CHAR_LENGTH_FILTER_SENTENCE
                        filter sentences shorter than a given minimum character length
  --word-length-filter-sentence WORD_LENGTH_FILTER_SENTENCE
                        filter sentences shorter than a given minimum word length
  --digits-filter-sentence DIGITS_FILTER_SENTENCE
                        Maximum allowed proportion of digit characters in the sentence
  --profanity-check     filter sentences with sensible content
  --fast-lang-filter-threshold FAST_LANG_FILTER_THRESHOLD
                        If --lang-filter is set, minimumthreshold for the faster lang identifier
  --slow-lang-filter-threshold SLOW_LANG_FILTER_THRESHOLD
                        If --lang-filter is set, minimumthreshold for the slower lang identifier
  --lang-filter-sentence
                        Applying language filter on sentences
  --lang-filter-sentence_src_tgt
                        Applying language filter on sentences with "src=" pattern
  --code-threshold CODE_THRESHOLD
                        Threshold (percentage) of code-like chars and tokensto filter a sentence (-1 to deactivate)
  --dictionary-filter-sen DICTIONARY_FILTER_SEN
                        Path to dictionary (plain text, one term perline of terms that should not appear in asentence
  --dedup-same-doc-sentences
                        Deduplicate sentences inside the same document.
  --spell-check         Apply spell checking.
  --terminology-norm TERMINOLOGY_NORM
                        Path to a terminology dictionary to appliynormalization
  --punctuation-norm    Apply punctuation normalization.
  --document-deduplication-threshold DOCUMENT_DEDUPLICATION_THRESHOLD
                        Threshold for document de-duplication, expressed as the percentage of sentencesoverlap between documents
  --remove-glob-rep-sen REMOVE_GLOB_REP_SEN
                        Whether to remove corpus-level repeated sentences (threshold of repetitions; -1to deactivate)
  --dedup-buffer DEDUP_BUFFER
                        Deduplication buffer size, in bytes (default: 1000000000)
  --only-reduce-ind-onion
                        Individually apply reduction
```

The options will be detailed if you run the program with the `--help` argument.

### Examples

In the `data/` directory, there is the `toy_wiki` directory, which is a tiny subset of the Catalan wikipedia.

Depending on your run option, run one of the following commands:

```sh
(venv) $ python clean.py example-output --input-path data/toy_wiki --input-format wikipedia --output-format fairseq-lm --lang-filter ca
```

```sh
bash run-docker.sh example-output --input-path data/toy_wiki --input-format wikipedia --output-format fairseq-lm --lang-filter ca
```

```sh
bash run-singularity.sh example-output --input-path data/toy_wiki --input-format wikipedia --output-format fairseq-lm --lang-filter ca
```

The output will be stored in `output/` directory:
  - `args.json`: Arguments used, in order to make it reproducible.
  - `clean.log`: The cleaning log.
  - `output.txt`: The actual output.

## Internals

For understanding how Corpus Cleaner works, please see the code documentation (_TODO_). As a high-level overview, see this section.

### Components

Corpus Cleaner applies the following components (in order):
  - a) Data parser: Parse the data in a specific format (currently supported formats: BNE Json and Wikipedia). It is easy to extend to new formats, by subclassing DataParser.
  - b) Encoding fixer.
  - c) Pre-filterer: Document-level, char-based, heuristic filters for discarding documents.
  - d) Sentence splitter.
  - e) Sentence filter: Sentence-level filters, slightly more complex than the ones in the Pre-filterer.
  - f) Normalizer: Optional normalization including punctuation.
  - g) Document filter: Document-level filters. Basically, document deduplication.
  - h) Document organizer: Organize documents into domains or languagees (not implemented yet).
  - i) Output formatter: Write the output in a specific format (currently supported outputs: Fairseq LM format).

## Contributing

Pull requests are welcome!

### My input format (eg. PubMed XML) is not supported

Sub-class DataParser similarly to how BNEJsonParser and WikipediaParser are implemented. Adapt the DataParserFactory accordingly.

### My output format is not supported.
Sub-class OutputFormatter similarly to how FairseqLMOutputFOrmatter is implemented. Adapt the OutputFormatterFactory accordingly.

### A specific component doesn't adapt to my needs

First, try to change the default arguments. If it still doesn't fit your use case, modify the component, or add a new one.

## Versioning

The current version is 0.1.

## Authors

* [Jordi Armengol Estapé](https://github.com/jordiae)
* [Casimiro Pio Carrino](https://github.com/ccasimiro88)
* [Ona de Gibert](https://github.com/onadegibert)

See also the full list of [contributors](https://github.com/TeMU-BSC/corpus-cleaner/graphs/contributors) who participated in this project.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

Some of the filters of this project are inspired by: <https://github.com/spyysalo/wiki-bert-pipeline>.

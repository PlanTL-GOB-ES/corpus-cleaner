# Corpus Cleaner

## Project description

Corpus Cleaner is a modular Python-based toolkit to clean raw text corpora through generator pipelines.

It was mainly designed to clean text collected from web crawlers resulting in a specific data format. However, due to its modularity, it can be customized and adapted to any data format.

## Install and run

We provide three ways of installing the Corpus Cleaner.

### Method 1: Virtual environment

Corpus Cleaner was built and tested with Python3.7. It should work for Python >= 3.6 but it has not been tested with other versions than 3.7.

In addition, some parts are not supposed to be run in Windows, specially the parallel implementation. Instead, a Unix system is assumed.

For creating the virtual environment and installing the dependencies (from `requirements.txt`), run:

```sh
bash setup.sh
```

For downloading third-party, non-Python dependencies, run:

```sh
bash get-third-party.sh
```

Currently, the non-Python dependencies are:
  - FastText language identifier (<https://fasttext.cc/docs/en/language-identification.html>).
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
```sh
usage: clean.py [-h] [--input-path INPUT_PATH] [--output-path OUTPUT_PATH]
                [--input-format INPUT_FORMAT] [--output-format OUTPUT_FORMAT]
                [--checkpoint-backend {shelve,file}] [--components COMPONENTS [COMPONENTS ...]]
                [--parallel] [--log-every-iter LOG_EVERY_ITER]
                [--backend BACKEND] [--only-reduce] [--only-reduce-output]
                [--debug] [--extensions EXTENSIONS [EXTENSIONS ...]]
                [--encoding ENCODING] [--encoding-threshold ENCODING_THRESHOLD]
                [--encoding-error-policy ENCODING_ERROR_POLICY] [url-doc URL_DOC]
                [--warc-warn] [--none_filter] 
                [--no-lang-filter-document] [--no-language-normalization]
                [--no-replace-emails] [--no-remove-hashtags-mentions]
                [--no-remove-tags] [--no-space-normalization]
                [--no-replace-urls] [--char-length-filter-document CHAR_LENGTH_FILTER_DOCUMENT]
                [--no-head-filter] [--digits_filter DIGITS_FILTER]
                [--remove-citations] [-lang-chars-filter LANG_CHARS_FILTER]
                [--alphanum_filter ALPHANUM_FILTER]
                [--uppercase_filter UPPERCASE_FILTER]
                [--alphabet-filter ALPHABET_FILTER [ALPHABET_FILTER ...]]
                [--lang-filter LANG_FILTER [LANG_FILTER ...]]
                [--initial-lang-filter-threshold INITIAL_LANG_FILTER_THRESHOLD]
                [--dictionary-filter-doc DICTIONARY_FILTER_DOC] [--seg-sentences]
                [--char-length-filter-sentence CHAR_LENGTH_FILTER_SENTENCE]
                [--word-length-filter-sentence WORD_LENGTH_FILTER_SENTENCE]
                [--digits-filter-sentence DIGITS_FILTER_SENTENCE]
                [--profanity-check]
                [--fast-lang-filter-threshold FAST_LANG_FILTER_THRESHOLD]
                [--slow-lang-filter-threshold SLOW_LANG_FILTER_THRESHOLD]
                [--no-lang-filter-sentence] [--no-lang-filter-sentence_src_tgt]
                [--code-threshold CODE_THRESHOLD]
                [--dictionary-filter-sen DICTIONARY_FILTER_SEN]
                [--no-dedup-same-doc-sentences] [--no-src-tag-filter]
                [--spell-check] [--terminology-norm TERMINOLOGY_NORM]
                [--punctuation-norm]
                [--document-deduplication-threshold DOCUMENT_DEDUPLICATION_THRESHOLD]
                [--remove-glob-rep-sen REMOVE_GLOB_REP_SEN]
                [--dedup-buffer DEDUP_BUFFER]
                name
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

Pull requests are welcome! TeMU members, please do not directly push to the master branch.

### My input format (eg. PubMed XML) is not supported

Sub-class DataParser similarly to how BNEJsonParser and WikipediaParser are implemented. Adapt the DataParserFactory accordingly.

### My output format is not supported.
Sub-class OutputFormatter similarly to how FairseqLMOutputFOrmatter is implemented. Adapt the OutputFormatterFactory accordingly.

### A specific component doesn't adapt to my needs

First, try to change the default arguments. If it still doesn't fit your use case, modify the component, or add a new one.

## Versioning

So far, Corpus Cleaner is only used internally and it is still being developed. The current version is 0.1 but we don't have a proper versioning scheme yet.

## Authors

* [Jordi Armengol Estapé](https://github.com/jordiae)
* [Casimiro Pio Carrino](https://github.com/ccasimiro88)
* [Ona de Gibert](https://github.com/onadegibert)

See also the full list of [contributors](https://github.com/TeMU-BSC/corpus-cleaner/graphs/contributors) who participated in this project.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

Some of the filters of this project are inspired by: <https://github.com/spyysalo/wiki-bert-pipeline>.

# Create a class with methods as filters that recieve as input a list of sentences
# The class' object is initialized with some params of the filters
import fasttext
from langid.langid import LanguageIdentifier
from langid.langid import model as langid_model
from collections import defaultdict
from tqdm import tqdm
import random
import re
import logging
import argparse
from corpus_cleaner.configs.langs import langs


FASTTEXT_MODEL = "../lib/lid.176.bin"

logging.basicConfig(level=logging.DEBUG)


class CleaningErrorSampler:
    def __init__(self, lang_filter: str, sample_size: int, sampling_seed: int):
        self.sample_size = sample_size
        self.lang_filter = lang_filter
        self.sampling_seed = sampling_seed

        # Unlike the pipeline, all the thresholds of the filter are set to a fixed value that enable
        # the retrieval of all the possible cases belonging to each filter
        self.slow_lang_filter_threshold = 0.99
        self.uppercase_filter = 0.99
        self.char_length_filter = 40
        self.digits_filter = 0.1

        self.alphabet = set([])
        for lang in self.lang_filter:
            self.alphabet.update(langs[lang]['alphabet'])
            self.lang_chars = ("".join(char for char in self.alphabet if char.isalpha()))
        self.urls_pattern = re.compile(
            rf'(@)?((http|https)://)?([{self.lang_chars}0-9./?\\\\@\-—_=#])+\.[a-z]{{2,6}}([{self.lang_chars}0-9&/\\\\+~*?%:!@—_=#()-])*')
        self.urls_pattern2 = re.compile('(\[URL\]\.?\w*\s*)+')
        self.emails_pattern = re.compile(
            rf'[{self.lang_chars}0-9_.+-]+@[a-zA-Z0-9-]+\.[a-z0-9-.]+')

        self.fasttext_lid = fasttext.load_model(FASTTEXT_MODEL)
        self.lang_id = LanguageIdentifier.from_modelstring(langid_model, norm_probs=True)
        _ = self.lang_id.classify('')  # force init

        self.filters = []
        # For each filter, store the sentences that have been filtered.
        self.sentences_per_filter = defaultdict(list)
        self._get_filters()

    # For each filter we have: True == not filtered, False == filtered
    # We are interested in the filtered sentences that contains errors
    def _filter_by_lang(self, sentence: str) -> bool:
        res = self.fasttext_lid.predict(sentence.lower())
        lang = res[0][0][-2:]
        conf = res[1][0]
        if lang in self.lang_filter and conf > self.slow_lang_filter_threshold - 0.1:
            return True
        elif lang in self.lang_filter:
            res = self.lang_id.classify(sentence)
            if res[0] in self.lang_filter and res[1] > self.slow_lang_filter_threshold:
                return True
        return False

    def _filter_by_uppercase(self, sentence: str):
        if sum(c.isupper() for c in sentence) / len(sentence) > self.uppercase_filter:
            return False
        return True

    def _filter_by_length(self, sentence: str):
        if len(sentence) < self.char_length_filter:
            return False
        return True

    def _filter_by_digits(self, sentence: str):
        if sum(c.isdigit() for c in sentence) / len(sentence) > self.digits_filter:
            return False
        return True

    def _filter_by_urls(self, sentence: str):
        if self.urls_pattern.findall(sentence) or self.urls_pattern2.findall(sentence):
            return False
        return True

    def _filter_by_emails(self, sentence: str):
        if self.emails_pattern.findall(sentence):
            return False
        return True

    def _no_filter(self, sentence: str):
        return not all(_filter(sentence) for _filter in self.filters if _filter.__name__ != "_no_filter")

    # Unlike the cleaning pipeline, the choice of filters to use is not controlled by command line arguments
    # but is fixed.
    def _get_filters(self):
        self.filters.append(self._filter_by_lang)
        self.filters.append(self._filter_by_uppercase)
        self.filters.append(self._filter_by_length)
        self.filters.append(self._filter_by_digits)
        self.filters.append(self._filter_by_emails)
        self.filters.append(self._filter_by_urls)
        self.filters.append(self._no_filter)

    def classify(self, input_file: str):
        with open(input_file) as fn:
            for sentence in tqdm(fn.readlines(), desc="Filtering sentences"):
                for _filter in self.filters:
                    if not _filter(sentence.strip()):
                        self.sentences_per_filter[_filter.__name__].append(sentence)

        logging.info("Number of sentences found for each error type")
        for error, sentences in self.sentences_per_filter.items():
            logging.info(f"{error}: {len(sentences)}")

        return self.sentences_per_filter

    def sample(self, output_file):
        random.seed(self.sampling_seed)  # set random seed
        # Define a balanced sampling with the same number of sentences sampled per error type
        sentences_per_error_type = round(self.sample_size / len(self.filters))
        sample_sentences = []
        for error, sentences in self.sentences_per_filter.items():
            # Check if the number of sampled sentences is greater than the total number of sentences for each
            # error type before to apply random sampling. If not, select all the sentences of the group type
            if sentences_per_error_type >= len(sentences):
                random_sentences = sentences
                logging.info(f"Random sampling of {len(sentences)} sentences for error type {error}")
            else:
                random_sentences = list(set(random.choices(sentences, k=sentences_per_error_type)))
                logging.info(f"Random sampling of {sentences_per_error_type} sentences for error type {error}")

            sample_sentences.extend(random_sentences)

        sample_sentences = list(set(sample_sentences))
        logging.info(f"Collected sample with {len(sample_sentences)} sentences")

        with open(output_file, 'w') as of:
            of.writelines(sample_sentences)
        return sample_sentences


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-size', type=int,
                        help='Number of sentences in the final sample')
    parser.add_argument('--sampling-seed', type=int,
                        help='Seed used for the random sampling')
    parser.add_argument('--input-file', type=str,
                        help='File containing the sentences that are sampled by error type')
    parser.add_argument('--output-file', type=str,
                        help='File to write the sampled sentences')
    parser.add_argument('--lang-filter', type=str,
                        help='List of languages that should allowed when filtering by lang. '
                             'If not set, no filtering is applied.',
                        nargs='+')

    args = parser.parse_args()

    sampler = CleaningErrorSampler(lang_filter=args.lang_filter, sample_size=args.sample_size,
                                   sampling_seed=args.sampling_seed)

    sentence_per_filter = sampler.classify(args.input_file)
    sample_sentences = sampler.sample(args.output_file)

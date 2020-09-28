import argparse
import random
import logging
import os

SCRIPT_DIR = os.path.realpath(__file__)

logging.basicConfig(level=logging.DEBUG)


# 1. Classify sentences in two classes ERROR/NO ERROR
# 2. Balanced sampling from each class

class ErrorSampler:
    def __init__(self, sample_size: int, sampling_seed: int):
        self.sample_size = sample_size
        self.sampling_seed = sampling_seed
        self.sentences_errors = {'error': [], 'no_error': []}

    @staticmethod
    def check_error(sentence_orig, sentence_clean):
        if not sentence_orig.strip() == sentence_clean.strip():
            return True
        return False

    @staticmethod
    def parse_file(input_file):
        with open(input_file) as fn:
            lines = fn.readlines()
        assert all(len(line.split('\t')) == 2 for line in lines), \
            "Please input a file in a TAB-separated format obtained from the pipeline executed in debug mode"

        return list(set(lines))

    # 2. Classify sentences in two classes ERROR/NO ERROR
    def classify(self, input_file):
        logging.info(f"Classifying sentences in error type from the file: {input_file}")
        lines = self.parse_file(input_file)
        for line in lines:
            sent_orig, sent_clean = line.split('\t')

            if self.check_error(sent_orig, sent_clean):
                self.sentences_errors['error'].append(sent_orig)
            else:
                self.sentences_errors['no_error'].append(sent_orig)

    def sample(self, output_file):
        random.seed(self.sampling_seed)  # set random seed

        # Define a balanced sampling for the ERROR and NO_ERROR classes
        logging.info("Trying balanced sampling from the 'error' and 'no_error' class")
        sentences_per_error_type = round(self.sample_size / 2)
        sample_sentences = []
        for error, sentences in self.sentences_errors.items():
            # Check if the number of sampled sentences is greater than the total number of sentences for each
            # error type before to apply random sampling. If not, select all the sentences of the group type
            if sentences_per_error_type >= len(sentences):
                random_sentences = sentences
            else:
                random_sentences = list(random.choices(sentences, k=sentences_per_error_type))
            logging.info(f"Random sampling of {len(random_sentences)} sentences from '{error}' class")

            sample_sentences.extend(random_sentences)

        sample_sentences = list(set(sample_sentences))

        with open(output_file, 'w') as of:
            of.write('\n'.join(sample_sentences))
        logging.info(f"Collected sample with {len(sample_sentences)} sentences into file {output_file}")

        return sample_sentences


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-size', type=int,
                        help='Number of sentences in the final sample')
    parser.add_argument('--sampling-seed', type=int, default=42,
                        help='Seed used for the random sampling')
    parser.add_argument('--input-file', type=str,
                        help='File containing the sentences that are sampled by error type')
    parser.add_argument('--output-file', type=str,
                        help='File to write the sampled sentences')

    args = parser.parse_args()

    sampler = ErrorSampler(sample_size=args.sample_size, sampling_seed=args.sampling_seed)
    sampler.classify(args.input_file)
    sampler.sample(args.output_file)

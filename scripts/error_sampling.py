import argparse
import random
import logging
import os
import itertools
from collections import defaultdict

SCRIPT_DIR = os.path.realpath(__file__)

logging.basicConfig(level=logging.DEBUG)


class ErrorSampler:
    def __init__(self, sample_size: int, sampling_seed: int):
        self.sample_size = sample_size
        self.sampling_seed = sampling_seed
        self.documents_errors = defaultdict(list)
        self.separator = ' ||| '

    @staticmethod
    def check_error(original, cleaned, input_format):
        if input_format == 'sentence':
            if not original.strip() == cleaned.strip():
                return True
        # Check if there are at least more than 50% of sentences with error in the document
        elif input_format == 'fairseq-lm':
            assert isinstance(original, list) and isinstance(cleaned, list), 'No documents found with fairseq-lm format'
            percentage_error = round(sum([orig != clean for orig, clean in zip(original, cleaned)]) / len(cleaned), 1)
            if percentage_error > 0.5:
                return True
        return False

    def parse_file(self, input_file, input_format):
        with open(input_file) as fn:
            lines = fn.readlines()
        assert all(len(line.split(f"{self.separator}")) == 3 for line in lines if line != '\n'), \
            "Please input a file in a TAB-separated format obtained from the pipeline executed in debug mode"

        if input_format == 'fairseq-lm':
            original = []
            cleaned = []
            operations = []
            original_doc = []
            cleaned_doc = []
            operations_doc = []
            for line in lines:
                if not line == '\n':
                    original_doc.append(line.split(self.separator)[0])
                    cleaned_doc.append(line.split(self.separator)[1])
                    operations_doc.append(line.split(self.separator)[2])
                else:
                    original.append(original_doc)
                    cleaned.append(cleaned_doc)
                    operations.append(operations_doc)
                    original_doc = []
                    cleaned_doc = []
                    operations_doc = []

            return original, cleaned, operations

        elif input_format == 'sentence':
            original = [[line.split(self.separator)[0]] for line in lines]
            cleaned = [[line.split(self.separator)[1]] for line in lines]
            operations = [[line.split(self.separator)[2]] for line in lines]

            return original, cleaned, operations

    # 2. Classify documents in two classes ERROR/NO ERROR
    def classify(self, input_file, input_format, use_unaligned):
        logging.info(f"Classifying documents in error type from the file: {input_file}")
        original, cleaned, operations = self.parse_file(input_file, input_format)
        for orig_doc, clean_doc, ops_doc in zip(original, cleaned, operations):
            doc = [f'{orig_sent}{self.separator}{clean_sent}{self.separator}{ops_sent}'
                   for orig_sent, clean_sent, ops_sent in zip(orig_doc, clean_doc, ops_doc)]
            if self.check_error(orig_doc, clean_doc, input_format):
                if orig_doc[0].startswith('UNALIGNED:'):
                    if use_unaligned:
                        self.documents_errors['unaligned'].append(doc)
                else:
                    self.documents_errors['error'].append(doc)
            else:
                self.documents_errors['no_error'].append(doc)

    def sample(self, output_file):
        # Define a balanced sampling for the ERROR and NO_ERROR classes
        logging.info("Trying balanced sampling from the 'error', 'no_error' and optionally 'unaligned' classes")
        random.seed(self.sampling_seed)  # set fixed random for reproducibility
        number_error_types = len(self.documents_errors.keys())
        sentences_per_error_type = round(self.sample_size / number_error_types)
        sample_documents = []
        for error, documents in self.documents_errors.items():
            # Check if the number of sampled documents is greater than the total number of documents for each
            # error type before to apply random sampling. If not, select all the documents of the group type
            if sentences_per_error_type >= len(documents):
                random_documents = documents
            else:
                random_documents = list(random.sample(documents, k=sentences_per_error_type))
            logging.info(f"Random sampling of {len(random_documents)} documents from '{error}' class")

            sample_documents.extend(random_documents)

        # remove duplicates
        # from: https://www.w3resource.com/python-exercises/list/python-data-type-list-exercise-69.php
        sample_documents.sort()
        list(sample_documents for sample_documents, _ in itertools.groupby(sample_documents))

        with open(output_file, 'w') as of:
            for document in sample_documents:
                for sentence in document:
                    of.write(sentence)
                of.write('DOCUMENT\n')
        logging.info(f"Collected sample with {len(sample_documents)} documents into file {output_file}")

        return sample_documents


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-size', type=int,
                        help='Number of documents in the final sample')
    parser.add_argument('--sampling-seed', type=int, default=42,
                        help='Seed used for the random sampling')
    parser.add_argument('--input-file', type=str,
                        help='File containing the documents that are sampled by error type')
    parser.add_argument('--output-file', type=str,
                        help='File to write the sampled documents')
    parser.add_argument('--input-format', type=str,
                        help='Input format that is either fairseq-lm or sentence')
    parser.add_argument('--use-unaligned', action='store_true',
                        help='Use documents with unaligned original and cleaned sentences')

    args = parser.parse_args()

    sampler = ErrorSampler(sample_size=args.sample_size, sampling_seed=args.sampling_seed)
    sampler.classify(args.input_file, args.input_format, args.use_unaligned)
    sample_documents = sampler.sample(args.output_file)

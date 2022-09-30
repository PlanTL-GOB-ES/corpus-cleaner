import copy
import xml.etree.ElementTree as ET
from os import listdir, makedirs
from os.path import isfile, join, exists
from collections import defaultdict
import argparse
import numpy as np
from csv import writer
from transformers import AutoTokenizer
import logging



parser = argparse.ArgumentParser(description='Introduce the paths of source and target folders.')
parser.add_argument('--splits_path', type=str,
                    help='path for source text splits')
parser.add_argument('--target_path', type=str,
                    help='path for target files')

parser.add_argument('--force_overwrite', action="store_true",
                    help='set if you want to overwrite the created files')    
parser.add_argument('--tokenizer_path', type=str,
                    help='tokenizer path for target files') 

parser.add_argument('--num_train_splits', type=int,
                    help='number splits for training') 
parser.add_argument('--num_dev_splits', type=int,
                    help='number splits for dev') 
parser.add_argument('--num_test_splits', type=int,
                    help='number splits for test') 
parser.add_argument('--num_dev_documents_per_split', type=int,
                    help='documents to retrieve per each dev split') 
parser.add_argument('--num_test_documents_per_split', type=int,
                    help='documents to retrieve per each test split') 


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)                 
logger.setLevel(logging.INFO)

def create_folder(path):
    # Check whether the specified path exists or not
    isExist = exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        makedirs(path)
        logger.info(f"\tNew directory '{path}' has been created")

    return not isExist


def check_files(path, train_name, dev_name, test_name, force_overwrite):

    # Check whether the specified filepaths exists or not
    is_exist_train = exists(join(path, train_name))
    is_exist_dev = exists(join(path, dev_name))
    is_exist_test = exists(join(path, test_name))


    if (is_exist_train or is_exist_dev or  is_exist_test) and not force_overwrite:
        raise Exception(f"One of either {join(path, train_name)}, {path, dev_name} or \
             {test_name} already exists in {path}")


def write_append_plain_text(text, output_txt_filepath):

    # Get the filename without extension and write to disk
    with open(output_txt_filepath, 'a') as writer:
        writer.write(text)

def read_write_split(split_filepath, output_txt_filepath, tokenizer, num_short_files, num_large_files, retrieve_num_docs=None):
    """
    split_filepath:
    output_txt_filepath:
    tokenizer: tokenizer to use to count the tokens
    retrieve_num_docs: number of maximum docs to retrieve per split. Set to None to ignore.
    """


    num_included_files_ini = num_short_files + num_large_files
    num_files = 0

    logger.info("Processing first batch...")

    with open(split_filepath) as myFile:
        text = myFile.read()

        texts_list = text.split("\n\n")

        texts_list = texts_list[1:-1]

        if retrieve_num_docs != -1:
            texts_list = texts_list[:retrieve_num_docs]

        selected_texts = []

        for text in texts_list:
            num_files += 1


            encoded_text = tokenizer.encode(text)

            encoded_text_len = len(encoded_text)
            
            if encoded_text_len < 4096:

                # If dataset is balanced between short and large files, add them
                if abs(num_large_files - num_short_files) < 1000:
                    selected_texts.append(text)
                    if encoded_text_len > 512:
                        num_large_files += 1
                    elif encoded_text_len <= 512:
                        num_short_files +=1
                # If dataset has a lot more large files, add short files only
                elif num_large_files > num_short_files and encoded_text_len <= 512:
                    selected_texts.append(text)
                    num_short_files +=1
                # If dataset has a lot more short files, add large files only
                elif num_large_files < num_short_files and encoded_text_len > 512:
                    selected_texts.append(text)
                    num_large_files +=1

            
            if retrieve_num_docs is not None and num_short_files + num_large_files == retrieve_num_docs:
                break

        text = "\n\n".join(selected_texts)

        write_append_plain_text(text, output_txt_filepath)

        logger.info(f"Split processed")
        logger.info(f'Num short files {num_short_files}')
        logger.info(f'Num large files {num_large_files}')
        logger.info(f'Num included files {num_short_files + num_large_files - num_included_files_ini}')
        logger.info(f'Num files in the dataset {num_files}\n')

        return num_short_files, num_large_files

def build_train_dataset(splits_filenames, splits_path, target_path, tokenizer):

    num_short_files = 0
    num_large_files = 0
    for f in splits_filenames:
        num_short_files, num_large_files = read_write_split(join(splits_path, f), join(target_path, 'train.txt'), 
            tokenizer, num_short_files, num_large_files)



def build_dev_or_test_dataset(splits_filenames, splits_path, target_path, tokenizer, split_name, num_documents_per_split):

    num_short_files = 0
    num_large_files = 0
    for f in splits_filenames:
        num_short_files, num_large_files = read_write_split(join(splits_path, f), join(target_path, split_name),
            tokenizer, num_short_files, num_large_files, num_documents_per_split)


def main(splits_path, target_path, tokenizer_path, force_overwrite):
    """
    'splits_path' path must only contain files with plain text
    """
    files = [f for f in listdir(splits_path) if isfile(join(splits_path, f))]

    seed = 1
    np.random.seed(seed)
    # Shuffle the files
    np.random.shuffle(files)

    logger.info("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path, use_fast=True)


    # num_train_splits = 40
    # num_dev_splits = 20
    # num_test_splits = 20
   
    # num_dev_documents_per_split = 200
    # num_test_documents_per_split = 200


    # Get the train splits from the beginning of the list
    train_files = files[:num_train_splits]
    # Get the dev-test files from the end of the list. We make sure that with the same seed, enlarging the train
    # split will not collide with dev-test.
    dev_files = files[-num_dev_splits:]
    test_files = files[-num_dev_splits-num_test_splits:-num_dev_splits]

    train_name = 'train.txt'
    dev_name = 'dev.txt'
    test_name = 'test.txt'

    # Create folder if needed
    create_folder(target_path)
    # Check if the files exist so as no to overwrite
    check_files(target_path, train_name, dev_name, test_name, force_overwrite)

    logger.info("CREATING TRAIN SPLIT...")
    build_train_dataset(train_files, splits_path, target_path, tokenizer)
    logger.info("\n\nCREATING DEV SPLIT...")
    build_dev_or_test_dataset(dev_files, splits_path, target_path, tokenizer, dev_name, num_dev_documents_per_split)
    logger.info("\n\nCREATING TEST SPLIT...")
    build_dev_or_test_dataset(test_files, splits_path, target_path, tokenizer, test_name, num_test_documents_per_split)


if __name__ == "__main__":
    args = parser.parse_args()

    splits_path = args.splits_path
    target_path = args.target_path
    tokenizer_path = args.tokenizer_path
    force_overwrite = args.force_overwrite


    num_train_splits = args.num_train_splits
    num_dev_splits = args.num_dev_splits
    num_test_splits = args.num_test_splits
   
    num_dev_documents_per_split = args.num_dev_documents_per_split
    num_test_documents_per_split = args.num_test_documents_per_split

    main(splits_path, target_path, tokenizer_path, force_overwrite)


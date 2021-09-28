import os.path
import sys
import hashlib
import pickle
from datetime import datetime

start_time = datetime.now()


def get_hash(string_list):
    p = pickle.dumps(string_list, -1)
    return hashlib.md5(p).hexdigest()


unique_sentences = set()
sentences = []
duplicated_docs_count = 0
unique_docs_count = 0

with open(os.path.join(sys.argv[1] + ".deduplicated"), 'w') as outfile:
    with open(sys.argv[1]) as fileobject:
        for line in fileobject:
            if line == "\n":
                doc_hash = get_hash(sentences)
                if doc_hash not in unique_sentences:
                    # Add has to set
                    unique_sentences.add(doc_hash)
                    # Print to file
                    for element in sentences:
                        outfile.write(element)
                    outfile.write("\n")
                    unique_docs_count = unique_docs_count + 1
                else:
                    duplicated_docs_count = duplicated_docs_count + 1
                # Clear list of sentences
                sentences.clear()
            else:
                sentences.append(line)
        if sentences:
            doc_hash = get_hash(sentences)
            if doc_hash not in unique_sentences:
                # Add has to set
                unique_sentences.add(doc_hash)
                # Print to file
                for element in sentences:
                    outfile.write(element)
                outfile.write("\n")
                unique_docs_count = unique_docs_count + 1
            else:
                duplicated_docs_count = duplicated_docs_count + 1
            # Clear list of sentences
            sentences.clear()


print(f'Unique documents: {unique_docs_count}.')
print(f'Duplicated documents removed: {duplicated_docs_count}.')
print(f'Execution time: {format(datetime.now() - start_time)}.')

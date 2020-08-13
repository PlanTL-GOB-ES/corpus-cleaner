# This script takes as input the path to a file, the boundary to respect, and the number of files you want to split it into.
# Example of usage: python scripts/shard.py -p data/dataset.txt -b '</doc>' -n 5
import optparse
import re

def parse_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-p','--path', action="store", default=False)
    parser.add_option('-b','--boundary', action="store", default=False)
    parser.add_option('-n','--number_of_files', action="store", default=False)
    options, args = parser.parse_args()
    return options.path, options.boundary, options.number_of_files

def write_doc(file, filelines, index, boundary):
    doc_len = 0
    while filelines[index].strip() != boundary:
        file.write(filelines[index])
        index += 1
        doc_len += 1
    else:
        file.write(filelines[index])
        index += 1
        doc_len += 1
    return doc_len

def main():
    path, boundary, number_of_files = parse_arguments()
    filename = re.sub('\.[a-z]+$','',path)
    filelines = open(path,'r',encoding='utf-8').readlines()
    max_lines = round(len(filelines)/int(number_of_files))
    print("Filelines...{}".format(len(filelines)))
    print("Number of files...{}".format(number_of_files))
    print("Max lines per file...{}".format(int(max_lines)))
    files = [open(filename+'%d.txt' % i, 'w', encoding='utf-8') for i in range(int(number_of_files))]
    fileline_index = 0
    try:
        for file in files:
            index = 0
            while index < max_lines:
                doc_len = write_doc(file, filelines, fileline_index, boundary)
                print("Written {} lines to file {}".format(doc_len,file))
                index += doc_len
                fileline_index += doc_len
    except IndexError:
        print("The boundary doesn't appear in the file you provided")
main()
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
    while filelines[index].strip() != boundary:
        file.write(filelines[index])
        index += 1
    else:
        file.write(filelines[index])
        index += 1
    return index

def main():
    path, boundary, number_of_files = parse_arguments()
    filename = re.sub('\.[a-z]+$','',path)
    filelines = open(path,'r').readlines()
    max_lines = round(len(filelines)/int(number_of_files))
    files = [open(filename+'%d.txt' % i, 'w') for i in range(int(number_of_files))]
    fileline_index = 0
    try:
        for file in files:
            index = 0
            while index < max_lines:
                index = write_doc(file, filelines, fileline_index, boundary)
            fileline_index = index
    except IndexError:
        print("The boundary doesn't appear in the file you provided")
main()
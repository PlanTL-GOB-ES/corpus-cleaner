# This script takes as input the path to a file, the boundary to respect, and the number of files you want to split it into.
# Example of usage: python scripts/shard.py -p data/dataset.txt -b '</doc>' -n 5
import optparse
import re


def parse_arguments():
    parser = optparse.OptionParser()
    parser.add_option('-p', '--path', action="store", default=False, help="path to the file")
    parser.add_option('-b', '--boundary', action="store", default=False, help="document boundaries (e.g '', '</doc>', ...")
    parser.add_option('-n', '--number_of_files', action="store", default=False, type=int, help="Number of files into which you want to split")
    parser.add_option('-l', '--lines', action="store", default=False, type=int, help="Total number of lines of the file you want to split")
    options, args = parser.parse_args()
    return options.path, options.boundary, options.number_of_files, options.lines


def line_is_not_boundary(line, boundary):
    if line != boundary:
        return True


def main():
    path, boundary, number_of_files, lines = parse_arguments()
    if lines:
        filelines = lines
    else:
        try:
            filelines = len(open(path, 'r', encoding='utf-8').readlines())
        except MemoryError:
            print(
                "The file you provided is too long, please run wc -l and provide the number of lines with the argument -l")
    max_lines = round(filelines / number_of_files)
    print("Filelines...{}".format(filelines))
    print("Number of files...{}".format(number_of_files))
    print("Max lines per file...{}".format(max_lines))

    filename = re.sub('\.[a-z]+$', '', path)
    files = [open(filename+'%d.txt' % i, 'a', encoding='utf-8') for i in range(int(number_of_files))]
    index = 0
    filename_index = 0
    for line in open(path, 'r', encoding='utf-8'):
        file_to_write = files[filename_index]
        if index < max_lines:
            file_to_write.write(line)
        else:
            if line_is_not_boundary(line.strip(), boundary):
                file_to_write.write(line)
            else:
                filename_index += 1
                index = -1
        index += 1


if __name__ == '__main__':
    main()

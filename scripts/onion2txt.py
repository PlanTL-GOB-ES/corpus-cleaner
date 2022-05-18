# Script to convert onion format to plain txt
# python scripts/onion2txt.py input output
import sys

def onion2txt(filelines):
    txt_lines = []
    par_words = []
    for word in filelines:
        # ignore the first two lines with the start tags
        if word.startswith('<doc'):
            continue
        # If words in paragraph, merge words of paragraphs to create the sentence paragraph
        # based on \n as document boundary and empty the list of words.
        # Empty the document sentences list when a new document is reached (</p> tag) and return the document object
        elif word == '</doc>':
            par_words.append('\n\n')
            txt_lines.append(par_words)
            par_words = []
        elif word == '':
            par_words.append('\n')
            txt_lines.append(par_words)
            par_words = []
        else:
            par_words.append(word)
    return(txt_lines)

def write_file(outfile, txt_lines):
    with open(outfile,'w') as out:
        for par_words in txt_lines:
            par_sentence = ' '.join(par_words)
            out.write(par_sentence)

def main():
    filepath = sys.argv[1]
    outfile = sys.argv[2]

    filelines = open(filepath,'r').read().splitlines()
    txt_lines = onion2txt(filelines)
    write_file(outfile, txt_lines)

main()
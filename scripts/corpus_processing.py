# Source: https://github.com/josecannete/spanish-corpora/blob/master/corpus_processing.py
# Modified by odegiber@gmail.com

import re
import sys
import os

path = 'test/beto/'
output_path = 'test/beto_output'

URLS_RE = re.compile(r'((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')

LISTING_RE = re.compile(r'^(|[a-z]?|[0-9]{0,3})(\-|\.)+( |\n)')

def remove_urls(text):
	return URLS_RE.sub('', text)

def replace_multi_whitespaces(line):
	return ' '.join(line.split())

def remove_listing(line):
	return LISTING_RE.sub('', line)

def main():	
	for filename in os.listdir(path):
		with open(os.path.join(path, filename), "rb") as input_file:
			fout = open(os.path.join(output_path, filename),'w')
			for line in input_file:
				if line == '\n':
					fout.write('')
				else:
					#line = line.lower()
					line = remove_urls(line)
					line = remove_listing(line)
					line = replace_multi_whitespaces(line)

					if line != '':
						fout.write(line+'\n')

if __name__ == '__main__':
    main()

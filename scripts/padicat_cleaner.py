import os
import re
import json
from tqdm import tqdm
from selectolax.parser import HTMLParser
from warcio.archiveiterator import ArchiveIterator
import pathlib
from multiprocessing import Pool
from itertools import chain


def parse_document(uri, html):
    tags = ['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a', 'meta']
    # Replace breaks with a new line in front to make sure they mark an EOL
    html = str(html.decode('utf-8')).replace("<br", "\n<br")
    tree = HTMLParser(html)
    paragraphs = []
    heads = []
    links = []
    keyws = []
    for t in tags:
        selector = t
        for node in tree.css(selector):
            if selector == 'meta':
                if 'name' in node.attributes and 'content' in node.attributes:
                    if node.attributes['name'] == 'keywords' and node.attributes['content'] is not None:
                        keyws.append(node.attributes['content'])
            if selector == 'p':
                paragraphs.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'h1':
                heads.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'h2':
                heads.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'h3':
                heads.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'h4':
                heads.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'h5':
                heads.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'h6':
                heads.append(str(" ".join(node.text(separator=' ').split(' '))))
            if selector == 'a' and 'href' in node.attributes and 'title' in node.attributes:
                links.append(str(node.attributes['href']) + "\|" + str(node.attributes['title']))

    return {'url': uri,
            'p': "<p>".join(paragraphs),
            'heads': "<h>".join(heads),
            'titles': "<t>".join(links),
            'keywords': "<k>".join(keyws)}


def read_file(path):
    file_data = list()
    n_ok = 0
    try:
        with open(path, 'rb') as stream:
            for record in ArchiveIterator(stream):

                if (record.rec_type) == 'response' and ('http' in record.content_type or
                        'html' in record.content_type or 'text/plain' == record.content_type) and record.http_headers and \
                        record.http_headers.statusline[0] in ['2', '3']:

                    uri_data = dict(record.rec_headers.headers)
                    if 'uri' in uri_data:
                        uri = uri_data['uri']
                    else:
                        uri = uri_data['WARC-Target-URI']
                    if os.path.splitext(uri)[1] in SKIP_FORMATS:
                        continue
                    elif record.length > 10000000:
                        # print("Warning! Maximum length exceded for " + uri)
                        continue
                    else:
                        html = record.raw_stream.read()
                        if html and len(html) > 0:
                            data = parse_document(uri, html)
                            file_data.append(data)
                            n_ok = n_ok + 1
    except:
        pass
    return file_data, n_ok


def write_data(path, data):
    output_file = os.path.splitext(os.path.basename(path))[0] + '.json'
    output_file = os.path.join(OUTPUT_PATH, output_file)
    with open(output_file, 'w', encoding='utf-8') as fout:
        for d in data:
            if COMPULSORY_TAG:
                save = d[COMPULSORY_TAG] and len(d[COMPULSORY_TAG]) and re.search('[a-zA-Z]', d[COMPULSORY_TAG])
            else:
                save = True
            if save:
                fout.write(json.dumps(d, ensure_ascii=False))
                fout.write("\n")


def data_mapping(file_path):
    file_data, n_ok = read_file(file_path)
    if len(file_data) > 0:
        write_data(file_path, file_data)
    return n_ok


PATH = '/gpfs/projects/bsc88/corpora/padicat/v1/s1'
#PATH = './sample_data'
OUTPUT_PATH = './output'
SKIP_FORMATS = ['mp4', 'mp3', 'wav', 'jpg', 'jpeg', 'png', 'svg', 'js', 'css']
COMPULSORY_TAG = 'p'
MULTIPROCESSING = True
MULTIPROCESSING_N = 128
# CONTENT_TYPES = ["application/http", "application/html", "text/html", "application/xhtml+xml", "text/plain"]
if __name__ == '__main__':
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    files = [[os.path.join(root, file) for file in files] for root, dirs, files in os.walk(PATH)]
    chained_files = list(chain.from_iterable(files))
    if MULTIPROCESSING:
        n_ok_total = list()
        with Pool(processes=MULTIPROCESSING_N) as p:
            with tqdm(total=len(chained_files)) as pbar:
                for i, res in enumerate(p.imap_unordered(data_mapping, chained_files)):
                    pbar.update()
                    n_ok_total.append(res)
        print(sum(list(n_ok_total)))

            #n_ok_total = p.map(data_mapping, chained_files), total=len(chained_files)
    else:
        total = map(data_mapping, tqdm(chained_files))
        print(sum(list(total)))

import argparse


def parse(input_file, corpora_tag, doc_tag):

    # Get deduplicated data
    corpora_sentence = []
    doc_sentences = []
    par_words = []
    with open(input_file) as fn:
        for line in fn:
            line_index = line.split("\t")[0]
            line = "\t".join(line.split("\t")[1:])

            # If words in document, merge words of document to create the sentences paragraph
            # based on \n as document boundary (<corpora_tag>) and empty the list of words.
            # Empty the document sentences list when a new document is reached (</doc_tag>) and return the document object
            if line in [f"</{doc_tag}>\n", "\n"]:
                if par_words:
                    par_sentence = " ".join(par_words)
                    doc_sentences.append(par_sentence + "\n")
                    par_words = []
                    if line == f"</{doc_tag}>\n":
                        doc_sentences.append("\n")
                        corpora_sentence.append(doc_sentences)
                        doc_sentences = []
            elif line in [
                f"<{corpora_tag}>\n",
                f"</{corpora_tag}>\n",
                f"<{doc_tag}>\n",
            ]:
                continue
            elif line.startswith(f"<{doc_tag}"):
                continue
            else:
                if line_index == "0":
                    par_words.append(line.strip("\n"))

    # Write to file
    output_file = f"{input_file}.txt"
    with open(output_file, "w") as gn:
        gn.writelines(sent for doc in corpora_sentence for sent in doc)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("onion-input-file", help="Input file with Onion format")
    parser.add_argument("--corpora-tag", default="corpora", help="Corpora tag name")
    parser.add_argument("--doc-tag", default="doc", help="Paragraph tag name")
    args = parser.parse_args()

    # parse(args.onion_input_file)
    parse(
        args.onion_input_file,
        args.corpora_tag,
        args.doc_tag,
    )

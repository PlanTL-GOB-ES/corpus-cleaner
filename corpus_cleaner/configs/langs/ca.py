import string

alphabet = set(list(string.ascii_lowercase) + list('àèéíòóú'))
fasttext = True
langid = True

ca = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)

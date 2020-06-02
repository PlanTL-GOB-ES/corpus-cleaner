import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('àèéíòóúïüç·') + list('ÀÈÉÍÒÓÚÏÜÇ'))
fasttext = True
langid = True

ca = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)

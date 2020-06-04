import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('æøå') + list('ÆØÅ'))
fasttext = True
langid = True

no = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)
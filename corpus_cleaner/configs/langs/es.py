import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('áééíóúüñ') + list('ÁÉÍÓÚÜÑ'))
fasttext = True
langid = True

es = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)

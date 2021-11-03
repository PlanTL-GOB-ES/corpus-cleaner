import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('áééíóúüñç') + list('ÁÉÍÓÚÜÑÇ'))
fasttext = True
langid = True

gl = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)

import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('äåöšž') + list('ÄÅÖŠŽ'))
fasttext = True
langid = True

fi = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)
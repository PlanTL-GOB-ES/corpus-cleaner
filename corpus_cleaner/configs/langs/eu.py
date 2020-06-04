import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('çñ') + list('ÇÑ'))
fasttext = True
langid = True

eu = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)

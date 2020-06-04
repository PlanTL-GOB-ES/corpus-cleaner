import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('äöüß') + list('ÄÖÜẞ'))
fasttext = True
langid = True

de = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)

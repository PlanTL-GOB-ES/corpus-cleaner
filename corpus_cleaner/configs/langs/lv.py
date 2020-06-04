import string

alphabet = set(list(string.ascii_uppercase) + list(string.ascii_lowercase) + list('āčēģīķļņšūž') + list('ĀČĒĢĪĶĻŅŠŪŽ'))
fasttext = True
langid = True

lv = dict(alphabet=alphabet, fasttext=fasttext, langid=langid)
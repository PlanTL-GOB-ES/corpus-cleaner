from .ca import ca
from .en import en
from .eu import eu
from .es import es

langs = dict(ca=ca, es=es, en=en, eu=eu)

__all__ = ['langs']

try:
	from werkzeug.utils import cached_property
except ImportError:
	try:
		from cached_property import cached_property
	except ImportError:
		cached_property = property

from .helpers import isiterable, ismapping
from .message_bag import MessageBag
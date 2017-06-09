from collections import Iterable
from datetime import datetime, date

import six
from sqlalchemy_utils import types
from tea.carbon import carbon
from dateutil import tz
try:
	import arrow
except ImportError:
	arrow = None

if arrow:
	from arrow.util import is_timestamp


class Carbon(types.ArrowType):

	arrow_factory = carbon

	def __init__(self, timezone=False, utc=True, factory=None, **kwargs):
		self.arrow_factory = factory or self.arrow_factory
		self.to_utc = utc
		super(Carbon, self).__init__(timezone=timezone, **kwargs)

	def process_bind_param(self, value, dialect):
		if not value:
			return value
		value = self._coerce(value)
		if self.to_utc:
			value = value.to('UTC')
		return value.datetime if self.impl.timezone else value.naive
		
	def _coerce(self, value):
		if value is None or isinstance(value, self.arrow_factory.type):
			return value
		if isinstance(value, six.string_types):
			value = self.arrow_factory.get(value)
		elif is_timestamp(value):
			value = self.arrow_factory.get(value)
		elif isinstance(value, Iterable):
			value = self.arrow_factory.get(*value)
		elif isinstance(value, datetime):
			value = self.arrow_factory.get(value)
		elif isinstance(value, arrow.Arrow):
			value = self.arrow_factory.get(value)
		return value


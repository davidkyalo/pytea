from tea.utils import six
from functools import reduce
import operator
from tea.collections import stack
from tea.constants import NOT_PROVIDED

class MessageBag(object):
	"""
	An error while validating data.
	Forked from django
	"""
	def __init__(self, message=None, code=None, placeholders=None, **kwargs):
		"""
		The `message` argument can be a single error, a list of errors, or a
		dictionary that maps field names to lists of errors. What we define as
		an "error" can be either a simple string or an instance of
		MessageBag with its message attribute set, and what we define as
		list or dictionary can be an actual `list` or `dict` or an instance
		of MessageBag with its `message_list` or `message_dict` attribute set.
		"""
		if message is None and kwargs:
			message = kwargs

		if isinstance(message, MessageBag):
			if hasattr(message, 'message_dict'):
				message = message.message_dict
			# PY2 has a `message` property which is always there so we can't
			# duck-type on it. It was introduced in Python 2.5 and already
			# deprecated in Python 2.6.
			elif not hasattr(message, 'message' if six.PY3 else 'code'):
				message = message.message_list
			else:
				message, code, placeholders = message.message, message.code, message.placeholders

		if isinstance(message, dict):
			self.message_dict = stack()
			for field, messages in message.items():
				if not isinstance(messages, MessageBag):
					messages = self._make(messages)
				self.message_dict[field] = messages.message_list

		elif isinstance(message, list):
			self.message_list = []
			for message in message:
				# Normalize plain strings to instances of MessageBag.
				if not isinstance(message, MessageBag):
					message = self._make(message)
				if hasattr(message, 'message_dict'):
					self.message_list.extend(sum(message.message_dict.values(), []))
				else:
					self.message_list.extend(message.message_list)
		else:
			self.message = message
			self.code = code
			self.placeholders = placeholders or {}
			self.message_list = [self]

	def to_dict(self, strict=True):
		# Trigger an AttributeError if this MessageBag
		# doesn't have an message_dict.
		getattr(self, 'message_dict')
		return stack(self)

	def to_list(self):
		if hasattr(self, 'message_dict'):
			return reduce(operator.add, stack(self).values())
		return list(self)

	@property
	def all(self):
		return self.to_list()

	@property
	def messages(self):
		if hasattr(self, 'message_dict'):
			return self.to_dict()
		return self.to_list()

	def has(self, key):
		message_dict = getattr(self, 'message_dict')
		return key in message_dict

	def get(self, key, default=None):
		return self.message_dict.get(key, default)

	def update(self, message_dict):
		if hasattr(self, 'message_dict'):
			for field, message_list in self.message_dict.items():
				message_dict.setdefault(field, []).extend(message_list)
		else:
			message_dict.setdefault('__all__', []).extend(self.message_list)
		return message_dict

	def extend(self, messages):
		pass

	def format(self, template, *args, **kwargs):
		messages = []
		for message in self.all:
			messages.append(template.format(*args, message=message, **kwargs))
		return '\n'.join(messages)

	def _make(self, message, code=None, placeholders=None):
		return self.__class__(message, code=code, placeholders=placeholders)

	def __iter__(self):
		if hasattr(self, 'message_dict'):
			for field, errors in self.message_dict.items():
				yield field, list(self._make(errors))
		else:
			for error in self.message_list:
				message = str(error.message).format(**error.placeholders)
				yield message.replace('``', '').replace('""', '').replace("''", '')

	def __str__(self):
		if hasattr(self, 'message_dict'):
			return repr(stack(self))
		return repr(list(self))

	def __repr__(self):
		return '%s(%s)' % (self.__class__.__name__, self)


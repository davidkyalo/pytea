from tea.utils import six, MessageBag
from functools import reduce
import operator
from tea.collections import stack
from tea.constants import NOT_PROVIDED

NON_FIELD_ERRORS = '__all__'

class DataSet(object):
	"""docstring for DataSet"""
	def __init__(self, data, getter=None, setter=None):
		if isinstance(data, DataSet):
			self.data = data.data
			self.getter = data.getter
			self.setter = data.setter
		else:
			self.data = data
			if getter is not None:
				self.getter = getter
			else:
				if isinstance(data, dict):
					self.getter = _dict_get_value
				else:
					self.getter = _obj_getattr
			if setter is not None:
				self.setter = setter
			else:
				if isinstance(data, dict):
					self.setter = _dict_set_value
				else:
					self.setter = _obj_setattr

	def get(self, key, default=NOT_PROVIDED):
		return self.getter(self.data, key, default)

	def set(self, key, value):
		return self.setter(self.data, key, value)

class ValidationError(MessageBag, Exception):
	pass


class _ValidationError(Exception):
	"""
	An error while validating data.
	Forked from django
	"""
	def __init__(self, message, code=None, placeholders=None):
		"""
		The `message` argument can be a single error, a list of errors, or a
		dictionary that maps field names to lists of errors. What we define as
		an "error" can be either a simple string or an instance of
		ValidationError with its message attribute set, and what we define as
		list or dictionary can be an actual `list` or `dict` or an instance
		of ValidationError with its `error_list` or `error_dict` attribute set.
		"""

		# PY2 can't pickle naive exception: http://bugs.python.org/issue1692335.
		super(ValidationError, self).__init__(message, code, placeholders)

		if isinstance(message, ValidationError):
			if hasattr(message, 'error_dict'):
				message = message.error_dict
			# PY2 has a `message` property which is always there so we can't
			# duck-type on it. It was introduced in Python 2.5 and already
			# deprecated in Python 2.6.
			elif not hasattr(message, 'message' if six.PY3 else 'code'):
				message = message.error_list
			else:
				message, code, placeholders = message.message, message.code, message.placeholders

		if isinstance(message, dict):
			self.error_dict = stack()
			for field, messages in message.items():
				if not isinstance(messages, ValidationError):
					messages = ValidationError(messages)
				self.error_dict[field] = messages.error_list

		elif isinstance(message, list):
			self.error_list = []
			for message in message:
				# Normalize plain strings to instances of ValidationError.
				if not isinstance(message, ValidationError):
					message = ValidationError(message)
				if hasattr(message, 'error_dict'):
					self.error_list.extend(sum(message.error_dict.values(), []))
				else:
					self.error_list.extend(message.error_list)
		else:
			self.message = message
			self.code = code
			self.placeholders = placeholders or {}
			self.error_list = [self]

	@property
	def message_dict(self):
		# Trigger an AttributeError if this ValidationError
		# doesn't have an error_dict.
		getattr(self, 'error_dict')
		return stack(self)

	@property
	def messages(self):
		if hasattr(self, 'error_dict'):
			return reduce(operator.add, stack(self).values())
		return list(self)

	def has(self, key):
		error_dict = getattr(self, 'error_dict')
		return key in error_dict

	def update_error_dict(self, error_dict):
		if hasattr(self, 'error_dict'):
			for field, error_list in self.error_dict.items():
				error_dict.setdefault(field, []).extend(error_list)
		else:
			error_dict.setdefault(NON_FIELD_ERRORS, []).extend(self.error_list)
		return error_dict

	def format(self, template, *args, **kwargs):
		messages = []
		for message in self.messages:
			messages.append(template.format(*args, message=message, **kwargs))
		return '\n'.join(messages)

	def __iter__(self):
		if hasattr(self, 'error_dict'):
			for field, errors in self.error_dict.items():
				yield field, list(ValidationError(errors))
		else:
			for error in self.error_list:
				message = str(error.message).format(**error.placeholders)
				yield message.replace('``', '').replace('""', '').replace("''", '')

	def __str__(self):
		if hasattr(self, 'error_dict'):
			return repr(stack(self))
		return repr(list(self))

	def __repr__(self):
		return 'ValidationError(%s)' % self


def _dict_get_value(dct, key, default=NOT_PROVIDED):
	return dct.get(key, default)

def _obj_getattr(obj, attr, default=NOT_PROVIDED):
	return getattr(obj, attr, default)

def _dict_set_value(dct, key, value):
	dct[key] = value

def _obj_setattr(obj, attr, value):
	setattr(obj, attr, value)

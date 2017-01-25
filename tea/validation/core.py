from tea.utils import six
from functools import reduce
import operator
from tea.collections import stack
from tea import uzi

class RuleSet(object):
	def __init__(self, rules=None):
		self.rules = stack(rules)

	def add(self, field, *rules, field_name=None):
		self.rules[field] = rules

	def prepare_rule(self, rule, name=None):
		pass


NON_FIELD_ERRORS = '__all__'

class ValidationError(Exception):
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

	def update_error_dict(self, error_dict):
		if hasattr(self, 'error_dict'):
			for field, error_list in self.error_dict.items():
				error_dict.setdefault(field, []).extend(error_list)
		else:
			error_dict.setdefault(NON_FIELD_ERRORS, []).extend(self.error_list)
		return error_dict

	def __iter__(self):
		if hasattr(self, 'error_dict'):
			for field, errors in self.error_dict.items():
				yield field, list(ValidationError(errors))
		else:
			for error in self.error_list:
				message = error.message
				yield uzi.compact(str(message).format(**error.placeholders))

	def __str__(self):
		if hasattr(self, 'error_dict'):
			return repr(stack(self))
		return repr(list(self))

	def __repr__(self):
		return 'ValidationError(%s)' % self

	def __bool__(self):
		return False

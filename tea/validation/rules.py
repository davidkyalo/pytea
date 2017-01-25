import re
from tea.constants import NOT_PROVIDED, EMPTY, NOTHING
from .core import ValidationError
from tea.collections import stack
from tea import uzi
from tea.utils import six
from tea.utils.ipv46 import IPV4_REGEX, is_valid_ipv6, is_valid_ipv4, is_valid_ip
from tea.utils.encoding import force_text
from urllib.parse import urlsplit, urlunsplit


##################################################################
# Constants
##################################################################

EMPTY_VALUES = (None, '', NOT_PROVIDED, EMPTY, NOTHING)
EMPTY_COLLECTIONS = ([], (), {})
EMPTY_VALUES_AND_COLLECTIONS = EMPTY_VALUES + EMPTY_COLLECTIONS


##################################################################
# Base
##################################################################

class RuleMeta(type):

	def __new__(mcls, name, bases, nspace):
		cls = super(RuleMeta, mcls).__new__(mcls, name, bases, nspace)
		if getattr(cls, 'placeholders', None) is None:
			setattr(cls, 'placeholders', {})
		for base in reversed(bases):
			if isinstance(base, RuleMeta):
				cls.placeholders.update(base.placeholders)
		return cls

class Rule(metaclass=RuleMeta):
	"""The Base Validation Rules Class"""
	message = ""
	code = "invalid"
	placeholders = None
	ignore_empty = False
	empty_values = EMPTY_VALUES
	_name_placeholder_key = '__name__'
	_value_placeholder_key = '__value__'

	def __init__(self, message=None, placeholders=None, name=None, code=None,
	             ignore_empty=None, empty_values=None):
		if message is not None:
			self.message = message
		if code is not None:
			self.code = code
		if ignore_empty is not None:
			self.ignore_empty = ignore_empty
		if empty_values is not None:
			self.empty_values = empty_values

		self.placeholders = self.__class__.placeholders.copy()
		self.update_placeholders(placeholders)

		if name is None:
			name = self.get_name_placeholder("")

		self.set_name_placeholder(name)
		self.set_default_value_placeholder(self.get_default_value_placeholder(None))

	def __call__(self, value, data_set=None, placeholders=None):
		return self.validate(value, data_set, placeholders)

	def validate(self, value, data_set=None, placeholders=None):
		if not self.check(value, data_set):
			return self.create_error(self.get_placeholders(
						placeholders, data_set, {self._value_placeholder_key:value}))
		return True

	def should_ignore(self, value):
		return self.ignore_empty and value in self.empty_values

	def check(self, value, data_set=None):
		error = "Abstract method check() is not implemented in {0}."
		raise NotImplentedError(error.format(self.__class__))

	def create_error(self, placeholders):
		return ValidationError(self.get_message(), self.get_code(), placeholders)

	def get_message(self):
		return self.message

	def get_code(self):
		return self.code

	def get_placeholders(self, *args, **kwargs):
		return _update_placeholders(self.placeholders.copy(), *args, **kwargs)

	def update_placeholders(self, *dicts, **kwargs):
		_update_placeholders(self.placeholders, *dicts, **kwargs)

	def get_name_placeholder(self, default=None):
		return self.placeholders.get(self._name_placeholder_key, default)

	def set_name_placeholder(self, name):
		self.placeholders[self._name_placeholder_key] = uzi.humanize(name)

	def get_default_value_placeholder(self, default=None):
		return self.placeholders.get(self._value_placeholder_key, default)

	def set_default_value_placeholder(self, value):
		self.placeholders[self._value_placeholder_key] = value


##################################################################
# Required, NotEmpty, Empty
##################################################################

class Required(Rule):
	message = "Field {__name__} is required."

	def check(self, value, data_set=None):
		return value not in EMPTY_VALUES

class NotEmpty(Rule):
	message = "Field {__name__} should not be empty."

	def check(self, value, data_set=None):
		return value not in EMPTY_VALUES_AND_COLLECTIONS

class Empty(Rule):
	message = "Field {__name__} should be empty."

	def check(self, value, data_set=None):
		return value in EMPTY_VALUES_AND_COLLECTIONS


##################################################################
# Regex
##################################################################

class Regex(Rule):
	message = "The value `{__value__}` in field {__name__} is invalid."
	regex = ''
	ignore_empty = False
	# code = 'invalid_regex'
	inverse_match = False
	flags = 0

	def __init__(self, regex=None, message=None, placeholders=None, name=None,
	             code=None, inverse_match=None, flags=None, ignore_empty=None, empty_values=None):
		super(Regex, self).__init__(
							message=message, placeholders=placeholders, name=name,
							code=code, ignore_empty=ignore_empty, empty_values=empty_values)

		if regex is not None:
			self.regex = regex
		if inverse_match is not None:
			self.inverse_match = inverse_match
		if flags is not None:
			self.flags = flags
		if self.flags and not isinstance(self.regex, six.string_types):
			raise TypeError("If the flags are set, regex must be a regular expression string.")

		if isinstance(self.regex, six.string_types):
			self.regex = re.compile(self.regex, self.flags)

	def check(self, value, data_set=None):
		return self.should_ignore(value) or \
			self.inverse_match is not bool(self.regex.search(force_text(value)))


##################################################################
# URLs
##################################################################

class Url(Regex):
	regex = re.compile(
		r'^(?:[a-z0-9\.\-]*)://'  # scheme is validated separately
		r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}(?<!-)\.?)|'  # domain...
		r'localhost|'  # localhost...
		r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
		r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
		r'(?::\d+)?'  # optional port
		r'(?:/?|[/?]\S+)$', re.IGNORECASE)

	message ="Field {__name__} must be a valid URL."
	schemes = ['http', 'https', 'ftp', 'ftps']

	def __init__(self, schemes=None, **kwargs):
		super(Url, self).__init__(**kwargs)
		if schemes is not None:
			self.schemes = schemes

	def check(self, value, data_set=None):
		if self.should_ignore(value):
			return True
		value = force_text(value)
		# Check first if the scheme is valid
		scheme = value.split('://')[0].lower()
		if scheme not in self.schemes:
			return False
		# Then check full URL
		if super(Url, self).check(value, data_set):
			return True
		if not value:
			return False

		scheme, netloc, path, query, fragment = urlsplit(value)
		try:
			netloc = netloc.encode('idna').decode('ascii')  # IDN -> ACE
		except UnicodeError:  # invalid domain part
			return False

		url = urlunsplit((scheme, netloc, path, query, fragment))
		return super(Url, self).check(url, data_set)



##################################################################
# Email Address
##################################################################

class Email(Rule):
	message = "Field {__name__} must be a valid email address."
	user_regex = re.compile(
		r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*$"  # dot-atom
		r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"$)',  # quoted-string
		re.IGNORECASE)
	domain_regex = re.compile(
		r'(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}|[A-Z0-9-]{2,}(?<!-))$',
		re.IGNORECASE)
	literal_regex = re.compile(
		# literal form, ipv4 or ipv6 address (SMTP 4.1.3)
		r'\[([A-f0-9:\.]+)\]$',
		re.IGNORECASE)
	domain_whitelist = ['localhost', '127.0.0.1']

	def __init__(self, whitelist=None, **kwargs):
		super(Email, self).__init__(**kwargs)
		if whitelist is not None:
			self.domain_whitelist = whitelist

	def check(self, value, data_set=None):
		if self.should_ignore(value):
			return True

		value = force_text(value)

		if not value or '@' not in value:
			return False

		user, domain = value.rsplit('@', 1)

		if not self.user_regex.match(user):
			return False

		if domain in self.domain_whitelist or self.check_domain(domain):
			return True

		# Try for possible IDN domain-part
		try:
			domain = domain.encode('idna').decode('ascii')
			return self.check_domain(domain)
		except UnicodeError:
			return False

	def check_domain(self, domain):
		if self.domain_regex.match(domain):
			return True
		literal_match = self.literal_regex.match(domain)
		if literal_match:
			ip_address = literal_match.group(1)
			return is_valid_ip(ip_address)
		return False



##################################################################
# IP Addresses
##################################################################

class IPv4(Regex):
	message = "Field {__name__} must be a valid IPv4 address."
	regex = IPV4_REGEX


class IPv6(Rule):
	message = "Field {__name__} must be a valid IPv6 address."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or is_valid_ipv6(force_text(value))


class IP(Rule):
	message = "Field {__name__} must be a valid IP address."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or is_valid_ip(force_text(value))

#Alias
IpAddress = IP



##################################################################
# Numeric
##################################################################

class Integer(Rule):
	message = "Field {__name__} must be an integer."

	def check(self, value, data_set=None):
		if self.should_ignore(value):
			return True
		try:
			return force_text(int(value)) == force_text(value)
		except (ValueError, TypeError):
			return False



##################################################################
# Functions
##################################################################

def _update_placeholders(placeholders, *args, **kwargs):
	for arg in args:
		if arg is not None:
			placeholders.update(arg)
	placeholders.update(kwargs)
	return placeholders



##################################################################
# Late Imports.
##################################################################


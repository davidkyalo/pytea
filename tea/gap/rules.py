import re
from tea.constants import NOT_PROVIDED, EMPTY, NOTHING
from .core import ValidationError, DataSet
from tea.collections import stack
from tea import uzi
from tea.utils import six
from tea.utils.ipv46 import IPV4_REGEX, is_valid_ipv6, is_valid_ipv4, is_valid_ip
from tea.utils.encoding import force_text
from urllib.parse import urlsplit, urlunsplit
from tea.decorators import cached_property

##################################################################
# Constants
##################################################################

MISSING_VALUES = (NOT_PROVIDED, NOTHING, None, '')
EMPTY_VALUES = MISSING_VALUES
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
			if isinstance(data_set, DataSet):
				data_set = data_set.data
			value_placeholder = {
				self._value_placeholder_key : self.clean_value(value)
			}
			placeholders = self.get_placeholders(placeholders, data_set, value_placeholder)
			raise self.create_error(placeholders)

	def should_ignore(self, value):
		return self.ignore_empty and value in self.empty_values

	def check(self, value, data_set=None):
		error = "Abstract method check() is not implemented in {0}."
		raise NotImplementedError(error.format(self.__class__))

	def create_error(self, placeholders):
		return ValidationError(self.get_message(), self.get_code(), placeholders)

	def clean_value(self, value):
		return value

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
		self.placeholders[self._name_placeholder_key] = name

	def get_default_value_placeholder(self, default=None):
		return self.placeholders.get(self._value_placeholder_key, default)

	def set_default_value_placeholder(self, value):
		self.placeholders[self._value_placeholder_key] = value


##################################################################
# Required, NotEmpty, Empty
##################################################################

class Required(Rule):
	message = "The `{__name__}` field is required."
	missing = MISSING_VALUES

	def __init__(self, missing=None, **kwargs):
		super(Required, self).__init__(**kwargs)
		if missing is not None:
			self.missing = self.missing + tuple(missing)

	def check(self, value, data_set=None):
		return value not in self.missing

class NotEmpty(Rule):
	message = "The `{__name__}` field should not be empty."

	def check(self, value, data_set=None):
		return value not in EMPTY_VALUES_AND_COLLECTIONS

class Empty(Rule):
	message = "The `{__name__}` field should be empty."

	def check(self, value, data_set=None):
		return value in EMPTY_VALUES_AND_COLLECTIONS


##################################################################
# Regex
##################################################################

class Regex(Rule):
	message = "The value `{__value__}` in `{__name__}` is invalid."
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

	message ="The `{__name__}` must be a valid URL."
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


class Slug(Regex):
	regex = re.compile(r'^[-a-zA-Z0-9_]+$')
	message = "The `{__name__}` should only consist of letters, numbers, underscores or hyphens."


##################################################################
# Email Address
##################################################################

class Email(Rule):
	message = "The `{__name__}` must be a valid email address."
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
	message = "The `{__name__}` must be a valid IPv4 address."
	regex = IPV4_REGEX


class IPv6(Rule):
	message = "The `{__name__}` must be a valid IPv6 address."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or is_valid_ipv6(force_text(value))


class IP(Rule):
	message = "The `{__name__}` must be a valid IP address."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or is_valid_ip(force_text(value))

#Alias
IpAddress = IP



##################################################################
# Numeric
##################################################################

class Integer(Rule):
	message = "The `{__name__}` must be an integer."

	def check(self, value, data_set=None):
		if self.should_ignore(value):
			return True
		try:
			return force_text(int(value)) == force_text(value)
		except (ValueError, TypeError):
			return False


##################################################################
# Limits
##################################################################

class _Limit(Rule):
	limit = None
	def __init__(self, limit, **kwargs):
		super(_Limit, self).__init__(**kwargs)
		self.limit = limit
		self.placeholders['limit'] = limit

class Max(_Limit):
	message = "The `{__name__}` must be less than or equal to {limit}."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or self.limit >= value

class Min(_Limit):
	message = "The `{__name__}` must be greater than or equal to {limit}."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or self.limit <= value

class MaxLen(_Limit):
	message = "The `{__name__}` must be at most {limit} character(s)."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or self.limit >= len(value)

class MinLen(_Limit):
	message = "The `{__name__}` must be at least {limit} character(s)."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or self.limit <= len(value)

class Length(_Limit):
	message = "The `{__name__}` must be {limit} character(s)."

	def check(self, value, data_set=None):
		return self.should_ignore(value) or self.limit == len(value)


##################################################################
#
##################################################################

class Passes(Rule):
	message = "The `{__name__}` must pass a condition."
	condition = None
	kwargs = None

	def __init__(self, condition, args=None, kwargs=None, **_kwargs):
		super(Passes, self).__init__(**_kwargs)

		if not callable(condition):
			raise TypeError("Condition should be callable.")

		self.condition = condition
		self.args = args or ()
		self.kwargs = kwargs or {}

	def check(self, value, data_set=None):
		return self.should_ignore(value) or \
			self.condition(value, data_set, *self.args, **self.kwargs)

class Fails(Rule):
	message = "The `{__name__}` must fail a condition."
	condition = None
	kwargs = None

	def __init__(self, condition, args=None, kwargs=None, **_kwargs):
		super(Fails, self).__init__(**_kwargs)

		if not callable(condition):
			raise TypeError("Condition should be callable.")

		self.condition = condition
		self.args = args or ()
		self.kwargs = kwargs or {}

	def check(self, value, data_set=None):
		return self.should_ignore(value) or \
			not self.condition(value, data_set, *self.args, **self.kwargs)


class Same(Rule):
	message = "The `{__name__}` and `{other}` fields must match."
	other = None

	def __init__(self, other, other_name=None, **kwargs):
		super(Same, self).__init__(**kwargs)
		self.other = other
		if 'other' not in self.placeholders:
			other_name = other_name or uzi.humanize(force_text(other)).title()
			self.placeholders['other'] = other_name

	def check(self, value, data_set):
		if self.should_ignore(value):
			return True
		other = DataSet(data_set).get(self.other)
		return value == other


class Equals(Rule):
	message = "The value of '{__name__}' should be equal to {other_value}."
	_other_value = None
	as_str = False
	_check_cache = False

	def __init__(self, value, as_str=False, **kwargs):
		super(Equals, self).__init__(**kwargs)
		self._other_value = value
		self.as_str = as_str

	def check(self, value, data_set=None):
		if self.should_ignore(value):
			return True
		if self.as_str:
			return force_text(value) == force_text(self.other_value)
		return value == self.other_value

	@cached_property
	def other_value(self):
		other = self._other_value() if callable(self._other_value) else self._other_value
		self.placeholders.setdefault('other_value', other)
		return other


##################################################################
# Functions
##################################################################

class PhoneNumber(Regex):
	regex = re.compile(r'^\+?1?\d{9,15}$')
	message = "The '{__name__}' field must be a valid phone number in the format: '+xxxxxxxxxx'. Up to 15 digits allowed."

class PhoneNumberE164(Regex):
	regex = re.compile(r'^\+[1-9]\d{8,14}$')
	message = "The '{__name__}' field must be a valid phone number in the format: '+xxxxxxxxxx'. Up to 15 digits allowed."

##################################################################
# Functions
##################################################################

def _update_placeholders(placeholders, *args, **kwargs):
	for arg in args:
		if arg is not None:
			if not isinstance(arg, dict):
				arg = arg.__dict__
			placeholders.update(arg)
	placeholders.update(kwargs)
	return placeholders


def _get_rule_instance(rule, name=None, message=None):
	if isinstance(rule, RuleMeta):
		rule = rule()
	if isinstance(rule, Rule):
		if name is not None and rule.get_name_placeholder("") == "":
			rule.set_name_placeholder(name)
		if message is not None and rule.message == rule.__class__.message:
			rule.message = message

	return rule


##################################################################
# Late Imports.
##################################################################


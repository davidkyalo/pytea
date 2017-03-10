import unittest
from nose.tools import raises
from tea import uzi
from tea.collections import Stack
from tea.gap import ValidationError
from nose_parameterized import parameterized
from tea.gap.rules import (
	Rule, Required, Regex, Url, Email, Integer, IPv4, IPv6, IP,
	Min, Max, MaxLen, MinLen, Length, Passes, Fails, Equals,
	EMPTY, NOTHING, NOT_PROVIDED,
	EMPTY_VALUES, EMPTY_COLLECTIONS, EMPTY_VALUES_AND_COLLECTIONS)


class DummyRule(Rule):

	def check(self, value, data_set=None):
		return True if value else False

class FailRule(Rule):
	message = "Field {__name__} failed with value {__value__}"

	def check(self, value, data_set=None):
		return False

class PassRule(Rule):

	def check(self, value, data_set=None):
		return True

class DummyObject(object):

	def __init__(self, value='foo-bar'):
		self.value = value

	def __str__(self):
		return str(self.value)

	def __eq__(self, other):
		return isinstance(other, DummyObject) and other.value == self.value



class RulesTest(unittest.TestCase):

	@parameterized.expand([
			('basic',),
			('with message', "Error message."),
			('with placeholders', "Error message.", dict(value_1=1,value_2=2,value_3=3)),
			('with name', "Error message.", None, 'foo'),
			('with name in placeholders', None, {Rule._name_placeholder_key : 'foo'}),
			('with code', None, None, None, 'code_black'),
		])
	def test_create_instance(self, _, message=None, placeholders=None, name=None, code=None):
		rule = Rule(message, placeholders, name, code)
		placeholders = placeholders or {}

		self.assertEqual(message or "", rule.get_message())

		if rule._name_placeholder_key not in placeholders:
			placeholders[rule._name_placeholder_key] = rule.get_name_placeholder()
		if rule._value_placeholder_key not in placeholders:
			placeholders[rule._value_placeholder_key] = rule.get_default_value_placeholder()
		self.assertEqual(dict(placeholders), dict(rule.get_placeholders()))

		name = name or placeholders.get(rule._name_placeholder_key, "")
		self.assertEqual(uzi.humanize(name), rule.get_name_placeholder())

		if code is not None:
			self.assertEqual(code, rule.get_code())

	@parameterized.expand([
			(False, ''),
			(True, '', True),
			(False, None, False),
			(True, None, True),
			(True, NOTHING, True),
			(True, NOT_PROVIDED, True),
			(False, 'abc', True),
			(False, False, True),
			(False, [], True),
			(True, [], True, EMPTY_COLLECTIONS),
		])
	def test_should_ignore(self, expected, value, ignore_empty=None, empty_values=None):
		rule = DummyRule(ignore_empty=ignore_empty, empty_values=empty_values)
		self.assertEqual(expected, rule.should_ignore(value))

	def test_validate(self):
		rule = DummyRule()
		self.assertIsNone(rule.validate('foo'))

	@raises(ValidationError)
	def test_validate_raises_validation_error(self):
		rule = DummyRule()
		rule.validate(False)

	def test_rule_is_callable(self):
		rule = DummyRule()
		self.assertIsNone(rule('foo'))

	@raises(ValidationError)
	def test_calling_rule_raises_validation_error(self):
		rule = DummyRule()
		rule(False)

	def test_sets_value_placeholder(self):
		rule = FailRule()
		error = None
		try:
			rule('foo', {'data':'case'})
		except ValidationError as e:
			error = e

		self.assertIsInstance(error, ValidationError)
		self.assertEqual('foo', error.placeholders.get('__value__'))

	def test_adds_data_set_to_placeholders(self):
		rule = FailRule()
		error = None
		try:
			rule('foo', {'data_item' : 'DATA'})
		except ValidationError as e:
			error = e

		self.assertIsInstance(error, ValidationError)
		self.assertEqual('DATA', error.placeholders.get('data_item'))

	@parameterized.expand([
			('str', True, 'abc'),
			('int', True, 5),
			('zero', True, 0),
			('false', True, False),
			('none', False, None),
			('empty str', False, ''),
		])
	def test_required(self, _, expected, value, message=None, placeholders=None, name=None):
		rule = Required(message=message, placeholders=placeholders, name=name)
		result = rule.check(value)
		self.assertEqual(expected, result)

	@parameterized.expand([
			(True, 20),
			(True, '20'),
			(True, '', dict(ignore_empty=True)),
			(False, 23.5),
			(False, '23i'),
			(False, {}),
		])
	def test_integer(self, expected, value, kwargs={}):
		rule = Integer(**kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 20, 30),
			(True, 20, 20),
			(True, '20', '30'),
			(True, '', 100, dict(ignore_empty=True)),
			(False, 23, 20),
			(False, '23', '20')
		])
	def test_max(self, expected, value, limit, kwargs={}):
		rule = Max(limit, **kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 20, 10),
			(True, 20, 20),
			(True, '20', '10'),
			(True, '', 100, dict(ignore_empty=True)),
			(False, 2, 20),
			(False, '2', '20')
		])
	def test_min(self, expected, value, limit, kwargs={}):
		rule = Min(limit, **kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 'foo', 10),
			(True, 'foo', 3),
			(True, '', 5, dict(ignore_empty=True)),
			(False, 'foobar', 3),
		])
	def test_maxlen(self, expected, value, limit, kwargs={}):
		rule = MaxLen(limit, **kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 'foo', 1),
			(True, 'foo', 3),
			(True, '', 5, dict(ignore_empty=True)),
			(False, 'foo', 5),
		])
	def test_minlen(self, expected, value, limit, kwargs={}):
		rule = MinLen(limit, **kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 'foo', 3),
			(True, '', 5, dict(ignore_empty=True)),
			(False, 'foo', 5),
			(False, 'foobar', 5),
		])
	def test_length(self, expected, value, limit, kwargs={}):
		rule = Length(limit, **kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, '^[a-zA-Z]+\d+$', 'abc123'),
			(True, '^[a-zA-Z]+\d+$', '', dict(ignore_empty=True)),
			(False, '^[a-zA-Z]+\d+$', 'abc123', dict(inverse_match=True)),
			(False, '^[a-zA-Z]+\d+$', 'abc'),
		])
	def test_regex(self, expected, regex, value, kwargs={}):
		rule = Regex(regex, **kwargs)
		result = rule.check(value)
		self.assertEqual(expected, result)

	@parameterized.expand([
			(False, 'abc'),
			(False, '127.0.0.1'),
			(False, 'http://127.0.0.1', ('https',)),
			(True, 'http://127.0.0.1'),
			(True, 'http://localhost:8080'),
			(True, '', None, True),
			(True, 'https://www.google.com/search?q=foo+bar&oq=foo+bar&aqs=chrome..69i57.229035j0j7&sourceid=chrome&ie=UTF-8'),
		])
	def test_url(self, expected, value, schemes=None, ignore_empty=None, kwargs={}):
		rule = Url(schemes=schemes, ignore_empty=ignore_empty, **kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 'mail_25@example.com'),
			(True, 'mail-25@example.co.ke'),
			(True, 'mail.$$@localhost'),
			(True, '123@127.0.0.1'),
			(True, '', dict(ignore_empty=True)),
			(False, '', dict(ignore_empty=False)),
			(False, '123@127.0.0'),
			(False, '327.0.0.1'),
			(False, 'mail\25@example.com'),
			(False, 'mail[25]@example.com'),
			(False, 'mail(25)@example.com'),
			(False, 'mail<div>25@example.com'),
		])
	def test_email(self, expected, value, kwargs={}):
		rule = Email(**kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, '127.0.0.1'),
			(True, '', dict(ignore_empty=True)),
			(False, '127.0.0'),
			(False, '327.0.0.1'),
		])
	def test_ipv4_address(self, expected, value, kwargs={}):
		rule = IPv4(**kwargs)
		self.assertEqual(expected, rule.check(value))


	@parameterized.expand([
			(True, 'fe80::bc57:92f9:8b9b:3c3c'),
			(True, None, dict(ignore_empty=True)),
			(False, '127.0.0.1'),
			(False, 'bc57:92f9:8b9b:3c3c'),
		])
	def test_ipv6_address(self, expected, value, kwargs={}):
		rule = IPv6(**kwargs)
		self.assertEqual(expected, rule.check(value))


	@parameterized.expand([
			(True, '127.0.0.1'),
			(True, 'fe80::bc57:92f9:8b9b:3c3c'),
			(False, 'bc57:92f9:8b9b:3c3c'),
			(True, '', dict(ignore_empty=True)),
			(False, '127.0.0'),
			(False, '327.0.0.1'),
		])
	def test_ip_address(self, expected, value, kwargs={}):
		rule = IP(**kwargs)
		self.assertEqual(expected, rule.check(value))

	@parameterized.expand([
			(True, 'foo-bar', 'foo-bar'),
			(True, 254, 254),
			(True, 254, '254', dict(as_str=True)),
			(True, 'abc', lambda : 'abc'),
			(True, DummyObject('abc'), DummyObject('abc')),
			(True, '', 'foo-bar', dict(ignore_empty=True)),
			(False, 'foo', 'foo-bar'),
			(False, 254, '254'),
			(False, 'abc', lambda : 'foo'),
			(False, DummyObject('foo'), DummyObject('abc')),
		])
	def test_equals(self, expected, value, other_value, kwargs={}):
		rule = Equals(other_value, **kwargs)
		self.assertEqual(expected, rule.check(value))

	def test_passes(self):
		condition = lambda value, data: value == 'foo'
		rule = Passes(condition)
		self.assertTrue(rule.check('foo'))
		self.assertFalse(rule.check('bar'))

	def test_passes_with_params(self):
		condition = lambda value, data, expected: value == expected
		rule = Passes(condition, args=('foo',))
		self.assertTrue(rule.check('foo'))
		self.assertFalse(rule.check('bar'))

	def test_fails(self):
		condition = lambda value, data: value == 'foo'
		rule = Fails(condition)
		self.assertTrue(rule.check('bar'))
		self.assertFalse(rule.check('foo'))

	def test_fails_with_params(self):
		condition = lambda value, data, expected: value == expected
		rule = Fails(condition, args=('foo',))
		self.assertTrue(rule.check('bar'))
		self.assertFalse(rule.check('foo'))

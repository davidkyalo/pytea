import unittest
from nose.tools import raises
from tea import uzi
from tea.collections import Stack
from tea.validation import ValidationError
from nose_parameterized import parameterized
from tea.validation.rules import (
	Rule, Required, Regex, Url, Email, Integer, IPv4, IPv6, IP,
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
			(True, EMPTY, True),
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
		self.assertTrue(rule.validate('foo'))
		self.assertFalse(rule.validate(False))
		self.assertIsInstance(rule.validate(False), ValidationError)

	def test_rule_is_callable(self):
		rule = DummyRule()
		self.assertTrue(rule('foo'))

	def test_sets_value_placeholder(self):
		rule = FailRule()
		result = rule.validate('foo', {'data':'case'})
		self.assertEqual('foo', result.placeholders.get('__value__'))

	def test_adds_data_set_to_placeholders(self):
		rule = FailRule()
		result = rule.validate('foo', {'data_item' : 'DATA'})
		self.assertEqual('DATA', result.placeholders.get('data_item'))

	@parameterized.expand([
			('str', True, 'abc'),
			('int', True, 5),
			('zero', True, 0),
			('false', True, False),
			('none', False, None),
			('empty str', False, ''),
		])
	def test_required(self, _, expected, value, message=None, placeholders=None, name=None):
		rule = Required(message, placeholders, name)
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


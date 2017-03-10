import unittest
from nose.tools import raises
from tea import uzi
from tea.collections import Stack
from tea.gap import ValidationError, validate, field
from nose_parameterized import parameterized
from tea.gap.rules import (
	Rule, Required, Regex, Url, Email, Integer, IPv4, IPv6, IP, Same,
	EMPTY, NOTHING, NOT_PROVIDED,
	EMPTY_VALUES, EMPTY_COLLECTIONS, EMPTY_VALUES_AND_COLLECTIONS)

class ValidationTest(unittest.TestCase):

	def test_with_rule_list(self):
		rules = [
			field('name', Required, display_name='First Name'),
			field('email', Required, Email(message=" \"{__name__}\" should be a valid email address. {__value__} given")),
			field('url', Required, Url),
			field('pass', Same('confirm_password'))
		]
		data = {
			'fname' : '',
			'email' : 'mail@example',
			'url' : 'example.com',
			'pass' : '123456',
			'confirm_password' : 'qwertea'
		}
		errors = validate(rules, data)
		# print('\n', 'url' in data, errors.messages)
		print('')
		print(errors.format("<li>{message}</li>"))


def dummy_ruleset():
	pass
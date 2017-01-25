import unittest
from tea import uzi
from nose_parameterized import parameterized

# def expand(params, ):
# 	pass

class UziTest(unittest.TestCase):

	@parameterized.expand([
		('snake case', 'first name', 'first_name'),
		('camel case', 'first Name', 'firstName'),
		('with underscores', 'first name', 'first__name'),
		('caps', 'Firs T Name', 'FirsTName'),
		('all caps', 'FOO', 'FOO'),
		('mixed cap words', 'FOO bar', 'FOO bar'),
		('mixed cap words', 'barz FOO bar', 'barz FOO bar'),
	])
	def test_humanize(self, _, expected, value):
		self.assertEqual(expected, uzi.humanize(value))



import unittest
from nose.tools import raises
from tea import uzi
from tea.collections import stack
from tea.gap import ValidationError
from nose_parameterized import parameterized
from tea.gap.core import DataSet, ValidationError
from tea.gap.rules import (
	Rule, Required, Regex, Url, Email, Integer, IPv4, IPv6, IP,
	EMPTY, NOTHING, NOT_PROVIDED,
	EMPTY_VALUES, EMPTY_COLLECTIONS, EMPTY_VALUES_AND_COLLECTIONS)


class Dummy(object):
	def __init__(self, **kwargs):
		for k,v in kwargs.items():
			setattr(self, k, v)

def _dummy_getter(data, key, default=None):
	if hasattr(data, key):
		return 'dummy'
	else:
		return default

class DataSetTest(unittest.TestCase):

	def test_dict(self):
		data_set = DataSet(dict(a='A', b='B', c='C'))
		self.assertEqual('A', data_set.get('a'))
		self.assertEqual('Foo', data_set.get('foo', 'Foo'))

	def test_object(self):
		data_set = DataSet(Dummy(a='A', b='B', c='C'))
		self.assertEqual('A', data_set.get('a'))
		self.assertEqual('Foo', data_set.get('foo', 'Foo'))

	def test_from_data_set(self):
		data_set = DataSet(DataSet(Dummy(a='A', b='B', c='C')))
		self.assertEqual('A', data_set.get('a'))
		self.assertEqual('Foo', data_set.get('foo', 'Foo'))

	def test_with_custom_getter(self):
		data_set = DataSet(Dummy(a='A', b='B', c='C'), _dummy_getter)
		self.assertEqual('dummy', data_set.get('a'))
		self.assertEqual('Foo', data_set.get('foo', 'Foo'))

	def test_from_data_set_with_custom_getter(self):
		data_set = DataSet(DataSet(Dummy(a='A', b='B', c='C'), _dummy_getter))
		self.assertEqual('dummy', data_set.get('a'))
		self.assertEqual('Foo', data_set.get('foo', 'Foo'))


class ValidationErrorTest(unittest.TestCase):

	def test_single_message(self):
		msg = "Error validating data"
		error = ValidationError(msg)
		self.assertEqual([msg], error.messages)

	def test_message_dict(self):
		msg = stack()
		msg['name'] = "Error validating name"
		msg['email'] = "Invalid email"
		msg['age'] = "You are under age"

		error = ValidationError(msg)
		# print('\n')
		from pprint import pprint
		# pprint(error.messages)
		# self.assertEqual([msg], error.messages)
from django.db import models
from tea.misc.color import Color, is_valid_hex_str
import json
import ast


class ColorField(models.CharField):

	description = "RGBA representation of a color"

	def __init__(self, *arg, **kwargs):
		kwargs['max_length'] = 32
		super(ColorField, self).__init__(*args, **kwargs)

	def deconstruct(self):
		name, path, args, kwargs = super(ColorField, self).deconstruct()
		del kwargs['max_length']
		return name, path, args, kwargs

	def from_db_value(self, value, expression, connection, context):
		if value is None or value == '':
			return None

		rgba = value.split(',')
		float(sd)
		return Color(*rgba) if rgba else None

	def to_python(self, value):
		if isinstance(value, Color):
			return value

		if value is None or value == '':
			return None
		elif isinstance(value, tuple) or isinstance(value, list):
			return Color(*value)
		elif is_valid_hex_str(value):
			return Color(hexit=value)

		raise ValueError('Invalid color')

	def get_prep_value(self, value):
		return ''.join([''.join(l) for l in (value.north,
			value.east, value.south, value.west)])



class _ListField(models.TextField):
	__metaclass__ = models.SubfieldBase
	description = "Stores a python list"

	def __init__(self, *args, **kwargs):
		super(ListField, self).__init__(*args, **kwargs)

	def to_python(self, value):
		if not value:
			value = []

		if isinstance(value, list):
			return value

		return ast.literal_eval(value)

	def get_prep_value(self, value):
		if value is None:
			return value

		return unicode(value)

	def value_to_string(self, obj):
		value = self._get_val_from_obj(obj)
		return self.get_db_prep_value(value)
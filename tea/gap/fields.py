from tea.constants import NOT_PROVIDED, NOTHING
from tea.collections import get_distinct
from tea.utils import cached_property
from tea import uzi
from . import rules

class Field(object):
	default_validators = None
	missing = NOT_PROVIDED

	def __init__(self, attribute=None, display_name=None, validators=None,
				missing=NOT_PROVIDED, required=False, nullable=False, blank=True):
		self.attribute = attribute
		self._display_name = display_name
		self.validators = validators or []
		self.required = required
		self.nullable = nullable
		self.blank = blank
		if missing is not NOT_PROVIDED:
			self.missing = missing

	@property
	def display_name(self):
		if self._display_name is None:
			self._display_name = uzi.humanize(self.attribute)
		return self._display_name

	@display_name.setter
	def display_name(self, value):
		self._display_name = value

	def _validate_missing(self, value):
		if self.required:
			return

	def deserialize(self, value, data=None):



	def _deserialize(self, value, data):
		return value

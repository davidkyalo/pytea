import warnings
from sqlalchemy.exc import SAWarning
from sqlalchemy.ext import declarative
from sqlalchemy.util import set_creation_order
from sqlalchemy import util as sa_util
from tea.decorators import locked_cached_property

_declared_attr = declarative.declared_attr


class declared_creation_order(object):
	"""docstring for declared_attr_creation_order_property"""
	def __init__(self, arg):
		super(declared_attr_creation_order_property, self).__init__()
		self.arg = arg


class declared_attr(_declared_attr):

	def __init__(self, *args, **kwargs):
		super(declared_attr, self).__init__(*args, **kwargs)
		sa_util.set_creation_order(self)

	def __get__(self, instance, cls):
		reg = cls.__dict__.get('_sa_declared_attr_reg', None)
		if reg is None:
			attr = self.fget(cls)
			attr._sa_attr_declaration = self
		elif self in reg:
			return reg[self]
		else:
			attr = self.fget(cls)
			if hasattr(attr, '_creation_order'):
				attr._creation_order = self._creation_order
				reg[self] = attr

		return attr


#patch
declarative.declared_attr = declared_attr

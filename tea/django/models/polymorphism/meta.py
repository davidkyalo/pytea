from .const import POLYMORPHISM_TYPES

class ModelPolymorphismBase(object):
	"""Base Polymorphic models meta"""
	type = POLYMORPHISM_TYPES.POLYMORPHIC


class SingleTable(ModelPolymorphismBase):
	"""Single Table Polymorphic models meta"""
	type = POLYMORPHISM_TYPES.SINGLE_TABLE


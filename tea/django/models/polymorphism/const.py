

class POLYMORPHISM_TYPES:
	class POLYMORPHIC:
		"""Represents any type polymorphism."""
		pass

	"""Polymorphism related contants"""
	class JOINED_TABLE(POLYMORPHIC):
		"""Represents joined table (Table Per Type) polymorphism."""
		pass

	class SINGLE_TABLE(POLYMORPHIC):
		"""Represents single table (Table Per Hierarchy) polymorphism entries."""
		pass
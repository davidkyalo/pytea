from enum import unique
import enum

class Enum(enum.Enum):
	@classmethod
	def all(cls):
		list(cls)


class IntEnum(enum.IntEnum):
	@classmethod
	def all(cls):
		list(cls)

try:
	from enum import auto

	class Flag(enum.Flag):
		@classmethod
		def all(cls):
			list(cls)

	class IntFlag(enum.IntFlag):
		@classmethod
		def all(cls):
			list(cls)
except Exception as e:
	pass

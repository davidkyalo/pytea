
class BadMethodCall(Exception):
	pass

class ArgumentError(Exception):
	pass

try:
	from tea.gap import ValidationError
except ImportError:
	from tea.utils import MessageBag
	class ValidationError(MessageBag, Exception):
		pass
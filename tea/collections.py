from .wrapper import wrap, val
from .misc import NOTHING

__all__ = [
	'Stack', 'stack', 'heap', 'Heap'
]

class Stack(dict):
	"""docstring for stack"""
	__keystack__ = None
	__default__ = None

	def __init__(self, items = None):
		super(Stack, self).__init__()
		self.__keystack__ = []
		if items:
			if isinstance(items, dict):
				items = items.items()

			for k, v in items:
				self[k] = v


	def set_default(self, default, update = False, kwargs = None):
		if kwargs is None:
			kwargs = {}
		self.__default__ = (default, update, kwargs)

	def has_default(self):
		return True if self.__default__ else False

	def get_default(self, _k = None, **_kwargs):
		if not self.__default__:
			return None

		default, update, kwargs = self.__default__

		kwargs.update(_kwargs)

		value = val(default, **kwargs)
		if _k is not None and update:
			self[_k] = value
		return value

	def default_replaces_missing(self):
		return True if self.__default__ and self.__default__[1] else False

	def _get_or_default(self, key, default=NOTHING, strict = True, **kwargs):
		if key in self.__keystack__:
			return super(Stack, self).__getitem__(key)
		elif default is not NOTHING:
			return val(default)
		elif self.has_default():
			return self.get_default(_k = key)
		elif not strict:
			return None

		raise KeyError("Key {0} not found in stack.".format(key))

	def define(self, name, extension, override=False):
		if not override and (name in self.__dict__ or hasattr(self.__class__, name)):
			raise AttributeError('Attribute {0} already exists in stack'.format(name))
		self.__dict__[name] = self._wrap_extension(extension)

	def _wrap_extension(self, extension):
		def wrapper(*args, **kwargs):
			return extension(self, *args, **kwargs)
		return wrapper

	def get(self, key, default = None):
		value = self._get_or_default(key, default = default, strict = False)
		return value

	def keys(self):
		return self.__keystack__

	def items(self):
		return [(key, self[key]) for key in self.__keystack__]

	def update(self, *stacks, **kwargs):
		stacks = stacks + (kwargs,)
		for st in stacks:
			for key, value in st.items():
				self[key] = value

	def __getitem__(self, key):
		return self._get_or_default(key)

	def __setitem__(self, key, value):
		if key not in self.__keystack__:
			self.__keystack__.append(key)
		return super(Stack, self).__setitem__(key, value)

	def __delitem__(self, key):
		self.__keystack__.remove(key)
		return super(Stack, self).__delitem__(key)

	def __getattr__(self, key):
		return self._get_or_default(key)

	def __setattr__(self, key, value):
		if hasattr(self.__class__, key):
			self.__dict__[key] = value
		else:
			self[key] = value

	def __delattr__(self, key):
		if key in self:
			del self[key]
		else:
			raise KeyError("No such key: " + key)


class Heap(dict):
	"""docstring for Heap"""
	def __init__(self, *args, **kwargs):
		super(Heap, self).__init__(*args, **kwargs)
		self.__dict__ = self


def stack(items=None):
	return Stack(items)

def heap(*args, **kwargs):
	return Heap(*args, **kwargs)
__all__ = [
	'stack', 'heap'
]

_stact_cls_attrs = ['__keystack__', '__default__']

class stack(dict):
	"""docstring for stack"""
	__keystack__ = None
	__default__ = None
	def __init__(self, keys = None, **items):
		self.__keystack__ = keys if keys else []

		super(stack, self).__init__(**items)

	def setdefault(self, func, update = True, args = None, kwargs = None):
		if args is None:
			args = ()
		if kwargs is None:
			kwargs = {}
		self.__default__ = (func, update, args, kwargs)

	def _get_or_default(self, key, default = None, strict = True):
		if key in self.__keystack__:
			return super(stack, self).__getitem__(key)

		if not self.__default__:
			if strict and default == None:
				raise KeyError("No such key: " + key)
				return
			else:
				return default

		func, update, args, kwargs = self.__default__
		value = func( *args, **kwargs)
		if update:
			self[key] = value

		return value



	def get(self, key, default = None):
		value = self._get_or_default(key, default = default, strict = False)
		return value

	def keys(self):
		return self.__keystack__

	def items(self):
		return [(key, self[key]) for key in self.__keystack__]

	def update(self, *stacks):
		for st in stacks:
			for key, value in st.items():
				self[key] = value

	def __getitem__(self, key):
		return self._get_or_default(key)

	def __setitem__(self, key, value):
		if key not in self.__keystack__:
			self.__keystack__.append(key)
		return super(stack, self).__setitem__(key, value)

	def __delitem__(self, key):
		self.__keystack__.remove(key)
		return super(stack, self).__delitem__(key)


	def __getattr__(self, key):
		return self._get_or_default(key)

	def __setattr__(self, key, value):
		if key in _stact_cls_attrs: # key == '__keystack__':
			self.__dict__[key] = value
		else:
			self[key] = value

	def __delattr__(self, key):
		if key in self:
			del self[key]
		else:
			raise KeyError("No such key: " + key)


class heap(dict):
	"""docstring for heap"""
	def __init__(self, *args, **kwargs):
		super(heap, self).__init__(*args, **kwargs)
		self.__dict__ = self
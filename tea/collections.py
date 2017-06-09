from .wrapper import wrap, val
from .misc import NOTHING
import collections
import warnings
import six
from abc import ABCMeta, abstractproperty

_namedtuple = collections.namedtuple

__all__ = [
	'stack', 'heap', 'Heap', 'un'
]

class __ALL_ITEMS__(object):
	pass

SOMETHING = object()

class stack(dict):
	"""docstring for stack"""
	ALL_ITEMS = __ALL_ITEMS__
	__keystack__ = None
	__default__ = None

	def __init__(self, *args, **kwargs):
		super(stack, self).__init__()
		self.__keystack__ = []
		args = args + (kwargs,)
		for arg in args:
			if isinstance(arg, dict):
				arg = arg.items()
			for k, v in arg:
				self[k] = v

	def setdefault(self, key=None, default=None, g=False, update=False, kwargs=None):
		if not g:
			if self._has_key(key):
				return self._super_getitem(key)
			self[key] = default
			return default
		else:
			self.set_global_default(default, update, kwargs)

	def set_global_default(self, default, update=False, kwargs=None):
		self.__default__ = (default, update, kwargs or {})

	def set_default(self, default, update = False, kwargs = None):
		warnings.warn("Method set_default() is depreciated. "\
				"Use setdefault() instead.", DeprecationWarning)
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

		if update:
			self[_k] = value

		return value

	def default_replaces_missing(self):
		return True if self.__default__ and self.__default__[1] else False

	def _has_key(self, key):
		return key in self.__keystack__

	def _super_getitem(self, key):
		return super(stack, self).__getitem__(key)

	def _get_or_default(self, key, default=NOTHING, strict = True, raises=KeyError, **kwargs):
		if self._has_key(key):
			return self._super_getitem(key)
		elif default is not NOTHING:
			return val(default)
		elif self.has_default():
			return self.get_default(_k = key)
		elif not strict:
			return None

		raise raises("Attribute/Key {0} not found in stack.".format(key))

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

	def pop(self, key, default=NOTHING):
		if default is NOTHING:
			value = super(stack, self).pop(key)
		else:
			value = super(stack, self).pop(key, default)
		if key in self.__keystack__:
			self.__keystack__.remove(key)
		return value

	def keys(self):
		return self.__keystack__

	def items(self):
		return [(key, self[key]) for key in self.__keystack__]

	def values(self):
		return [self[key] for key in self.__keystack__]

	def update(self, *stacks, **kwargs):
		stacks = stacks + (kwargs,)
		for st in stacks:
			for key, value in st.items():
				self[key] = value

	def copy(self):
		return self.__class__(self.items())

	def clear(self):
		super(stack, self).clear()
		self.__keystack__ = []

	def __contains__(self, key):
		return key in self.__keystack__

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
		return self._get_or_default(key, raises=AttributeError)

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


class Stack(stack):

	def __init__(self, *args, **kwargs):
		warnings.warn('Class Stack is depracated and will soon be removed. '\
						'Use stack instead.', DeprecationWarning)
		stack.__init__(self, *args, **kwargs)


# class DefaultStack(Stack):

# 	def set_default(self, default, update = False, kwargs = None):
# 		if kwargs is None:
# 			kwargs = {}
# 		self.__default__ = (default, update, kwargs)


class Heap(dict):
	"""docstring for Heap"""
	def __init__(self, *args, **kwargs):
		super(Heap, self).__init__(*args, **kwargs)
		self.__dict__ = self


class UniqueAppender(object):
	"""Appends items to a collection ensuring uniqueness.

	Additional appends() of the same object are ignored.  Membership is
	determined by identity (``is a``) not equality (``==``).
	"""

	def __init__(self, data=None, via=None):
		self.data = [] if data is None else data
		self._unique = {}
		if via:
			self._data_appender = getattr(data, via)
		elif hasattr(data, 'append'):
			self._data_appender = data.append
		elif hasattr(data, 'add'):
			self._data_appender = data.add

	def append(self, *items):
		for item in items:
			id_ = id(item)
			if id_ not in self._unique:
				self._data_appender(item)
				self._unique[id_] = True

	def __iter__(self):
		return iter(self.data)



# class NamedTupleABCMeta(ABCMeta):
# 	'''The metaclass for the abstract base class + mix-in for named tuples.'''
# 	def __new__(mcls, name, bases, namespace):
# 		fields = namespace.get('_fields')
# 		for base in bases:
# 			if fields is not None:
# 				break
# 			fields = getattr(base, '_fields', None)
# 		if not isinstance(fields, abstractproperty):
# 			basetuple = _namedtuple(name, fields)
# 			bases = (basetuple,) + bases
# 			namespace.pop('_fields', None)
# 			namespace.setdefault('__doc__', basetuple.__doc__)
# 			namespace.setdefault('__slots__', ())
# 		return ABCMeta.__new__(mcls, name, bases, namespace)


# class NamedTupleABC(metaclass=NamedTupleABCMeta):
# 	'''The abstract base class + mix-in for named tuples.'''
# 	_fields = abstractproperty()


# 	_namedtuple.abc = _NamedTupleABC
# #_NamedTupleABC.register(type(version_info))  # (and similar, in the future...)

# @wraps(_namedtuple)
# def namedtuple(*args, **kwargs):
# 	'''Named tuple factory with namedtuple.abc subclass registration.'''
# 	cls = _namedtuple(*args, **kwargs)
# 	_NamedTupleABC.register(cls)
# 	return cls

# collections.namedtuple = namedtuple





def heap(*args, **kwargs):
	return Heap(*args, **kwargs)


def get_distinct(seq):
	warnings.warn('function get_distinct() is deprecated. Use unique_list() instead.', DeprecationWarning)
	return unique_list(seq)

def unique_list(seq, hashfunc=None):
	seen = set()
	seen_add = seen.add
	if not hashfunc:
		return [x for x in seq
				if x not in seen
				and not seen_add(x)]
	else:
		return [x for x in seq
				if hashfunc(x) not in seen
				and not seen_add(hashfunc(x))]


def to_list(x, default=None):
	if x is None:
		return default
	if not isinstance(x, collections.Iterable) or isinstance(x, str):
		return [x]
	elif isinstance(x, list):
		return x
	else:
		return list(x)


def yielder(x, default=[], ignore=six.string_types):
	x = default if x is None else x
	if isinstance(x, collections.Iterable):
		if ignore and isinstance(x, ignore):
			yield x
		else:
			for v in x: yield v
	else:
		yield x
		

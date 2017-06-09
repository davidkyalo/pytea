from threading import RLock
import sys

NOTHING = object()


class class_only_method(classmethod):
	"""Creates a classmethod available only to the class. Raises AttributeError
	when called from an instance of the class.
	"""
	def __init__(self, func, name=None):
		super(class_only_method, self).__init__(func)
		self.__name__ = name or func.__name__

	def __get__(self, obj, cls):
		if obj is not None:
			raise AttributeError('Class method {}.{}() is available only to '\
				'the class, and not it\'s instances.'\
				.format(cls.__name__, self.__name__))
		return super(class_only_method, self).__get__(obj, cls)


class classproperty(classmethod):
	"""A decorator that converts a function into a lazy class property."""
	def __get__(self, obj, cls):
		func = super(classproperty, self).__get__(obj, cls)
		return func()

class_property = classproperty

class cached_class_property(class_property):
	"""A decorator that converts a function into a lazy class property."""
	def __init__(self, func, name=None, doc=None):
		super(cached_class_property, self).__init__(func)
		self.__name__ = name or func.__name__
		self.__module__ = func.__module__
		self.__doc__ = doc or func.__doc__
		self.lock = RLock()

	def __get__(self, obj, cls):
		with self.lock:
			rv = super(cached_class_property, self).__get__(obj, cls)
			setattr(cls, self.__name__, rv)
			return rv


class cached_property(property):
	"""A decorator that converts a function into a lazy property.  The
	function wrapped is called the first time to retrieve the result
	and then that calculated result is used the next time you access
	the value::

		class Foo(object):

			@cached_property
			def foo(self):
				# calculate something important here
				return 42

	The class has to have a `__dict__` in order for this property to
	work.
	"""

	# implementation detail: A subclass of python's builtin property
	# decorator, we override __get__ to check for a cached value. If one
	# choses to invoke __get__ by hand the property will still work as
	# expected because the lookup logic is replicated in __get__ for
	# manual invocation.

	def __init__(self, func, name=None, doc=None):
		self.__name__ = name or func.__name__
		self.__module__ = func.__module__
		self.__doc__ = doc or func.__doc__
		self.func = func

	def __set__(self, instance, value):
		instance.__dict__[self.__name__] = value

	def __get__(self, instance, type=None):
		if instance is None:
			return self
		value = instance.__dict__.get(self.__name__, NOTHING)
		if value is NOTHING:
			value = self.func(instance)
			instance.__dict__[self.__name__] = value
		return value


class locked_cached_property(property):
	"""A decorator that converts a function into a lazy property.  The
	function wrapped is called the first time to retrieve the result
	and then that calculated result is used the next time you access
	the value.  Works like the one in Werkzeug but has a lock for
	thread safety.
	"""

	def __init__(self, func, name=None, doc=None):
		self.__name__ = name or func.__name__
		self.__module__ = func.__module__
		self.__doc__ = doc or func.__doc__
		self.func = func
		self.lock = RLock()

	def __set__(self, instance, value):
		with self.lock:
			instance.__dict__[self.__name__] = value

	def __get__(self, instance, type=None):
		if instance is None:
			return self
		with self.lock:
			value = instance.__dict__.get(self.__name__, NOTHING)
			if value is NOTHING:
				value = self.func(instance)
				instance.__dict__[self.__name__] = value
			return value


def export(obj, module=None, name=None):
	module = sys.modules[module or obj.__module__]
	ol = getattr(module, '__all__', None)
	if ol is None:
		ol = []
		setattr(module, '__all__', ol)
	ol.append(name or obj.__name__)
	return obj


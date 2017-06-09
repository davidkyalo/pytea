import threading
from . import uzi
from uuid import uuid4
from warnings import warn

class DynamicProperty(object):
	"""docstring for ClassName"""

	def __init__(self, func, args=None, kwargs=None):
		raise Exception('DynamicProperty: Hey!!! Depreciated Error Consider '\
			'using decorators on tea.decorators.')
		self.__doc__ = getattr(func, '__doc__')
		self.func = func
		self.args = args or ()
		self.kwargs = kwargs or {}

	def __get__(self, obj, cls):
		if obj is None:
			return self
		return self.get_value(obj)

	def __set__(self, obj, value):
		raise AttributeError("{} {} in {} is read only."
				.format(self.__class__.__name__,
						self.func.__name__,
						obj.__class__.__name__)
			)

	def get_value(self, obj):
		return self.resolve(obj)

	def resolve(self, obj=None):
		return self.func(*self.args, **self.kwargs)

class CachedProperty(DynamicProperty):

	def __init__(self, func, args=None, kwargs=None, cache_attr=None, threaded=False):
		super(CachedProperty, self).__init__(func, args, kwargs)
		self.threaded = threaded
		self.cache_attr = cache_attr or _generate_attr_id(self, func)
		self.lock = threading.RLock() if self.threaded else None

	def get_value(self, obj):
		if obj is None:
			return self
		print('Getting:', self.cache_attr)
		obj_dict = obj.__dict__
		name = self.cache_attr
		if not self.threaded:
			return obj_dict.setdefault(name, self.resolve())
		else:
			with self.lock:
				try:
					# check if the value was computed before the lock was acquired
					return obj_dict[name]
				except KeyError:
					# if not, do the calculation and release the lock
					return obj_dict.setdefault(name, self.resolve())


class ThreadedCachedProperty(CachedProperty):
	"""docstring for ThreadedCachedProperty"""
	def __init__(self, func, args=None, kwargs=None, cache_attr=None):
		super(ThreadedCachedProperty, self).__init__(
						func, args=args, kwargs=kwargs,
						cache_attr=cache_attr, threaded=True
					)

def dynamic_property(*args, **kwargs):
	def wrapper(func):
		return DynamicProperty(func, args=args, kwargs=kwargs)
	return wrapper



def cached_property(*args, _cache_attr=None, **kwargs):
	def wrapper(func):
		return CachedProperty(func, args=args, kwargs=kwargs, cache_attr=_cache_attr)
	return wrapper


def threaded_cached_property(*args, _cache_attr=None, **kwargs):
	def wrapper(func):
		return ThreadedCachedProperty(func, args=args, kwargs=kwargs, cache_attr=_cache_attr)
	return wrapper

def _generate_attr_id(obj, func):
	cls_name = obj.__class__.__name__
	func_name = 'lambda' if func.__name__ == '<lambda>' else func.__name__
	uid = str(uuid4())
	return '_'+uzi.snake('{}_{}_{}'.format(cls_name, func_name, uid))
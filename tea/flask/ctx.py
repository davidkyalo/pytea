from flask import _app_ctx_stack, _request_ctx_stack
from . import exc, local
from threading import RLock

NOTHING = object()

class _AppContextPropertyContainer(object):
	"""Used as a container to cache an object properties in the app context."""

	def __init__(self, obj=None):
		self.__name__ = obj.__class__.__name__ if obj else None

	def set(self, name, value):
		self.__dict__[name] = value

	def get(self, name, default=None):
		return self.__dict__.get(name, default)

	def pop(self, name, default=NOTHING):
		if default is NOTHING:
			return self.__dict__.pop(name)
		else:
			return self.__dict__.pop(name, default)

	def setdefault(self, name, default=None):
		return self.__dict__.setdefault(name, default)

	def __contains__(self, item):
		return item in self.__dict__

	def __iter__(self):
		return iter(self.__dict__)

	def __repr__(self):
		return '<AppContextPropertyContainer for %r>' % self.__name__


class app_ctx_property(property):
	"""Decorator to creates a lazy property cached in the application context.
	The function wrapped is called the first time to retrieve the result which
	is stored in the current application context.
	The next time you access the property, the cached value in the current
	application context is returned. If the application context has changed, a
	new value is calculated and stored in the new context.
	"""
	def __init__(self, func, name=None, doc=None):
		self.__name__ = name or func.__name__
		self.__module__ = func.__module__
		self.__doc__ = doc or func.__doc__
		self.func = func
		self.lock = RLock()

	def get_name(self, inst):
		return '{}_{}__{}'.format(inst.__class__.__name__, id(inst), self.__name__)

	def _get_ctx(self, instance=None, silent=False):
		top = _app_ctx_stack.top
		if top is None and not silent:
			cls = None if instance is None else instance.__class__.__name__
			raise exc.AppContextError('The application context not pushed. '
				'The application context must be available to get/set '
				'property: {} of {}.'\
				.format(self.__name__, cls))
		return top

	def __set__(self, instance, value):
		with self.lock:
			ctx = self._get_ctx(instance)
			setattr(ctx, self.get_name(instance), value)
			return

	def __get__(self, instance, type=None):
		if instance is None:
			return self
		with self.lock:
			ctx = self._get_ctx(instance)
			name = self.get_name(instance)
			rv = getattr(ctx, name, NOTHING)
			if rv is NOTHING:
				rv = self.func(instance)
				setattr(ctx, name, rv)
				if not hasattr(instance, name):
					setattr(instance, name, self)

			return rv

	def __delete__(self, instance):
		if instance is None:
			return self
		with self.lock:
			ctx = self._get_ctx(silent=True)
			if ctx is not None:
				name = self.get_name(instance)
				if hasattr(ctx, name):
					delattr(ctx, name)
			return


@local.callable_local_proxy
def current_app_ctx():
	ctx = _app_ctx_stack.top
	if ctx is None:
		raise exc.AppContextError(
			'Error accessing current application context. '\
			'The application context not pushed.'
		)
	return ctx

@local.callable_local_proxy
def current_request_ctx():
	ctx = _request_ctx_stack.top
	if ctx is None:
		raise exc.RequestContextError(
			'Error accessing current request context. '\
			'The request context not pushed.'
		)
	return ctx


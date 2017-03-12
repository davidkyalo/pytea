from werkzeug.local import LocalProxy, Local
from functools import update_wrapper

class CallableLocalProxy(LocalProxy):
	"""A subclass of `werkzeug.local.LocalProxy` that returns the actual
	object when invoked.
	"""
	def __call__(self):
		return self._get_current_object()

CallableLocalProxy.__doc__ = LocalProxy.__doc__


def local_proxy(func, *args, **kwargs):
	"""A decorator that converts a function into a `werkzeug.local.LocalProxy`
	object. With the function as the local.
	"""
	def local():
		return func(*args, **kwargs)

	local.func = func
	local.args = args
	local.kwargs = kwargs
	return LocalProxy(update_wrapper(local, func))

def callable_local_proxy(func, *args, **kwargs):
	"""A decorator that converts a function into a `CallableLocalProxy`
	object with the function as the local.
	"""
	def local():
		return func(*args, **kwargs)

	local.func = func
	local.args = args
	local.kwargs = kwargs
	return CallableLocalProxy(update_wrapper(local, func))


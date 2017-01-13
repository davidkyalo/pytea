
class Closure(object):
	def __init__(self, item, args=None, kwargs=None):
		self.item = item
		self.args = args
		self.kwargs = kwargs

	def unwrap(self, *args, __force_ = False,**kwargs):
		if callable(self.item):
			args = self.gather_args(args)
			kwargs = self.gather_kwargs(kwargs)
			return self.item(*args, **kwargs)
		return self.item

	def __call__(self, *args, **kwargs):
		return self.unwrap(*args, **kwargs)

	def bind_to(self, item):
		return Closure(item, self.args, self.kwargs)

	def get_bound(self):
		return self.item

	def gather_args(self, args):
		if not self.args:
			return args
		old = list(self.args)
		for arg in args:
			old.remove(arg)
		return tuple(old) + tuple(args)

	def gather_kwargs(self, kwargs):
		if not self.kwargs:
			return kwargs
		new = dict(**self.kwargs)
		new.update(kwargs)
		return new

def wrap(item, *args, __args = None, __kwargs = None, **kwargs):
	"""Wrap the given item in a closure for it to be evaluated later."""
	if __args and not args:
		args = __args
	if __kwargs and not kwargs:
		kwargs = __kwargs

	return Closure(item, args, kwargs)

def is_wrapped(item):
	return isinstance(item, Closure)

def unwrap(item, *args, **kwargs):
	if not is_wrapped(item):
		error = 'Cannot unwrap object  {0}. Instance of {1} expected.'
		raise ValueError(error.format(item, Closure))

	recursive = kwargs.pop('_recursive', False)
	value = item.unwrap(*args, **kwargs)

	if recursive and is_wrapped(value):
		kwargs['_recursive'] = True
		return unwrap(value, *args, **kwargs)
	else:
		return value

def val(item, *args, **kwargs):
	return unwrap(item, *args, **kwargs) if is_wrapped(item) else item

__all__ = [ 'Closure', 'wrap', 'is_wrapped', 'unwrap', 'val' ]
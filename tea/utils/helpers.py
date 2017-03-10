
from copy import copy

def data_get(obj, key, default=None):
	if key is None:
		return obj

	target = copy(obj)
	key = list(key) if not isinstance(key, str) else key.split('.')

	for segment in key:
		if ismapping(target):
			if segment not in target:
				return default
			target = target[segment]
		else:
			if not hasattr(target, segment):
				return default
			target = getattr(target, segment)
	return target


def isiterable(obj, *exceptions, exceptstr = True):
	if not hasattr(obj, '__iter__'):
		return False

	if not exceptions and exceptstr:
		exceptions = (str,)

	return not isinstance(obj, exceptions) if exceptions else True


def ismapping(obj, *exceptions, exceptstr=True):
	if not hasattr(obj, '__getitem__'):
		return False

	if not exceptions and exceptstr:
		exceptions = (str,)

	return not isinstance(obj, exceptions) if exceptions else True
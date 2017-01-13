from tea.collections import stack
from django.utils import timezone
from django.db.models import DateTimeField, options

# class EMPTY:
# 	pass

# class NOTHING:
# 	pass

# class NOT_PROVIDED:
# 	pass

# class ANYTHING:
# 	pass

META_OPTIONS = stack()


# def model_timestamp_field(*args, **kwargs):
# 	if 'default' not in kwargs:
# 		kwargs['default'] = timezone.now
# 	if 'editable' not in kwargs:
# 		kwargs['editable'] = False
# 	return DateTimeField(*args, **kwargs)


def meta_options(*args, **kwargs):
	if not args and not kwargs:
		return META_OPTIONS

	options.DEFAULT_NAMES = options.DEFAULT_NAMES + args + tuple(kwargs.keys())

	for key, value in kwargs.items():
		if not isinstance(value, tuple):
			value = ( value, True )

		l = len(value)
		if l < 1:
			value = (None, True)
		elif l == 1:
			value = value + (True,)

		META_OPTIONS[key] = value

	return META_OPTIONS


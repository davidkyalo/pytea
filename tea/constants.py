from os import path
import re


class NOTHING:
	pass

"""
def hr(*args, nl = True):
	if args:
		print(*args)
	print('-'*139)
	if nl:
		print('')

def _fullname(cls):
	return cls.__module__ + '.' + cls.__qualname__

def __uris(*parts):
	parts = list(parts)


	# for p in parts:

def get_uri(cls, default=None):
	if not isinstance(cls, CONSTANT_BASE):
		return default
	else:
		return cls.get_uri(default)



class CONSTANT_BASE(type):

	def __new__(mcls, name, bases, namespace):
		# namespace.setdefault('__abstract__', False)
		# namespace['__base_uri__'] = None
		# namespace['__uri__'] = None
		cls = super(CONSTANT_BASE, mcls).__new__(mcls, name, bases, namespace)
		# cls.create_uri()
		return cls

	def __eq__(cls, other):
		eq = cls.equals(other)
		tab = '   '
		sp = ' '
		print(tab, 'Comparing :', _fullname(cls), 'Bases :', cls.__bases__)
		print(tab, 'With :', _fullname(other), 'Bases :', other.__bases__)
		hr(nl=False)
		hr(sp, 'Result :', eq)
		hr(nl=False)
		# hr('    Comparing', cls.__name__, 'with', other.__name__, 'Bases', cls.__bases__, 'Result', eq)
		return eq

	def __ne__(cls, other):
		return not cls.__eq__(other)

	def __hash__(cls):
		# if self.value is not None:
		return cls.value

	def equals(cls, other):
		if cls is other:
			return True
		if not isinstance(other, CONSTANT_BASE):
			return False

		elif other in cls.__bases__:
			return True
		else:
			return False

	def get_uri(cls, default=None):
		if cls.__uri__ is None:
			return default
		else:
			return cls.__uri__

	def create_uri(cls):
		if cls.__abstract__ or cls.__uri__:
			return

		uris = []
		for base in cls.__bases__:
			uri = get_uri(base)
			if uri is not None:
				uris.append('('+re.escape(uri.rstrip())+')')
		pattern = '|'.join(uris)

		cls.__uri__ = pattern


class CONSTANT(metaclass=CONSTANT_BASE):
	pass

"""
# class POLYMORPHISM:
# 	"""Polymorphism related contants"""

# 	class POLYMORPHIC(CONSTANT):
# 		"""Represents any type polymorphism."""
# 		pass

# 	class JOINED_TABLE(POLYMORPHIC):
# 		"""Represents joined table (Table Per Type) polymorphism."""
# 		pass

# 	class SINGLE_TABLE(POLYMORPHIC):
# 		"""Represents single table (Table Per Hierarchy) polymorphism."""
# 		pass



"""

hr()

from . import uzi

# value = POLYMORPHISM.JOINED_TABLE
# hr('Value', value.__qualname__)
# print('>> Is', POLYMORPHISM.JOINED_TABLE)
# value == POLYMORPHISM.JOINED_TABLE
# print('>> Is', POLYMORPHISM.POLYMORPHIC)
# value == POLYMORPHISM.POLYMORPHIC
# print('>> Is', POLYMORPHISM.SINGLE_TABLE)
# value == POLYMORPHISM.SINGLE_TABLE
pt =r'^((ab)|(aa)|(cca)|(ac))()'
hr('Pattern :', pt)
txts = ['ace', 'base', 'case', 'ccab(n)']
for t in txts:
	m = re.match(pt, t)
	if m:
		m = m.group(0)
	hr('Matched', '"'+t+'"', '>>', m)

xx = str('value')
hr('Compare Strings', (xx is 'value'))


exit()
"""
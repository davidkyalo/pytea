from tea import uzi, disk
from tea.collections import Stack
from tea.misc import NOTHING
import json

try:
	import yaml
except:
	yaml = None



class StaticMeta(type):
	def __init__(cls, name, bases, nmspc):
		super(StaticMeta, cls).__init__(name, bases, nmspc)
		cls.boot()

	def __getitem__(cls, key):
		return getattr(cls, key)

	def __setitem__(cls, key, value):
		setattr(cls, key, value)

	def boot(cls):
		print('\n\n', 'Meta Class BOOT on {0}'.format(cls.__name__), '\n\n')


class Static(metaclass=StaticMeta):

	@classmethod
	def boot(cls):
		pass

	@classmethod
	def get(cls, key, default = None):
		return getattr(cls, key, default)

	@classmethod
	def set(cls, key, value):
		setattr(cls, key, value)


class ConfigMeta(type):
	def __new__(mcl, name, bases, namespace):
		if not namespace.get('__alias__', None):
			namespace['__alias__'] = name

		if not namespace.get('__abstract__', False):
			namespace['__abstract__'] = False

		return super(ConfigMeta, mcl).__new__(mcl, name, bases, namespace)



class Repository(Stack):
	__registry__ = None
	__booted__ = None

	def __init__(self, *args, **kwargs):
		super(Repository, self).__init__(*args, **kwargs)
		self.__booted__ = False
		self.__registry__ = []

	def add(self, cls, *args, **kwargs):
		if not cls.__abstract__:
			self[cls.__alias__] = cls(*args, **kwargs)
			self.__registry__.append(cls.__alias__)
			self[cls.__alias__].__container__ = self
			self[cls.__alias__].__repository__ = self

			if self.booted():
				self[cls.__alias__].boot()

	# def register(self, alias, *args, **kwargs):
	# 	self.__registry__.append(cls.__alias__)
	# 	self[cls.__alias__].__container__ = self
	# 	self[cls.__alias__].__repository__ = self

	# 	if self.booted():
	# 		self[cls.__alias__].boot()

	def boot(self):
		if self.booted():
			return

		for alias in self.__registry__:
			self[alias].boot()

		self.__booted__ = True

	def booted(self):
		return self.__booted__


class Config(object, metaclass = ConfigMeta):

	__abstract__ = True
	__container__ = None
	__repository__ = None

	def boot(self):
		pass

	def mergewithfiles(self):
		pass

	def merge(self, *args, **kwargs):
		for arg in args:
			self.__dict__.update(arg)

		self.__dict__.update(kwargs)

	# def nest(self, config, _as = None, *args, **kwargs):
	# 	_as = _as or config.__alias__
	# 	self[_as] = config(*args, **kwargs)
	# 	self[_as].__container__ = self
	# 	self[_as].__repository__ = self._repository
	# 	if self._repository.booted():
	# 		self[_as].boot()


	def loadfromfile(self, path, loader = None):
		file = disk.File(path = path)

		if not loader:
			loader = self.load_yaml if file.type.lower() == 'yaml' else self.load_json

		if file.exists:
			return loader(file.content)
		else:
			return {}

	def load_json(self, content):
		return json.loads(content)

	def load_yaml(self, content):
		if not yaml:
			raise ImportError('yaml module not installed')

		return yaml.load(content)

	@property
	def _container(self):
		return self.__container__

	@property
	def _repository(self):
		return self.__repository__


	def get(self, key, default = None):
		return getattr(self, key, default)

	def set(self, key, value):
		setattr(self, key, value)
		return self

	def __getitem__(self, key):
		return getattr(self, key)

	def __setitem__(self, key, value):
		setattr(self, key, value)

	def __getattr__(self, key):
		inverse = key.upper() if key.islower() else key.lower()
		if hasattr(self, inverse):
			return getattr(self, inverse)
		else:
			KeyError("Key {0} not found in {1}".format(key, self.__class__.__name__))
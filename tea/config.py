from tea import uzi, disk
from tea.collections import Stack
from tea.misc import NOTHING
import json

try:
	import yaml
except:
	yaml = None

def _is_config_key(key):
	return not str(key).startswith('_') and not str(key).endswith('_')

def _is_default_key(key):
	return str(key) == '__default__'

def _to_dict(value):
	return value.to_dict() if isinstance(value, StaticMeta) else value

def _get_class_attrs(cls):
	attrs = {}
	for base in reversed(cls.__bases__):
		attrs.update(_get_class_attrs(base))

	for k,v in cls.__dict__.items():
		if _is_config_key(k) and not isinstance(v, classmethod):
			attrs[k] = v
	return attrs


class StaticMeta(type):
	def __new__(mcls, name, bases, body):
		has_default = '__default__' in body
		body['__keys__'] = []
		for k,v in body.items():
			if _is_config_key(k) and not isinstance(v, classmethod):
				body['__keys__'].append(k)

		for base in bases:
			if not isinstance(base, StaticMeta):
				for k,v in _get_class_attrs(base).items():
					if k not in body['__keys__']:
						body[k] = v
						body['__keys__'].append(k)
			else:
				if not has_default:
					default = base.get_default(NOTHING)
					if default is not NOTHING:
						body['__default__'] = default
						has_default = True

				for key in base.__keys__:
					if key not in body['__keys__']:
						body[key] = base.get(key)
						body['__keys__'].append(key)

		cls = super(StaticMeta, mcls).__new__(mcls, name, bases, body)
		return cls

	def __init__(cls, name, bases, body):
		super(StaticMeta, cls).__init__(name, bases, body)
		cls.boot()

	def __getitem__(cls, key):
		return getattr(cls, key)

	def __setitem__(cls, key, value):
		setattr(cls, key, value)

	def boot(cls):
		pass

	def get(cls, key=None, default=NOTHING):
		if key is None:
			if not cls.has_default():
				raise KeyError('None cannot be used a key coz class {0} has no default value.'.format(cls))
			return cls.get_default()

		if default is NOTHING:
			default = cls.get_default(default)
		return getattr(cls, key) if default is NOTHING else getattr(cls, key, default)

	def get_default(cls, otherwise=NOTHING):
		return getattr(cls, '__default__', otherwise)

	def has_default(cls):
		return hasattr(cls, '__default__')

	def set(cls, key, value):
		setattr(cls, key, value)

	def all(self):
		return self.to_dict()

	def to_dict(cls, *keys, exclude=False):
		results = Stack()
		if keys and not exclude:
			for key in keys:
				results[key] = _to_dict(getattr(cls, key))
			return results
		else:
			exclude = len(keys) > 0 and exclude
			for key in cls.__keys__:
				if not exclude or key not in keys:
					results[key] = _to_dict(getattr(cls, key))
			return results



class Static(metaclass=StaticMeta):
	pass


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
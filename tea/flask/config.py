from flask.config import Config as BaseConfig, ConfigAttribute
from collections import namedtuple

_config_src_fields = ['src', 'method', 'args', 'kwargs']

_config_src_methods = ('envvar', 'json', 'mapping', 'object', 'pyfile')

_ConfigSrc = namedtuple('_ConfigSrc', _config_src_fields)


class ConfigSrc(_ConfigSrc):
	"""The config source class."""
	__slots__ = ()

	def __init__(self, src, method='object', args=None, kwargs=None):
		args = args or ()
		kwargs = kwargs or {}
		_ConfigStrategy.__init__(self, src, method, args, kwargs)


class Config(BaseConfig):

	def from_src(self, *sources):
		"""Updates the config from given configuration source(s)."""
		for src in sources:
			if isinstance(src, (list, tuple)) and not isinstance(src, ConfigSrc):
				src = ConfigSrc(*src)

			method = args = kwargs = None
			if isinstance(src, ConfigSrc):
				src, method, args, kwargs = src

			method = method or 'object'
			if method not in _config_src_methods:
				raise ValueError('Error updating config. Invalid config '\
						'source update method. Allowed : {}. {} was given.'\
						.format(_config_src_methods, method))

			method = getattr(self, 'from_%s' % method)
			method(src, *(args or ()), **(kwargs or {}))
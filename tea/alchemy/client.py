from sqlservice import SQLClient
from sqlalchemy import orm
from .query import Query
from .session import Session
from tea.collections import stack
from tea.constants import NOTHING
from .model import declarative_base
from .utils import _set_app_state, _get_app_state
from flask import current_app, _app_ctx_stack
import warnings
from tea import uzi
from threading import Lock
from sqlalchemy.engine.url import make_url
from tea.flask import current_app_ctx, app_ctx_property
import sqlalchemy_utils as sa_utils
import copy

try:
	from sqlalchemy_mptt import mptt_sessionmaker
	mptt_session = True
except ImportError as e:
	mptt_session = False


_confkey = 'SQLALCHEMY'


class _EngineConnector(object):

	def __init__(self, client, app, bind=None):
		self._client = client
		self._app = app
		self._engine = None
		self._connected_for = None
		self._bind = bind
		self._lock = Lock()

	@property
	def _config(self):
		return self._app.config[_confkey]

	def get_uri(self):
		if self._bind is None:
			return self._config['DATABASE_URI']
		binds = self._config.get('BINDS') or ()
		assert self._bind in binds, \
			'Bind %r is not specified.  Set it in the SQLALCHEMY["BINDS"] ' \
			'configuration variable' % self._bind
		return binds[self._bind]

	def get_engine(self):
		with self._lock:
			uri = self.get_uri()
			echo = self._config['ECHO']
			if (uri, echo) == self._connected_for:
				return self._engine

			options = self._client.make_engine_options(self._config)
			rv = self._engine = self._client.create_engine(uri, options)
			self._connected_for = (uri, echo)
			return rv




class Client(SQLClient):
	proxy_registry = None
	proxies = None

	default_config = {
		'DATABASE_URI': 'sqlite:///:memory:',
		'BINDS': {},
		'ECHO': False,
		'ECHO_POOL': False,
		'ENCODING': 'utf8',
		'CONVERT_UNICODE': None,
		'ISOLATION_LEVEL': None,
		'POOL_SIZE': None,
		'POOL_TIMEOUT': None,
		'POOL_RECYCLE': None,
		'MAX_OVERFLOW': None,
		'AUTOCOMMIT': False,
		'AUTOFLUSH': True,
		'EXPIRE_ON_COMMIT': True,
		'COMMIT_ON_TEARDOWN' : False,
	}

	def __init__(self, app=None, model_class=None, query_class=Query,
				 session_class=Session,  session_options=None):
		self.app = None
		self.model_class = model_class or declarative_base()
		self.query_class = query_class
		self.session_class = session_class
		self._engine_lock = Lock()

		if session_options is None:
			session_options = {}

		self.session = self.create_scoped_session(**session_options)

		self.proxy_registry = stack()
		self.proxies = stack()

		if app is not None:
			self.set_app(app)

	@property
	def Model(self):
		return self.model_class

	@property
	def engine(self):
		return self.get_engine()

	def database_exists(self):
		return sa_utils.database_exists(self.engine.url)

	def create_database(self, create_tables=True, encoding='utf8', template=None):
		if not self.database_exists():
			sa_utils.create_database(self.engine.url, encoding, template)
			if create_tables:
				self.create_all()

	def drop_database(self, drop_tables=False):
		if self.database_exists():
			if drop_tables:
				self.drop_all()
			sa_utils.drop_database(self.engine.url)

	def make_engine_connector(self, app=None, bind=None):
		"""Creates the connector for a given state and bind."""
		return _EngineConnector(self, self.get_app(app), bind)

	def get_engine(self, app=None, bind=None):
		"""Returns a specific engine."""
		app = self.get_app(app)
		state = _get_app_state(app)

		with self._engine_lock:
			connector = state.connectors.get(bind)

			if connector is None:
				connector = self.make_engine_connector(app, bind)
				state.connectors[bind] = connector

			return connector.get_engine()

	def get_app(self, reference_app=None):
		"""Helper method that implements the logic to look up an
		application."""

		if reference_app is not None:
			return reference_app

		if current_app:
			return current_app

		if self.app is not None:
			return self.app

		raise RuntimeError(
			'Application not registered on db instance and no application'\
			'bound to current context'
		)

	def get_config(self, app=None):
		app = self.get_app(app)
		return app.config[_confkey]

	def set_app(self, app):
		self.app = app
		self.init_app(app)

	def init_app(self, app):
		"""This callback can be used to initialize an application for the
		use with this database setup.  Never use a database in the context
		of an application not initialized that way or connections will
		leak.
		"""
		if _confkey not in app.config:
			warnings.warn(
				'DATABASE config not set. Defaulting to {}'.format(self.default_config)
			)
			app.config[_confkey] = {}
		else:
			app.config[_confkey] = self.make_config(app.config[_confkey])

		_set_app_state(self, app)

		@app.teardown_appcontext
		def shutdown_session(response_or_exc):
			if self.get_config(app).get('COMMIT_ON_TEARDOWN'):
				if response_or_exc is None:
					self.commit()

			self.remove()
			return response_or_exc

	def make_config(self, config):
		rv = copy.deepcopy(self.default_config)
		rv.update(dict(config))
		# for key, value in dict(config).items():
		# 	rv[key] = value
		return rv


	def make_engine_options(self, config):
		"""Return engine options from :attr:`config` for use in
		``sqlalchemy.create_engine``.
		"""
		return self._make_options(config, (
			('ECHO', 'echo'),
			('ECHO_POOL', 'echo_pool'),
			('ENCODING', 'encoding'),
			('CONVERT_UNICODE', 'convert_unicode'),
			('ISOLATION_LEVEL', 'isolation_level'),
			('POOL_SIZE', 'pool_size'),
			('POOL_TIMEOUT', 'pool_timeout'),
			('POOL_RECYCLE', 'pool_recycle'),
			('MAX_OVERFLOW', 'max_overflow')
		))

	def make_session_options(self, config, extra_options=None):
		"""Return session options from :attr:`config` for use in
		``sqlalchemy.orm.sessionmaker``.
		"""
		options = self._make_options(config, (
			('AUTOCOMMIT', 'autocommit'),
			('AUTOFLUSH', 'autoflush'),
			('EXPIRE_ON_COMMIT', 'expire_on_commit')
		))

		if extra_options:
			options.update(extra_options)

		return options

	def _make_options(self, config, key_mapping):
		"""Return mapped :attr:`config` options using `key_mapping` which is a
		tuple having the form ``((<config_key>, <sqlalchemy_key>), ...)``.
		Where ``<sqlalchemy_key>`` is the corresponding option keyword for a
		SQLAlchemy function.
		"""
		return {opt_key: config[cfg_key]
				for cfg_key, opt_key in key_mapping
				if config.get(cfg_key) is not None}


	def get_model(self, name, default=NOTHING):
		model = self.models.get(name, default)
		if model is not NOTHING:
			return model
		raise KeyError('Invalid model name "{}"'.format(name))


	def create_session(self, **options):
		session_class = options.pop('session_class', self.session_class)
		options.setdefault('query_cls', self.query_class)
		factory = orm.sessionmaker(class_=session_class, db=self, **options)
		return mptt_sessionmaker(factory) if mptt_session else factory

	def create_scoped_session(self, **options):
		scopefunc = options.pop('scopefunc', _app_ctx_stack.__ident_func__)
		factory = self.create_session(**options)
		return orm.scoped_session(factory, scopefunc=scopefunc)

	def add_proxy(self, resolver, name=None, singleton=False):
		if name is None:
			name = resolver.__name__
		if hasattr(self, name) or self.has_proxy(name):
			raise KeyError(
					'Error registering proxy "{}". '\
					'Conflicting proxy name.'.format(name))
		self.proxy_registry[name] = (resolver, singleton)

	def proxy(self, name=None, singleton=False):
		def decorator(resolver):
			self.add_proxy(resolver, name=name, singleton=singleton)
			return resolver
		return decorator

	def has_proxy(self, name, resolved=False):
		return name in self.proxy_registry

	@app_ctx_property
	def resolved_proxies(self):
		return {}

	def make_proxy(self, name):
		if name in self.resolved_proxies:
			return self.resolved_proxies[name]
		return self.resolve_proxy(name)

	def resolve_proxy(self, name):
		if name not in self.proxy_registry:
			raise KeyError('Proxy "{}" does not exist.'.format(name))

		resolver, singleton = self.proxy_registry[name]
		instance = resolver(self)
		if singleton:
			self.resolved_proxies[name] = instance
		return instance

	def __getattr__(self, key):
		if self.has_proxy(key):
			return self.make_proxy(key)

		model = self.get_model(key, None)
		if model is not None:
			return self.query(model)

		raise AttributeError('The attribute "{0}" is not an attribute of '
							 '{1} nor is it a valid proxy name or model class name in the '
							 'declarative model class registry. '
							 'Valid proxies are: {2}. '
							 'While Valid model names are: {3}.'
							 .format(key,
									 self.__class__.__name__,
									 ', '.join(self.proxy_registry.keys()),
									 ', '.join(self.models)
									)
							 )



